from uuid import UUID

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from loguru import logger

from src.core.constants import SBP_CALLBACK_PREFIX
from src.core.enums import PaymentGatewayType, TransactionStatus
from src.core.utils.formatters import format_user_log as log
from src.core.utils.message_payload import MessagePayload
from src.infrastructure.database.models.dto import UserDto
from src.services.notification import NotificationService
from src.services.payment_gateway import PaymentGatewayService
from src.services.transaction import TransactionService
from src.services.user import UserService

router = Router(name=__name__)


@router.callback_query(F.data.startswith(SBP_CALLBACK_PREFIX))
async def on_sbp_decision(
    callback: CallbackQuery,
    user: UserDto,
    payment_gateway_service: FromDishka[PaymentGatewayService],
    transaction_service: FromDishka[TransactionService],
    user_service: FromDishka[UserService],
    notification_service: FromDishka[NotificationService],
) -> None:
    if not user.is_privileged:
        await callback.answer("Недостаточно прав", show_alert=True)
        return

    if not callback.data:
        await callback.answer("Некорректные данные")
        return

    parts = callback.data.split(":")
    if len(parts) != 4:
        await callback.answer("Некорректные данные")
        return

    _, action, payment_id_raw, target_user_id_raw = parts
    if action not in {"approve", "cancel"}:
        await callback.answer("Неизвестное действие")
        return

    try:
        payment_id = UUID(payment_id_raw)
    except ValueError:
        await callback.answer("Некорректный ID платежа")
        return

    try:
        target_user_id = int(target_user_id_raw)
    except ValueError:
        await callback.answer("Некорректный ID пользователя")
        return

    transaction = await transaction_service.get(payment_id=payment_id)
    if not transaction:
        await callback.answer("Платеж не найден")
        return

    if transaction.gateway_type != PaymentGatewayType.SBP:
        await callback.answer("Это не SBP платеж")
        return

    if transaction.status != TransactionStatus.PENDING:
        await callback.answer("Платеж уже обработан")
        return

    if action == "approve":
        logger.info(f"{log(user)} Approved SBP payment '{payment_id}'")
        await payment_gateway_service.handle_payment_succeeded(payment_id=payment_id)
        await callback.answer("Платеж подтвержден")
    else:
        logger.info(f"{log(user)} Canceled SBP payment '{payment_id}'")
        await payment_gateway_service.handle_payment_canceled(payment_id=payment_id)

        target_user = await user_service.get(telegram_id=target_user_id)
        await notification_service.notify_user(
            user=target_user,
            payload=MessagePayload(i18n_key="ntf-sbp-payment-rejected"),
        )
        await callback.answer("Платеж отклонен")

    if isinstance(callback.message, Message):
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass
