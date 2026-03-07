import uuid
from decimal import Decimal
from uuid import UUID

from fastapi import Request

from src.core.enums import TransactionStatus
from src.infrastructure.database.models.dto import PaymentResult

from .base import BasePaymentGateway


class SbpGateway(BasePaymentGateway):
    async def handle_create_payment(self, amount: Decimal, details: str) -> PaymentResult:
        # SBP is processed manually by admin confirmation in bot callbacks.
        return PaymentResult(id=uuid.uuid4(), url=None)

    async def handle_webhook(self, request: Request) -> tuple[UUID, TransactionStatus]:
        raise NotImplementedError("SBP gateway does not support webhooks")
