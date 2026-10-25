from pydantic import BaseModel


class OutreachRecipient(BaseModel):
    member_name: str
    measure: str = ""
    measure_code: str = ""
    age: int = 0
    pcp: str = ""
    gap: str = ""
    propensity: int = 0


class SendBundleRequest(BaseModel):
    channel: str
    recipients: list[OutreachRecipient]
    message_template: str


class RecipientResult(BaseModel):
    member_name: str
    contact_used: str
    status: str
    detail: str


class SendBundleResponse(BaseModel):
    channel: str
    total: int
    succeeded: int
    failed: int
    results: list[RecipientResult]


class MakeCallRequest(BaseModel):
    member_name: str
    phone: str = ""
    script: str
    measure: str = ""
    measure_code: str = ""


class MakeCallResponse(BaseModel):
    status: str          # "initiated", "failed"
    call_sid: str = ""
    to_number: str = ""
    detail: str = ""


class OutreachLogEntry(BaseModel):
    id: int | None = None
    created_at: str = ""
    member_name: str = ""
    channel: str = ""
    contact_used: str = ""
    measure: str = ""
    measure_code: str = ""
    campaign_name: str = ""
    status: str = ""
    provider_sid: str = ""
    error_detail: str = ""
    script_body: str = ""
    updated_at: str = ""
    member_selection: str = ""
    interaction_log: str = ""


class OutreachLogsResponse(BaseModel):
    total: int
    logs: list[OutreachLogEntry]


class SyncStatusResponse(BaseModel):
    synced: int
    updated: int
    results: list[dict] = []


class VerifiedContact(BaseModel):
    id: int | None = None
    phone: str = ""
    email: str = ""
    label: str = ""
    is_active: bool = True
    created_at: str = ""


class AddContactRequest(BaseModel):
    phone: str
    email: str = ""
    label: str = ""


class VerifiedContactsResponse(BaseModel):
    total: int
    contacts: list[VerifiedContact]
