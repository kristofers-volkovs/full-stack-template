from pathlib import Path

from sqlmodel import SQLModel


class EmailTemplateSchema(SQLModel):
    _template_filename: str = ""

    @property
    def path(self) -> Path:
        return Path(__file__).parent / "templates" / "build" / self._template_filename


class TestEmailTemplate(EmailTemplateSchema):
    _template_filename: str = "test_email.html"
    project_name: str
    email: str


class PasswordResetEmailTemplate(EmailTemplateSchema):
    _template_filename: str = "password_reset_email.html"
    project_name: str
    username: str
    valid_hours: int
    link: str


class NewAccountEmailTemplate(EmailTemplateSchema):
    _template_filename: str = "new_account_email.html"
    project_name: str
    username: str
    link: str
