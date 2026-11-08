import logging
import smtplib

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, host="", port=587, username="", password="", sender=""):
        self.host = host
        self.port = int(port or 587)
        self.username = username
        self.password = password
        self.sender = sender or username
        self.enabled = bool(host and username and password)

    @classmethod
    def from_config(cls, config):
        return cls(
            host=config.get("SMTP_HOST", ""),
            port=config.get("SMTP_PORT", 587),
            username=config.get("SMTP_USER", ""),
            password=config.get("SMTP_PASSWORD", ""),
            sender=config.get("SMTP_FROM", ""),
        )

    def send_email(self, to: str, subject: str, body: str) -> bool:
        if not self.enabled:
            logger.info(
                "SMTP não configurado; e-mail não enviado",
                extra={"to": to, "subject": subject},
            )
            return False

        try:
            server = smtplib.SMTP(self.host, self.port, timeout=5)
            server.starttls()
            server.login(self.username, self.password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.sender, to, message)
            server.quit()
            return True
        except Exception:
            logger.exception("Falha ao enviar e-mail", extra={"to": to})
            return False

    def notify_task_assigned(self, user, task) -> bool:
        if user is None or not getattr(user, "email", None):
            return False
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        return self.send_email(user.email, subject, body)

    def notify_task_overdue(self, user, task) -> bool:
        if user is None or not getattr(user, "email", None):
            return False
        subject = f"Task atrasada: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\n"
            f"Data limite: {task.due_date}"
        )
        return self.send_email(user.email, subject, body)
