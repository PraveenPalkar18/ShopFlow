import logging

logger = logging.getLogger("shopflow.notifications")


def send_order_confirmation(email: str, order_id: int) -> None:
    logger.info(
        "notification_simulated event=order_confirmation order_id=%s recipient=%s",
        order_id,
        email,
    )


def send_order_cancellation(email: str, order_id: int) -> None:
    logger.info(
        "notification_simulated event=order_cancellation order_id=%s recipient=%s",
        order_id,
        email,
    )
