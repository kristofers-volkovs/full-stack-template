from src.email.email_sender import EmailSender
from src.main.settings import settings


def main() -> None:
    email_receiver = settings.TEST_EMAIL_DESTINATION
    EmailSender.send_test_email(email_receiver=email_receiver)


if __name__ == "__main__":
    main()
