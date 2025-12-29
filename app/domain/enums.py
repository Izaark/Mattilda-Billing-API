from enum import Enum

class InvoiceStatus(str, Enum):
    ISSUED = "ISSUED"
    PARTIAL = "PARTIAL"
    PAID = "PAID"
    VOID = "VOID"


class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    TRANSFER = "TRANSFER"
    CHECK = "CHECK"
    OTHER = "OTHER"