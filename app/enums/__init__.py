from enum import Enum


class EStatus(Enum):
    CREATED = "criado"
    EXPIRED = "expirado"
    ANALYSIS = "em análise"
    COMPLETE = "concluído"
    CARHEBACK = "chargeback"
    PAID = "pago"
    REFUDED = "reembolsado"
    FAILED = "falha no pagamento"
