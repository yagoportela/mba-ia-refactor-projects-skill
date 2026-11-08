import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def order_created(self, pedido_id: int, usuario_id: int):
        logger.info(
            "Pedido criado",
            extra={"pedido_id": pedido_id, "usuario_id": usuario_id},
        )

    def order_status_changed(self, pedido_id: int, status: str):
        logger.info(
            "Status de pedido alterado",
            extra={"pedido_id": pedido_id, "status": status},
        )
