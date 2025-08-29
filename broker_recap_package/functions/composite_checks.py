import pandas as pd
import numpy as np
import broker_recap_package.functions.helper_functions as func
from broker_recap_package.functions.logger_setup import get_logger
from datetime import date
from pathlib import Path
import sys

logger = get_logger(__name__)

def separate_datasets(validation_df):
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

    return valid_df, invalid_df

def default_values(valid_df):
    # Format the valid dataset before sending for reporting

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

    return valid_report

def add_date(valid_report, valid_df):
    try:
        valid_report['Trade_Date'] = valid_df['date'].values
        pd.to_datetime(valid_report['Trade_Date'])
        data_type = valid_report['Trade_Date'].dtype
        logger.info(f"Date column successfuly added to the valid entries for reporting. Date column of dtype: {data_type}")
    except:
        logger.warning(f"Date column not successfuly added to final valid report")
    
    return valid_report

def add_account(valid_report, valid_df):
    try:
        valid_report['Account'] = valid_df['account'].values.astype('string')
        data_type = valid_report['Account'].dtype
        logger.info(f"Account column successfuly added to the valid entries for reporting. Account column of dtype: {data_type}")
    except:
        logger.warning(f"Account column not successfuly added to final valid report") 

    return valid_report

def add_quantity(valid_report, valid_df):
    try:
        valid_report['Quantity'] = valid_df['quantity'].values.astype('float64')
        data_type = valid_report['Quantity'].dtype
        logger.info(f"Quantity column successfuly added to the valid entries for reporting. Quantity column of dtype: {data_type}")
    except:
        logger.warning(f"Quantity column not successfuly added to final valid report") 

    return valid_report

def add_trade_price(valid_report, valid_df):
    try:
        valid_report['Trade_Price'] = valid_df['exec_price'].values.astype('float64')
        data_type = valid_report['Trade_Price'].dtype
        logger.info(f"Trade price column successfuly added to the valid entries for reporting. Trade price column of dtype: {data_type}")
    except:
        logger.warning(f"Trade price column not successfuly added to final valid report") 
    
    return valid_report

def add_identifier(valid_report, valid_df):
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

    return valid_report

def add_psid(valid_report, valid_df):

    try:
        # Capitalize the 'F/C/P' column; default to 'F' if missing
        valid_df['F/C/P'] = valid_df['F/C/P'].str.upper().fillna('F')
        # Is the row a future or is the 'F/C/P' value empty?
        type_condition = valid_df['F/C/P'].isin(['F', ''])
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
    
    return valid_report

def add_executing_broker(valid_report, valid_df):
    # add executing broker
    try:
        valid_report['Executing_Broker'] = valid_df['executing_broker'].values.astype('string')
        data_type = valid_report['Executing_Broker'].dtype
        logger.info(f"Executing broker column successfuly added to the valid entries for reporting. Executing broker column of dtype: {data_type}")
    except:
        logger.warning(f"Executing broker column not successfuly added to final valid report") 

    return valid_report


def add_internal(valid_report, valid_df):
    try:
        valid_report['Internal'] = valid_df['Broker_Name'].values
        valid_report['Internal'] = valid_report['Internal'] + " " + valid_report['Source'] 
        valid_report['Internal'].astype('string')
        data_type = valid_report['Internal'].dtype
        logger.info(f"Internal column successfully added to the valid entried for reporting. Internal column of dtype: {data_type}")
    except:
        logger.warning(f"Internal column not successfuly added to final valid report") 

    return valid_report


def add_clearing_firm(valid_report, valid_df):
    # add clearing firm
    try:
        valid_report['Clearing_Firm'] = valid_df['Counterparty_Name'].values
        valid_report['Clearing_Firm'] = valid_report['Clearing_Firm'].astype('string')
        data_type = valid_report['Clearing_Firm'].dtype
        logger.info(f"Clearing firm column successfully added to the valid entried for reporting. Clearing firm column of dtype: {data_type}")
    except:
        logger.warning(f"Clearing firm not successfuly added to final valid report") 

    return valid_report

def perform_all_composite_checks(validation_df, dir_path):
    # extract the name of the executing broker
    executing_broker = validation_df["executing_broker"][0] 

    # separate the datasets into the valid and invalid datasets for reporting.
    valid_df, invalid_df = separate_datasets(validation_df)

    # create the destination path for the valid and invalid entries
    # for creating the string to name the dir
    today = date.today()

    if (dir_path / f"valid_entries_{today}").is_dir():
        valid_dir_path = (dir_path / f"valid_entries_{today}" / f"valid_entries_{executing_broker}.xlsx")
    else:
        sys.exit("There is no destination in the provided directory for valid entries")

    if (dir_path / f"invalid_entries_{today}").is_dir():
        invalid_dir_path = (dir_path / f"invalid_entries_{today}" / f"invalid_entries_{executing_broker}.xlsx")
    else:
        sys.exit("There is no destination in the provided directory for invalid entries")

    # Format the valid dataset before sending for reporting
    valid_report = default_values(valid_df)
    valid_report = add_date(valid_report, valid_df)
    valid_report = add_account(valid_report, valid_df)
    valid_report = add_quantity(valid_report, valid_df)
    valid_report = add_trade_price(valid_report, valid_df)
    valid_report = add_identifier(valid_report, valid_df)
    valid_report = add_psid(valid_report, valid_df)
    valid_report = add_executing_broker(valid_report, valid_df)
    valid_report = add_internal(valid_report, valid_df)
    valid_report = add_clearing_firm(valid_report, valid_df)

    # export the reports as excel worksheets to be emailed
    with pd.ExcelWriter(valid_dir_path) as writer: 
        valid_report.to_excel(writer, sheet_name='valid_report', index=False)

    with pd.ExcelWriter(invalid_dir_path) as invalid_writer:
        invalid_df.to_excel(invalid_writer, sheet_name='invalid_report', index=False)


    return True






