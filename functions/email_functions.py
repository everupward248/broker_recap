from pathlib import Path
import win32com.client
from .logger_setup import get_logger

logger = get_logger(__name__)

def create_email_draft(recipient: str, subject: str, body: str, attachments=None) -> None:
    # launch outlook so that can be interfaced with by python
    """
    Creates an email draft with the provded recipient, subject, body, and invalid broker attachment
    """
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        logger.info("outlook launched")
    except Exception as e:
        logger.warning(e)
        print(e)

    mail = outlook.CreateItem(0)
    mail.Display()
    mail.To = recipient
    mail.Subject = subject
    mail.Body = body
    mail.Display()
   

    if attachments:
        # win32com.client expects attachments as plain string paths and cannot accept python Path objects as argument
        mail.Attachments.Add(str(attachments))
    else:
        logger.warning(f"Atthacment not found: {attachments}")
        print(f"Atthacment not found: {attachments}")

    mail.Save()
    logger.info(f"Email draft created for: {recipient}")
    print(f"Email draft created for: {recipient}")


def test_email(attachment=None):
   create_email_draft(
        recipient="tester_email@test.com",
        subject="TESTING",
        body="This is a email draft used for testing purposes", 
        attachments=attachment
    )

if __name__ == "__main__":
    test_email()