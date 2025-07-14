# Data Validator & Email Notifier

A Python script that performs data validation using `pandas`, separates valid and invalid records, and sends notification emails with attached CSV reports using `email` and `smtplib`.

This is a simple, top-down script meant to be executed directly. It does encapsulate logic within a `if __name__ == "__main__"` block.

---

## Features

- Reads tabular data from CSV or Excel
- Validates records according to custom rules (e.g., required fields, data types, etc.)
- Outputs valid and invalid entries
- Sends email summaries with attachments

---

## Requirements

- Python 3.8+
- SMTP credentials (e.g., for Gmail, Outlook, etc.)

### Python Dependencies

Install the required packages using pip:

```bash
pip install -r requirements.txt
