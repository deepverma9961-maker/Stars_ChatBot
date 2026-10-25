from contextlib import contextmanager
from databricks import sql
from .config import settings


def _connect():
    hostname = settings.databricks_host.replace("https://", "").replace("http://", "").rstrip("/")
    return sql.connect(
        server_hostname=hostname,
        http_path=settings.databricks_http_path,
        access_token=settings.databricks_token,
        _socket_timeout=30,
    )


@contextmanager
def get_cursor():
    conn = _connect()
    try:
        with conn.cursor() as cursor:
            yield cursor
    finally:
        conn.close()


def query(sql_text: str, params: dict | None = None) -> list[dict]:
    with get_cursor() as cursor:
        cursor.execute(sql_text, params or {})
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]


def query_one(sql_text: str, params: dict | None = None) -> dict | None:
    rows = query(sql_text, params)
    return rows[0] if rows else None


def execute_write(sql_text: str, params: dict | None = None) -> None:
    with get_cursor() as cursor:
        cursor.execute(sql_text, params or {})


_table_exists_cache: dict[str, bool] = {}

def table_exists(fqn: str) -> bool:
    if fqn in _table_exists_cache:
        return _table_exists_cache[fqn]
    try:
        query(f"SELECT 1 FROM {fqn} LIMIT 1")
        _table_exists_cache[fqn] = True
    except Exception:
        _table_exists_cache[fqn] = False
    return _table_exists_cache[fqn]
