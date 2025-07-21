import pandas as pd
import numpy as np
from functions import helper_functions as func
import datetime as dt
from functions.logger_setup import get_logger
from pandas.api.types import is_numeric_dtype, is_number
from functions import validation_logic as vl
from functions import composite_checks as cc

#################################################################################################################################################################################################
logger = get_logger(__name__)
################################################################################################################################################################################################
# input the datasets
try:
    # create the dataframes from the recap and validation data
    recap_df = pd.read_excel('data/recap.xlsx')
    broker_df = pd.read_excel('data/broker_codes.xlsx')
    contract_df = pd.read_excel('data/contract_codes.xlsx')
    valid_acct_df = pd.read_excel('data/valid_accounts.xlsx')

    # success message
    logger.info(f"files read successfully")

except Exception as e:
    logger.warning(f"An unexpected error occured: {e}") 

################################################################################################################################################################################################

# add invalid rows to the dataset to ensure validations are being performed properly
invalid_df = pd.DataFrame([
    {'date': dt.datetime(2024, 1, 1), 'account': "0PSS1", 'bloomberg_ticker': "NVDA", 'quantity': 9000, 'exec_price': 20, 'bloomberg_contract_code': "SB", 'contract_mth': "F", 'contract_yr': 2027, 'strike': 200, 'F/C/P': "C", 'executing_broker': "APD"}, 
    {'date': dt.datetime(2026, 1, 1), 'account': "yada", 'bloomberg_ticker': "AAPL", 'quantity': 11000, 'exec_price': 16.5, 'bloomberg_contract_code': "YODELING", 'contract_mth': "J", 'contract_yr': 2024, 'strike': 'foo', 'F/C/P': "asdkhjasjk", 'executing_broker': 1000}, 
    {'date': "abc", 'account': 1, 'bloomberg_ticker': "GOOGL", 'quantity': "abc", 'exec_price': "abc", 'bloomberg_contract_code': "SB", 'contract_mth': 1000, 'contract_yr': "sfasdfsdfs", 'strike': 0, 'F/C/P': 12301, 'executing_broker': "invalid_code"},
    {'date': dt.datetime(2024, 1, 1), 'account': "0PSS1", 'bloomberg_ticker': "NVDA", 'quantity': -8500, 'exec_price': 40, 'bloomberg_contract_code': "SB", 'contract_mth': "F", 'contract_yr': 2027, 'strike': 1000, 'F/C/P': "P", 'executing_broker': "APD"},
    {'date': dt.datetime(2024, 1, 1), 'account': "0PSS1", 'bloomberg_ticker': "NVDA", 'quantity': -8500, 'exec_price': 40, 'bloomberg_contract_code': "SB", 'contract_mth': "F", 'contract_yr': 2027, 'strike': " ", 'F/C/P': "F", 'executing_broker': "APD"}
]
) 

# Concatenate the invalid rows to the recap
recap_df = pd.concat([recap_df, invalid_df], ignore_index=True)

################################################################################################################################################################################################
# create a copy of the recap to append boolean checks to
validation_df = recap_df.copy()

validation_df = vl.valid_date(validation_df)
validation_df = vl.valid_account(validation_df, valid_acct_df)
validation_df = vl.valid_quantity(validation_df)
validation_df = vl.valid_execution_price(validation_df)
validation_df = vl.valid_bbg(validation_df, contract_df)
validation_df = vl.valid_month(validation_df)
validation_df = vl.valid_year(validation_df)
validation_df = vl.valid_strike_price(validation_df)
validation_df = vl.valid_instrument(validation_df)
validation_df = vl.valid_broker(validation_df, broker_df)

print(validation_df)

##################################################################################################################################################################
# # separate the datasets into the valid and invalid datasets for reporting.

valid_df, invalid_df = cc.separate_datasets(validation_df)

###############################################################################################################################################################
# Format the valid dataset before sending for reporting
valid_report = cc.default_values(valid_df)
valid_report = cc.add_date(valid_report, valid_df)
valid_report = cc.add_account(valid_report, valid_df)
valid_report = cc.add_quantity(valid_report, valid_df)
valid_report = cc.add_trade_price(valid_report, valid_df)
valid_report = cc.add_identifier(valid_report, valid_df)
valid_report = cc.add_psid(valid_report, valid_df)
valid_report = cc.add_executing_broker(valid_report, valid_df)
valid_report = cc.add_internal(valid_report, valid_df)
valid_report = cc.add_clearing_firm(valid_report, valid_df)

# export the reports as excel worksheets to be emailed
with pd.ExcelWriter('data/output.xlsx') as writer:  
    valid_report.to_excel(writer, sheet_name='valid_report', index=False)
    invalid_df.to_excel(writer, sheet_name='invalid_report', index=False)

#############################################################################################################################################################
# add automated email via smtplib
# make the body string

body_string = "This is a test to send an email with attachments for reporting. SSL used for the SMTP server connection."

func.send_email('data/output.xlsx', 'logs/validation_log_main.log', body_string)


if __name__ == '__main__':
    pass










