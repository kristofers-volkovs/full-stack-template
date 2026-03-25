import smtplib
from email.mime.text import MIMEText

from jinja2 import Template

from src.email.email_template_schemas import (
    EmailTemplateSchema,
    NewAccountEmailTemplate,
    PasswordResetEmailTemplate,
    TestEmailTemplate,
)
from src.exceptions.not_implemented_501 import ActionUnavailable501Exception
from src.main.logging import get_logger
from src.main.settings import settings

logger = get_logger(__name__)


class EmailSender:
    @staticmethod
    def _send_email(
        *, email_receiver: str, template_context: EmailTemplateSchema, subject: str
    ) -> None:
        email_sender = settings.SMTP_USER
        sender_password = settings.SMTP_PASSWORD
        server_host = settings.SMTP_HOST
        server_port = settings.SMTP_PORT

        emails_unavailable = ActionUnavailable501Exception(
            "Sending emails is unavailable"
        )
        if email_sender is None:
            logger.error("SMTP_USER is not set in .env")
            raise emails_unavailable
        elif sender_password is None:
            logger.error("SMTP_PASSWORD is not set in .env")
            raise emails_unavailable
        elif server_host is None:
            logger.error("SMTP_HOST is not set in .env")
            raise emails_unavailable
        elif server_port is None:
            logger.error("SMTP_PORT is not set in .env")
            raise emails_unavailable

        context = template_context.model_dump(exclude_unset=True)
        template_str = template_context.path.read_text()
        html_content = Template(template_str).render(context)

        html_message = MIMEText(html_content, "html")
        html_message["Subject"] = subject
        html_message["From"] = email_sender
        html_message["To"] = email_receiver

        server = smtplib.SMTP(server_host, server_port)
        server.starttls()
        server.login(email_sender, sender_password)
        server.sendmail(email_sender, email_receiver, html_message.as_string())

    @classmethod
    def send_test_email(cls, *, email_receiver: str) -> None:
        template_context = TestEmailTemplate(
            project_name=settings.PROJECT_NAME,
            email=email_receiver,
        )
        cls._send_email(
            email_receiver=email_receiver,
            template_context=template_context,
            subject=f"{settings.PROJECT_NAME} - test email",
        )
        logger.info(f"Test email sent to {email_receiver}")

    @classmethod
    def send_password_reset_email(cls, *, email_receiver: str, token: str) -> None:
        password_token_expires_hours = int(
            settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES / 60
        )
        link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
        template_context = PasswordResetEmailTemplate(
            project_name=settings.PROJECT_NAME,
            username=email_receiver,
            valid_hours=password_token_expires_hours,
            link=link,
        )
        cls._send_email(
            email_receiver=email_receiver,
            template_context=template_context,
            subject=f"{settings.PROJECT_NAME} - Password recovery for {email_receiver}",
        )

    @classmethod
    def send_new_account_email(cls, *, email_receiver: str) -> None:
        template_context = NewAccountEmailTemplate(
            project_name=settings.PROJECT_NAME,
            username=email_receiver,
            link=settings.FRONTEND_HOST,
        )
        cls._send_email(
            email_receiver=email_receiver,
            template_context=template_context,
            subject=f"{settings.PROJECT_NAME} - New account for {email_receiver}",
        )
