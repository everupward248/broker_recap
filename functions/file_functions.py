import pandas as pd
from .logger_setup import get_logger
from pathlib import Path
from datetime import date
import sys


logger = get_logger(__name__)


def file_ingestion(broker_report):
    """Takes the provided file path and creates dataframes for all the required data"""
    try:
            # create the dataframes from the recap and validation data
            recap_df = pd.read_excel(broker_report)
            broker_df = pd.read_excel('data/broker_codes.xlsx')
            contract_df = pd.read_excel('data/contract_codes.xlsx')
            valid_acct_df = pd.read_excel('data/valid_accounts.xlsx')

            logger.info(f"files read successfully")
            
            return recap_df, broker_df, contract_df, valid_acct_df

    except Exception as e:
            logger.warning(f"An unexpected error occured: {e}") 


# all valid entries across brokers need to be consolidated, create the valid dir if it does not exist
def valid_dir(path):
        """Takes the file path for the broker recaps and creates a directory for valid entry consolidation if does not exist already"""
        path = Path(path)

        # for creating the string to name the dir
        today = date.today()

        if (path / f"valid_entries_{today}").is_dir():
                print("valid dir exists\n")
        else:
                try:
                       valid_entries = Path(path / f"valid_entries_{today}")
                       valid_entries.mkdir()
                       print("directory for valid entries successfuly created\n")
                except FileExistsError as e:
                       print(e)
                       

# the broker recaps are on a per broker basis and therefore separate directories need to be created for each broker's invalid entries
def invalid_dir(path):
        """Takes the file path for the broker recaps and creates a directory for all invalid entries per broker if does not exist already"""
        path = Path(path)

        # for creating the string to name the dir
        today = date.today()

        if (path / f"invalid_entries_{today}").is_dir():
                print("invalid dir exists\n")
        else:
                try:
                       invalid_entries = Path(path / f"invalid_entries_{today}")
                       invalid_entries.mkdir()
                       print("directory for valid entries successfuly created\n")
                except FileExistsError as e:
                       print(e)
                       