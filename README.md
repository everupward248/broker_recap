# Daily Broker Recap Validator and Email Drafter

A command line interface program using `click` that performs data validation using `pandas`, separates valid and invalid records using `pathlib`, and drafts notification emails with attached CSV reports using `win32com`.

## Business Problem
At a hedge fund, reports are received daily from the brokers regarding trades made on clients' behalf that day. These files will then be using to update the portfolio management system. 

However, these reports often contain errors such as: typos, mispriced trades, or invalid internal codes. 

This script automates the data validation of these reports, consolidating the valid trades and separating the invalids, then drafts emails containing the invalid entries report to the relevant broker with a dynamic email body summarizing the errors.

---

## Features

- Reads tabular data from CSV or Excel
- Validates records according to custom rules (e.g., required fields, data types, etc.)
- Outputs valid and invalid entries
- Drafts email summaries with attachments

---

