from pathlib import Path
import win32com.client
from .logger_setup import get_logger

logger = get_logger(__name__)


# This is an outdated version which only works with outlook classic
def create_email_draft(recipient, subject, body, attachments=None):
    # launch outlook so that can be interfaced with by python
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        logger.info("outlook launched")
    except Exception as e:
        logger.warning(e)
        print(e)

    mail = outlook.CreateItem(0)

    mail.To = recipient
    mail.Subject = subject
    mail.Body = body

    if attachments:
        for file_path in attachments:
            file = Path(file_path)
            if file.exists():
                mail.Attachments.Add(str(file))
            else:
                print(f"Atthacment not found: {file}")

    mail.Save()
    print(f"Email draft created for: {recipient}")


def main():
   create_email_draft(
        recipient="everupward248@gmail.com",
        subject="TESTING",
        body="This is a tester email #5"
    )


if __name__ == "__main__":
    main()