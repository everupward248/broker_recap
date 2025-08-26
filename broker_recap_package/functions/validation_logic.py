import pandas as pd
import numpy as np
import broker_recap_package.functions.helper_functions as func
import datetime as dt
from .logger_setup import get_logger
from pandas.api.types import is_numeric_dtype, is_number

logger = get_logger(__name__)


def invalid_data(recap_df):
    """add invalid rows to the dataset to ensure validations are being performed properly"""
    
    invalid_df = pd.DataFrame([
        {'date': dt.datetime(2024, 1, 1), 'account': "0PSS1", 'bloomberg_ticker': "NVDA", 'quantity': 9000, 'exec_price': 20, 'bloomberg_contract_code': "SB", 'contract_mth': "F", 'contract_yr': 2027, 'strike': 200, 'F/C/P': "C", 'executing_broker': "SUC"}, 
        {'date': dt.datetime(2026, 1, 1), 'account': "yada", 'bloomberg_ticker': "AAPL", 'quantity': 11000, 'exec_price': 16.5, 'bloomberg_contract_code': "YODELING", 'contract_mth': "J", 'contract_yr': 2024, 'strike': 'foo', 'F/C/P': "asdkhjasjk", 'executing_broker': 1000}, 
        {'date': "abc", 'account': 1, 'bloomberg_ticker': "GOOGL", 'quantity': "abc", 'exec_price': "abc", 'bloomberg_contract_code': "SB", 'contract_mth': 1000, 'contract_yr': "sfasdfsdfs", 'strike': 0, 'F/C/P': 12301, 'executing_broker': "invalid_code"},
        {'date': dt.datetime(2024, 1, 1), 'account': "0PSS1", 'bloomberg_ticker': "NVDA", 'quantity': -8500, 'exec_price': 40, 'bloomberg_contract_code': "SB", 'contract_mth': "F", 'contract_yr': 2027, 'strike': 1000, 'F/C/P': "P", 'executing_broker': "IBX"},
        {'date': dt.datetime(2024, 1, 1), 'account': "0PSS1", 'bloomberg_ticker': "NVDA", 'quantity': -8500, 'exec_price': 40, 'bloomberg_contract_code': "SB", 'contract_mth': "F", 'contract_yr': 2027, 'strike': " ", 'F/C/P': "F", 'executing_broker': "APD"}
    ]
    ) 

    # Concatenate the invalid rows to the recap
    recap_df = pd.concat([recap_df, invalid_df], ignore_index=True)
    logger.info("Invalid data added for testing purposes")
    
    return recap_df


def valid_date(df):
    # checks that date has valid dtype and not a date in the future
    current_date = pd.Timestamp.now()

    df['date'] = df['date'].apply(func.convert_date)

    if type(current_date) == type(df['date'][0]):
        logger.info("Data types are equal for date comparison.")
    else:
        type_a = type(current_date)
        type2 = type(df['date'][0])
        logger.warning(f"Data types for dates are not equal to make comparison. Current date type: {type_a}. Recap date type: {type2}")

    df['valid_date'] = df['date'].apply(lambda x: func.compare_date(x, current_date))
    if df['valid_date'].isin([False]).any():
        logger.warning("Invalid dates detected in broker recap")
    else:
        logger.info("Date validation passed.")

    return df

def valid_account(validation_df, valid_acct_df):
    # account provided in the broker report must be included in the valid accounts records

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

    return validation_df

def valid_quantity(validation_df):
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

    return validation_df

def valid_execution_price(validation_df):
    # the exec_price must be a number
    if not is_numeric_dtype(validation_df['exec_price']):
        exec_type = validation_df['exec_price'].dtype
        validation_df['exec_price'] = validation_df['exec_price'].apply(func.safe_to_numeric)
        exec_type2 = validation_df['exec_price'].dtype
        logger.warning(f"Execution price data type invalid: {exec_type}. Execution price data type converted to {exec_type2}")
    else:
        exec_type = validation_df['exec_price'].dtype
        logger.info(f"Execution price is a valid data type: {exec_type}.")

    validation_df['valid_exec_price'] = validation_df['exec_price'].apply(lambda x: is_number(x))

    if validation_df['valid_exec_price'].isin([False]).any():
        logger.warning("Invalid execution prices detected in broker recap")
    else:
        logger.info("Execution price validation passed.")
    return validation_df

def valid_bbg(validation_df, contract_df):
    # check to ensure that bloomberg contract provided is a valid contract code
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

    return validation_df

def valid_month(validation_df):
    # contract code must be one from the list below
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

    return validation_df

def valid_year(validation_df):
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

    return validation_df

def valid_strike_price(validation_df):
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

    return validation_df

def valid_instrument(validation_df):
    # create the boolean checker col
    validation_df['valid_F/C/P'] = validation_df['F/C/P'].isin(['F', 'C', 'P'])

    if validation_df['valid_F/C/P'].isin([False]).any():
        logger.warning("Invalid contract code detected in broker recap")
    else:
        logger.info("Contract code validation passed.")
    
    return validation_df

def valid_broker(validation_df, broker_df):
    # check that executing broker provided is a valid broker from broker_codes.xlxs
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
        broker_df[['Broker_Code', 'Broker_Name', 'Broker_Email']],
        how='left',
        left_on='executing_broker', 
        right_on='Broker_Code'
    )

    if validation_df['valid_executing_broker'].isin([False]).any():
        logger.warning("Invalid executing broker detected in broker recap")
    else:
        logger.info("Executing broker validation passed.")

    return validation_df

def perform_all_validations(recap_df, broker_df, contract_df, valid_acct_df):
    """runs all validation functions contained in the validation_logic module"""

     # create a copy of the recap to append boolean checks to
    validation_df = recap_df.copy()

    validation_df = valid_date(validation_df)
    validation_df = valid_account(validation_df, valid_acct_df)
    validation_df = valid_quantity(validation_df)
    validation_df = valid_execution_price(validation_df)
    validation_df = valid_bbg(validation_df, contract_df)
    validation_df = valid_month(validation_df)
    validation_df = valid_year(validation_df)
    validation_df = valid_strike_price(validation_df)
    validation_df = valid_instrument(validation_df)
    validation_df = valid_broker(validation_df, broker_df)
    
    return validation_df








