"""
Outreach activity logger — persists every call/SMS/email attempt to Databricks
and syncs delivery statuses from Twilio.
"""
import logging
from datetime import datetime, timezone

from ..config import settings
from ..db import execute_write, query, table_exists

logger = logging.getLogger("outreach_logger")

_TABLE = f"{settings.silver}.outreach_activity_log"
_table_ready = False


def _ensure_table():
    """Create the outreach log table if it doesn't exist (lazy, once per process)."""
    global _table_ready
    if _table_ready:
        return
    if table_exists(_TABLE):
        _table_ready = True
        return
    try:
        execute_write(f"""
            CREATE TABLE IF NOT EXISTS {_TABLE} (
                id              BIGINT GENERATED ALWAYS AS IDENTITY,
                created_at      TIMESTAMP,
                member_name     STRING,
                channel         STRING,
                contact_used    STRING,
                measure         STRING,
                measure_code    STRING,
                campaign_name   STRING,
                status          STRING,
                provider_sid    STRING,
                error_detail    STRING,
                script_body     STRING,
                updated_at      TIMESTAMP,
                member_selection STRING,
                interaction_log  STRING
            )
        """)
        logger.info("Created outreach log table: %s", _TABLE)
        _table_ready = True
    except Exception as e:
        logger.error("Failed to create outreach log table: %s", e)


def log_outreach(
    channel: str,
    member_name: str,
    contact_used: str,
    measure: str = "",
    measure_code: str = "",
    campaign_name: str = "",
    status: str = "",
    provider_sid: str = "",
    error_detail: str = "",
    script_body: str = "",
) -> None:
    """Insert one outreach activity row."""
    _ensure_table()
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        # Escape single quotes in text fields
        def esc(s: str) -> str:
            return (s or "").replace("'", "''")

        execute_write(f"""
            INSERT INTO {_TABLE}
                (created_at, member_name, channel, contact_used, measure,
                 measure_code, campaign_name, status, provider_sid,
                 error_detail, script_body, updated_at)
            VALUES
                ('{now}', '{esc(member_name)}', '{esc(channel)}', '{esc(contact_used)}',
                 '{esc(measure)}', '{esc(measure_code)}', '{esc(campaign_name)}',
                 '{esc(status)}', '{esc(provider_sid)}', '{esc(error_detail)}',
                 '{esc(script_body)}', '{now}')
        """)
        logger.info("Logged %s outreach to %s [%s] → %s", channel, member_name, status, provider_sid)
    except Exception as e:
        logger.error("Failed to log outreach: %s", e)


def update_outreach_by_sid(call_sid: str, status: str, detail: str = "",
                           member_selection: str = "") -> None:
    """Update an outreach log row by Twilio call SID.
    Appends detail to interaction_log (audit trail).
    member_selection stores the final choice (slot, AI outcome, etc.)."""
    _ensure_table()
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        detail_esc = (detail or "").replace("'", "''")
        status_esc = (status or "").replace("'", "''")
        selection_esc = (member_selection or "").replace("'", "''")
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        # Append new detail with timestamp to interaction_log trail
        append_entry = f"[{timestamp}] {status_esc}: {detail_esc}" if detail_esc else f"[{timestamp}] {status_esc}"

        # Build SET clauses
        set_parts = [
            f"status = '{status_esc}'",
            f"""interaction_log = CASE
                    WHEN interaction_log IS NULL OR interaction_log = '' THEN '{append_entry}'
                    ELSE interaction_log || ' | ' || '{append_entry}'
                END""",
            f"updated_at = '{now}'",
        ]
        if selection_esc:
            set_parts.append(f"member_selection = '{selection_esc}'")

        sql = f"""
            UPDATE {_TABLE}
            SET {', '.join(set_parts)}
            WHERE provider_sid = '{call_sid}'
        """
        execute_write(sql)
        logger.info("Updated outreach SID %s → status=%s detail=%s", call_sid, status, detail)
    except Exception as e:
        logger.error("Failed to update outreach by SID %s: %s", call_sid, e)


def fetch_twilio_status(sid: str, channel: str) -> str | None:
    """Fetch current delivery status from Twilio for a call or SMS SID."""
    try:
        from twilio.rest import Client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        if channel == "Call":
            resource = client.calls(sid).fetch()
        else:
            resource = client.messages(sid).fetch()
        return resource.status
    except Exception as e:
        logger.error("Twilio status fetch failed for SID %s: %s", sid, e)
        return None


def sync_pending_statuses() -> dict:
    """
    Query rows with transient statuses and refresh from Twilio API.
    Returns summary of what was synced.
    """
    _ensure_table()
    transient = ("initiated", "queued", "ringing", "in-progress", "sent", "sending", "accepted")
    placeholders = ", ".join(f"'{s}'" for s in transient)
    try:
        rows = query(f"""
            SELECT id, provider_sid, channel, status
            FROM {_TABLE}
            WHERE status IN ({placeholders})
              AND provider_sid IS NOT NULL
              AND provider_sid != ''
            ORDER BY created_at DESC
            LIMIT 100
        """)
    except Exception as e:
        logger.error("Failed to query pending statuses: %s", e)
        return {"synced": 0, "updated": 0, "results": []}

    updated = 0
    results = []
    for row in rows:
        sid = row["provider_sid"]
        ch = row["channel"]
        new_status = fetch_twilio_status(sid, ch)
        if new_status and new_status != row["status"]:
            try:
                now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                execute_write(f"""
                    UPDATE {_TABLE}
                    SET status = '{new_status}', updated_at = '{now}'
                    WHERE id = {row['id']}
                """)
                updated += 1
                results.append({"id": row["id"], "sid": sid, "old": row["status"], "new": new_status})
            except Exception as e:
                logger.error("Failed to update status for row %s: %s", row["id"], e)
        else:
            results.append({"id": row["id"], "sid": sid, "old": row["status"], "new": new_status or row["status"]})

    return {"synced": len(rows), "updated": updated, "results": results}


def get_outreach_logs(
    limit: int = 50,
    channel: str | None = None,
    status: str | None = None,
) -> list[dict]:
    """Read outreach log rows with optional filters."""
    _ensure_table()
    where = "1=1"
    if channel and channel != "all":
        where += f" AND channel = '{channel}'"
    if status and status != "all":
        where += f" AND status = '{status}'"
    try:
        return query(f"""
            SELECT id, created_at, member_name, channel, contact_used,
                   measure, measure_code, campaign_name, status,
                   provider_sid, error_detail, script_body, updated_at,
                   member_selection, interaction_log
            FROM {_TABLE}
            WHERE {where}
            ORDER BY created_at DESC
            LIMIT {limit}
        """)
    except Exception as e:
        logger.error("Failed to read outreach logs: %s", e)
        return []
