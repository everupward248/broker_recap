import pandas as pd
from .logger_setup import get_logger

logger = get_logger(__name__)


def file_ingestion(recap_df):
    """Takes the provided file path and creates dataframes for all the required data"""
    try:
            # create the dataframes from the recap and validation data
            recap_df = pd.read_excel('data/recap.xlsx')
            broker_df = pd.read_excel('data/broker_codes.xlsx')
            contract_df = pd.read_excel('data/contract_codes.xlsx')
            valid_acct_df = pd.read_excel('data/valid_accounts.xlsx')

            # success message
            logger.info(f"files read successfully")
            
            return recap_df, broker_df, contract_df, valid_acct_df

    except Exception as e:
            logger.warning(f"An unexpected error occured: {e}") 