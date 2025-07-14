import pandas as pd
import numpy as np
from functions import helper_functions as func
import datetime as dt
from functions.logger_setup import get_logger
from pandas.api.types import is_numeric_dtype, is_number

#################################################################################################################################################################################################
# # add the logger
# logger = logging.getLogger(__name__)
# # add handler to define where the log goes to
# handler = logging.FileHandler('validation_log.log', mode='w')
# # add formatter to define structure of the log message
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d")
# # set the format to the handler
# handler.setFormatter(formatter)
# # add the handler to the logger
# logger.addHandler(handler)
# # set the level of the logger
# logger.setLevel(logging.DEBUG)

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
# add boolean checkers for each validation
# vectorization and apply approach decided over row iteration to avoid row by row overhead from python as data stores as numpy array where loops are executed at C level

# create a copy of the recap to append boolean checks to
validation_df = recap_df.copy()

# first check is for the date, the date per the recap cannot be a day in the future
# get the current time with pandas Timestamp and compare to the date in the recap
current_date = pd.Timestamp.now()
# make sure same data type before comparison
validation_df['date'] = validation_df['date'].apply(func.convert_date)


if type(current_date) == type(validation_df['date'][0]):
    logger.info("Data types are equal for date comparison.")
else:
    # store types for log message
    type1 = type(current_date)
    type2 = type(validation_df['date'][0])
    logger.warning(f"Data types for dates are not equal to make comparison. Current date type: {type1}. Recap date type: {type2}")

# check that dates are not in future
# validation_df['valid_date'] = validation_df['date'].apply(lambda d: d <= current_date)
validation_df['valid_date'] = validation_df['date'].apply(lambda x: func.compare_date(x, current_date))
if validation_df['valid_date'].isin([False]).any():
    logger.warning("Invalid dates detected in broker recap")
else:
    logger.info("Date validation passed.")

# to use isin for checks in the validation data sets
# pandas can store strings as object data type, explicitly convert to string to enforce account code data types
if (validation_df['account'].dtype != 'string') & (valid_acct_df['Account_Code'].dtype != 'string'):
    # enforce string data type
    validation_df['account'] = validation_df['account'].astype('string')
    valid_acct_df['Account_Code'] = valid_acct_df['Account_Code'].astype('string')
    
    logger.warning(f"Account codes not stored as strings. Data type converted to {validation_df['account'].dtype}")
else:
    logger.info("Account codes are valid data types")


# ensure that the data being compared is of the same type
if validation_df['account'].dtype == valid_acct_df['Account_Code'].dtype:
    logger.info("Data types are equal for account code comparison.")
else:
    type1 = validation_df['account'].dtype
    type2 = valid_acct_df['Account_Code'].dtype
    logger.warning(f"Data types for dates are not equal to make comparison. Current date type: {type1}. Recap date type: {type2}")

# add boolean checker for account being in valid accounts
validation_df['valid_account'] = validation_df['account'].isin(valid_acct_df['Account_Code'])

# add the broker names for the 'Clearing_Firm' column for the final report
validation_df = validation_df.merge(
    valid_acct_df[['Account_Code', 'Counterparty_Name']],
    how='left',
    left_on='account', 
    right_on='Account_Code'
)

if validation_df['valid_account'].isin([False]).any():
    logger.warning("Invalid accounts detected in broker recap")
else:
    logger.info("Account validation passed.")

# commodity quantity check
# must be a number
if not is_numeric_dtype(validation_df['quantity']):
    logger.warning("Quantity data type invalid")
else:
    quant_type = validation_df['quantity'].dtype
    logger.info(f"Quantity is a valid data type: {quant_type}.")

# create boolean checker column that quantity is a number, non-zero, in realistic range
validation_df['valid_quantity'] = validation_df['quantity'].apply(lambda x: func.quant_range(x, 10000))

if validation_df['valid_quantity'].isin([False]).any():
    logger.warning("Invalid quantities detected in broker recap")
else:
    logger.info("Quantity validation passed.")

# exec_price validation check
# the exec_price must be a number
if not is_numeric_dtype(validation_df['exec_price']):
    exec_type = validation_df['exec_price'].dtype
    # use safe_to_numeric to convert to numeric dtype and leave non-numeric entries unchanged for reporting
    validation_df['exec_price'] = validation_df['exec_price'].apply(func.safe_to_numeric)
    exec_type2 = validation_df['exec_price'].dtype
    logger.warning(f"Execution price data type invalid: {exec_type}. Execution price data type converted to {exec_type2}")
else:
    exec_type = validation_df['exec_price'].dtype
    logger.info(f"Execution price is a valid data type: {exec_type}.")

# boolean checker exec_price being a number
# use apply() and is_number to check each row in column for numeric data type
validation_df['valid_exec_price'] = validation_df['exec_price'].apply(lambda x: is_number(x))

if validation_df['valid_exec_price'].isin([False]).any():
    logger.warning("Invalid execution prices detected in broker recap")
else:
    logger.info("Execution price validation passed.")

# bloomberg_contract_code validation check
# enforce the data type of the column as string
if (validation_df['bloomberg_contract_code'].dtype != 'string') | (contract_df['Contract_Code'].dtype != 'string'):
    # enforce string data type
    validation_df['bloomberg_contract_code'] = validation_df['bloomberg_contract_code'].astype('string')
    contract_df['Contract_Code'] = contract_df['Contract_Code'].astype('string')
    
    logger.warning(f"Bloomberg contract codes not stored as strings. Data type converted to {validation_df['bloomberg_contract_code'].dtype}")
else:
    logger.info("Bloomberg contract codes are valid data types")

# ensure same type for comparison
if validation_df['bloomberg_contract_code'].dtype != contract_df['Contract_Code'].dtype:
    type1 = validation_df['bloomberg_contract_code'].dtype
    type2 = contract_df['Contract_Code'].dtype
    logger.warning(f"Data being compared not of the same type: Receap {type1} Contract Codes: {type2}")
else:
    logger.info("Data types are equal for bloomberg contract code comparison.")

# add boolean checker for bloomberg contract code being in valid bloomberg contract codes
validation_df['valid_bloomberg_contract_code'] = validation_df['bloomberg_contract_code'].isin(contract_df['Contract_Code'])
if validation_df['valid_bloomberg_contract_code'].isin([False]).any():
    logger.warning("Invalid bloomberg contract codes detected in broker recap")
else:
    logger.info("bloomberg contract code validation passed.")

# contract_mth validation check
# Code submitted must be a valid code from the list below
# contract month valid codes
contract_months_df = pd.Series(["F","G","H","J","K","M","N","Q","U","V","X","Z"], dtype='string')

# enforce the data type of the column as string
if (validation_df['contract_mth'].dtype != 'string') | (contract_months_df.dtype != 'string'):
    # enforce string data type
    validation_df['contract_mth'] = validation_df['contract_mth'].astype('string')
    contract_months_df = contract_months_df.astype('string')
    
    logger.warning(f"Contract month not stored as strings. Data type converted to {validation_df['contract_mth'].dtype}")
else:
    logger.info("Contract months are valid data types")

# boolean check if valid contract month code
validation_df['valid_contract_mth'] = validation_df['contract_mth'].isin(contract_months_df) 

if validation_df['valid_contract_mth'].isin([False]).any():
    logger.warning("Invalid contract months detected in broker recap")
else:
    logger.info("Contract month validation passed.")

# contract year validation check
# the year must be the present year or later, cannot be a year in the past, contract year must be a number
# use datetime to get the current year
cy =  dt.datetime.now().year

# check the data type of the input and force int64 datatype for numeric rows
if not is_numeric_dtype(validation_df['contract_yr']):
    validation_df['contract_yr'] = validation_df['contract_yr'].apply(func.safe_to_numeric)
    contract_yr_type = validation_df['contract_yr'].dtype
    logger.warning(f"Contract year data type invalid: {contract_yr_type}")
else:
    contract_yr_type = validation_df['contract_yr'].dtype
    logger.info(f"Contract year is a valid data type: {contract_yr_type}.")

# create boolean checker column that quantity is a number, non-zero, in realistic range
validation_df['valid_contract_yr'] = validation_df['contract_yr'].apply(lambda x: func.is_valid_contract_yr(x, cy))

if validation_df['valid_contract_yr'].isin([False]).any():
    logger.warning("Invalid contract years detected in broker recap")
else:
    logger.info("Contract years validation passed.")

# strike price validation check
# must be numeric data type and must be populated for options 'C' & 'P'

# check the data type of the input and force float64 datatype for numeric rows
if not is_numeric_dtype(validation_df['strike']):
    validation_df['strike'] = validation_df['strike'].apply(func.safe_to_numeric)
    strike_type = validation_df['strike'].dtype
    logger.warning(f"Strike price data type invalid: {strike_type}")
else:
    strike_type = validation_df['strike'].dtype
    logger.info(f"Strike price is a valid data type: {strike_type}.")

# create boolean checker column that quantity is a number, non-zero, in realistic range
validation_df['valid_strike'] = validation_df.apply(lambda row: func.is_valid_strike(row['strike'], row['F/C/P']), axis=1)

if validation_df['valid_strike'].isin([False]).any():
    logger.warning("Invalid strike price detected in broker recap")
else:
    logger.info("Strike price validation passed.")

# F/C/P validation check
# create the boolean checker col
validation_df['valid_F/C/P'] = validation_df['F/C/P'].isin(['F', 'C', 'P'])

if validation_df['valid_F/C/P'].isin([False]).any():
    logger.warning("Invalid contract code detected in broker recap")
else:
    logger.info("Contract code validation passed.")

# executing broker validation check
# ensure the same data type before comparison


if (validation_df['executing_broker'].dtype != 'string') | (broker_df['Broker_Code'].dtype != 'string'):
    # enforce string data type
    validation_df['executing_broker'] = validation_df['executing_broker'].astype('string')
    broker_df['Broker_Code'] = broker_df['Broker_Code'].astype('string')
    
    logger.warning(f"Executing broker codes not stored as strings. Data type converted to {validation_df['executing_broker'].dtype} & {broker_df['Broker_Code'].dtype}")
else:
    logger.info("Executing broker codes are valid data types")

# ensure same type for comparison
if validation_df['executing_broker'].dtype != broker_df['Broker_Code'].dtype:
    type1 = validation_df['executing_broker'].dtype
    type2 = broker_df['Broker_Cod'].dtype
    logger.warning(f"Data being compared not of the same type: Receap {type1} Contract Codes: {type2}")
else:
    logger.info("Data types are equal for bloomberg contract code comparison.")

# add boolean checker for bloomberg contract code being in valid bloomberg contract codes
validation_df['valid_executing_broker'] = validation_df['executing_broker'].isin(broker_df['Broker_Code'])

# add the broker names for the 'Internal' column for the final report
validation_df = validation_df.merge(
    broker_df[['Broker_Code', 'Broker_Name']],
    how='left',
    left_on='executing_broker', 
    right_on='Broker_Code'
)

if validation_df['valid_executing_broker'].isin([False]).any():
    logger.warning("Invalid executing broker detected in broker recap")
else:
    logger.info("Executing broker validation passed.")

##################################################################################################################################################################
# separate the datasets into the valid and invalid datasets for reporting.

# identify the validation columns dynamically
try: 
    validation_columns = [col for col in validation_df.columns if col.strip().startswith('valid')]
    if len(validation_columns) != 10:
        logger.warning("Not all validation columns parsed from the validation df")
    else:
        logger.info("Validation columns successfuly parsed from the validation df, proceed to creating the valid and invalid dateframes for reporting")
except Exception as e:
    logger.warning(f"An unexpected error occured: {e}") 


# separate into valid and invalid df
try:  
    valid_df = validation_df[validation_df[validation_columns].all(axis=1)].copy()
    invalid_df = validation_df[~validation_df[validation_columns].all(axis=1)].copy()

    logger.info("Valid and Invalid dataframes created")
except Exception as e:
    logger.warning(f"An unexpected error occured: {e}") 

###############################################################################################################################################################
# Format the valid dataset before sending for reporting

# Define default values
default_values = {
    'Source': "GIVEUP",                    # string
    'Strategy / Sub_Strategy': '',         # string
    'Trade_Type': 0,                       # int
    'Execution_Type': 'V'                  # string
}

num_rows = int(len(valid_df))

# create an empty dataframe with rows equal to the rows of valid df and populate the columns with a deafualt value
try:
    valid_report = pd.DataFrame([default_values] * num_rows)
    logger.info("Default columns successfully added.")
    # Enforce specific types
    valid_report = valid_report.astype({
        'Source': 'string',
        'Strategy / Sub_Strategy': 'string',
        'Trade_Type': 'int',
        'Execution_Type': 'string'
    })
except:
     logger.warning(f"Default columns not successfuly added to final valid report") 

# add date
try:
    valid_report['Trade_Date'] = valid_df['date'].values
    pd.to_datetime(valid_report['Trade_Date'])
    data_type = valid_report['Trade_Date'].dtype
    logger.info(f"Date column successfuly added to the valid entries for reporting. Date column of dtype: {data_type}")
except:
    logger.warning(f"Date column not successfuly added to final valid report") 

# add account 
try:
    valid_report['Account'] = valid_df['account'].values.astype('string')
    data_type = valid_report['Account'].dtype
    logger.info(f"Account column successfuly added to the valid entries for reporting. Account column of dtype: {data_type}")
except:
    logger.warning(f"Account column not successfuly added to final valid report") 

# add quantity
try:
    valid_report['Quantity'] = valid_df['quantity'].values.astype('float64')
    data_type = valid_report['Quantity'].dtype
    logger.info(f"Quantity column successfuly added to the valid entries for reporting. Quantity column of dtype: {data_type}")
except:
    logger.warning(f"Quantity column not successfuly added to final valid report") 

# add execution price
try:
    valid_report['Trade_Price'] = valid_df['exec_price'].values.astype('float64')
    data_type = valid_report['Trade_Price'].dtype
    logger.info(f"Trade price column successfuly added to the valid entries for reporting. Trade price column of dtype: {data_type}")
except:
    logger.warning(f"Trade price column not successfuly added to final valid report") 


# add bloomberg identifier

try:
    # Capitalize the 'F/C/P' column; default to 'F' if missing
    valid_df['F/C/P'] = valid_df['F/C/P'].str.upper().fillna('F')

    # Is the row a future or is the 'F/C/P' value empty?
    type_condition = valid_df['F/C/P'].isin(['F', ''])
    # check if strike price is empty or null
    strike_condition = (valid_df['strike'].isnull()) | (valid_df['strike'].astype('string').str.strip() == '')

    # Build the short label for the Bloomberg ticker
    valid_report['Identifier'] = np.where(
        valid_df['bloomberg_contract_code'].str.len() > 1, 
        valid_df['bloomberg_contract_code'] + valid_df['contract_mth'].str[0] 
            + valid_df['contract_yr'].astype('string').str[-1]
            + np.where(type_condition, '', valid_df['F/C/P']) 
            + np.where(strike_condition, ' ', ' ' + valid_df['strike'].astype('string') + ' ') 
            + 'Comdty',
        valid_df['bloomberg_contract_code'] + ' ' + valid_df['contract_mth'].str[0] 
            + valid_df['contract_yr'].astype('string').str[-1] 
            + np.where(type_condition, '', valid_df['F/C/P']) 
            + np.where(strike_condition, ' ', ' ' + valid_df['strike'].astype('string') + ' ')
            + 'Comdty'
    ).copy()

    # enfore string dtype as above returns object
    valid_report['Identifier'] = valid_report['Identifier'].astype('string')

    data_type = valid_report['Identifier'].dtype
    logger.info(f"Identifer column successfuly added to the valid entries for reporting. Identifier column of dtype: {data_type}")
    
except: 
    logger.warning("Identifier short label unsuccessul.")

# add PS_ID
try:
    # create the conditional values
    val_if_true = (
        valid_df['bloomberg_contract_code']
        + '_' + valid_df['contract_mth'].str[0]
        + '_' + valid_df['contract_yr'].astype('string')
    )
    val_if_false = (
        valid_df['bloomberg_contract_code']
        + '_' + valid_df['contract_mth'].str[0]
        + '_' + valid_df['contract_yr'].astype('string')
        + '_' + valid_df['strike'].fillna(0).astype('string')
        + valid_df['F/C/P']
    )

    valid_report['PS_ID'] = np.where(type_condition, val_if_true, val_if_false)
    # enfore string dtype as above returns object
    valid_report['PS_ID'] = valid_report['PS_ID'].astype('string')

    data_type = valid_report['PS_ID'].dtype
    logger.info(f"PS_ID column successfuly added to the valid entries for reporting. PS_ID column of dtype: {data_type}")

except:
    logger.warning("PS_ID short label unsuccessul.")

# add executing broker
try:
    valid_report['Executing_Broker'] = valid_df['executing_broker'].values.astype('string')
    data_type = valid_report['Executing_Broker'].dtype
    logger.info(f"Executing broker column successfuly added to the valid entries for reporting. Executing broker column of dtype: {data_type}")
except:
    logger.warning(f"Executing broker column not successfuly added to final valid report") 

# add internal
try:
    valid_report['Internal'] = valid_df['Broker_Name'].values
    valid_report['Internal'] = valid_report['Internal'] + " " + valid_report['Source'] 
    valid_report['Internal'].astype('string')
    data_type = valid_report['Internal'].dtype
    logger.info(f"Internal column successfully added to the valid entried for reporting. Internal column of dtype: {data_type}")
except:
    logger.warning(f"Internal column not successfuly added to final valid report") 

# add clearing firm
try:
    valid_report['Clearing_Firm'] = valid_df['Counterparty_Name'].values
    valid_report['Clearing_Firm'] = valid_report['Clearing_Firm'].astype('string')
    data_type = valid_report['Clearing_Firm'].dtype
    logger.info(f"Clearing firm column successfully added to the valid entried for reporting. Clearing firm column of dtype: {data_type}")
except:
    logger.warning(f"Clearing firm not successfuly added to final valid report") 

# export the reports as excel worksheets to be emailed
with pd.ExcelWriter('data/output.xlsx') as writer:  
    valid_report.to_excel(writer, sheet_name='valid_report', index=False)
    invalid_df.to_excel(writer, sheet_name='invalid_report', index=False)

#############################################################################################################################################################
# add automated email via smtplib
# make the body string

body_string = "This is a test to send an email with attachments for reporting. SSL used for the SMTP server connection."

func.send_email('data/output.xlsx', 'validation_log.log', body_string)


if __name__ == '__main__':
    pass










