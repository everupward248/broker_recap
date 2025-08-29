from pathlib import Path
import win32com.client
from broker_recap_package.functions.logger_setup import get_logger
import pandas as pd

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
    mail.To = recipient
    mail.Subject = subject
    mail.Body = body
   

    if attachments:
        # win32com.client expects attachments as plain string paths and cannot accept python Path objects as argument
        mail.Attachments.Add(str(attachments))
    else:
        logger.warning(f"Atthacment not found: {attachments}")
        print(f"Atthacment not found: {attachments}")

    mail.Save()
    mail.Display()
    logger.info(f"Email draft created for: {recipient}")
    print(f"Email draft created for: {recipient}")


def test_email(attachment=None):
   create_email_draft(
        recipient="tester_email@test.com",
        subject="TESTING",
        body="This is a email draft used for testing purposes", 
        attachments=attachment
    )
   
def obtain_email_address(file) -> str:
    """
    obtains the first valid email address from the invalid report to pass as the email recipient
    """
    file = pd.read_excel(file)
    # drop the NaNs for the column
    unique_emails = file["Broker_Email"].dropna()
    unique_emails = set(unique_emails)

    # there should only be one valid email address per report, if there are multiple this means the broker provided multiple unique broker codes
    if len(unique_emails) != 1:
        logger.warning(f"There are multiple valid email addressess in the provided report. Please review and ensure that the report is sent to the correct party: {unique_emails}")
        return "WARNING! PLEASE REVIEW BROKER_EMAILS COLUMN"
    email_address = next(iter(unique_emails)) 
    logger.info(f"Email address successfully extracted and being sent to: {email_address}")
    return email_address

    

if __name__ == "__main__":
    test_email()