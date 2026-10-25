from enum import Enum


class Status(str, Enum):
    green = "green"
    yellow = "yellow"
    red = "red"


class Channel(str, Enum):
    call = "Call"
    sms = "SMS"
    email = "Email"
    portal = "Portal"


class GapStatus(str, Enum):
    open = "Open"
    partial = "Partial"
    borderline = "Borderline"


class Incentive(str, Enum):
    none = "None"
    card25 = "$25 card"
    card50 = "$50 card"
