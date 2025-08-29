import pandas as pd
from broker_recap_package.functions.logger_setup import get_logger
from pathlib import Path
from datetime import date
import sys
from pathlib import Path


logger = get_logger(__name__)

# set default data path so that program can be executed as script and as package
DATA_PATH = Path(r"C:\Users\johnj\OneDrive\Documents\programming\projects\polar_star\broker_recap\broker_recap_package\data")

def file_ingestion(broker_report):
    """Takes the provided file path and creates dataframes for all the required data"""
    try:
            # create the dataframes from the recap and validation data
            recap_df = pd.read_excel(broker_report)
            broker_df = pd.read_excel(DATA_PATH / 'broker_codes.xlsx')
            contract_df = pd.read_excel(DATA_PATH / 'contract_codes.xlsx')
            valid_acct_df = pd.read_excel(DATA_PATH / 'valid_accounts.xlsx')

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
                       print("\ndirectory for valid entries successfuly created\n")
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
                       print("directory for invalid entries successfuly created\n")
                except FileExistsError as e:
                       print(e)


# concatination of valid_broker_reports into one file
def concat_valid_reports(directory: Path) -> None:
    """
    logic for consolidating all xlxs files in the dir into one valid report using pandas.concat()
    """
    # construct list of all valid_reports in the provided path
    today = date.today()
    valid_entries = directory / f"valid_entries_{today}"

    try:
        valid_reports = [file for file in valid_entries.iterdir() if file.is_file()]
    except Exception as e:
           logger.warning(e)
           print(e)
    
    try:
        # only files which end in the "xlsx" extension will be consolidated
        df_list = [pd.read_excel(report) for report in valid_reports if str(report).endswith("xlsx")]
    except Exception as e:
           logger.warning(e)
           print(e)
           
    final_df = pd.concat(df_list, ignore_index=True)
    final_df.to_excel(valid_entries / f"valid_broker_report_{today}.xlsx", index=False)
    logger.info("Valid entries for the day have been consolidated into one report")
    print("Valid entries for the day have been consolidated into one report")

# provides the directory for the invalid entries to be passed as attachements into the email drafts
def invalid_directory_for_email(directory: Path) -> list[Path]:
       """
       Takes the path of where the invalid broker reports are stored and then returns a list of path objects that can be iterated over when constructing the email drafts
       """
       today = date.today()
       invalid_entries = directory / f"invalid_entries_{today}"

       try: 
        invalid_reports = [file for file in invalid_entries.iterdir() if file.is_file()]
       except FileNotFoundError:
              logger.warning("Please ensure that the validations have been run for the day as the program cannot find the ivnalid entries made for the day")
              sys.exit("Please ensure that the validations have been run for the day as the program cannot find the ivnalid entries made for the day")
       logger.info(f"Invalid entries have been compiled into a list for iteration at the provided path: {directory}")
       return invalid_reports



               



