import click
import pandas as pd
import os
import sys
from pathlib import Path
from .file_functions import file_ingestion, valid_dir
from .logger_setup import get_logger
from .validation_logic import *
from .composite_checks import *
from .helper_functions import *


logger = get_logger(__name__)

DEFAULT_PATH = "C:\\Users\\johnj\\OneDrive\\Documents\\programming\\projects\\polar_star\\broker_recap\\data\\broker_daily_recaps"

def get_path():
    while True:
        try:
            broker_report = input("What is your file path: ")
            broker_report = broker_report.replace("\\", "/")
            broker_report = Path(broker_report)

            # store all the files in the directory in a list to iterate over
            broker_report = [file for file in broker_report.iterdir() if file.is_file()]
            
            return broker_report
        except Exception as e:
            print(type(e))

def default_files():
    directory = DEFAULT_PATH
    directory = DEFAULT_PATH.replace("\\", "/")
    directory = Path(directory)
    
    # store all the files in the directory in a list to iterate over
    file_paths = [file for file in directory.iterdir() if file.is_file()]
    
    return file_paths
 

@click.command()
@click.option("--default", is_flag=True, help="use the default file path for the broker recap reports")
@click.option("--custom", is_flag=True, help="select a different file path for the broker recap reports")
def validate_report(default, custom):
    """ingest the daily broker recap and perform the validations"""
    if default:
        broker_report = default_files()
    elif custom:
        broker_report = get_path()
    else:
        valid_dir(DEFAULT_PATH)
        sys.exit("Must select an option for the broker recap file path")

    for file in broker_report:
        if not os.path.exists(file):
            raise FileNotFoundError("Please ensure that you are providing a path to an existing broker report")
        else:
            try:
                broker_report = os.path.abspath(file)
                click.echo("the broker report has been successfully ingested and ready for validation")
                # replace this with a different call which performs all the logic
                data_sets = file_ingestion(broker_report)
                
                if data_sets != None:
                    logger.info("Data sets have been converted into pandas dataframes")
                    recap_df, broker_df, contract_df, valid_acct_df = data_sets
                    recap_df = invalid_data(recap_df)
                    validation_df = perform_all_validations(recap_df, broker_df, contract_df, valid_acct_df)
                    perform_all_composite_checks(validation_df)

                    body_string = "This is a test to send an email with attachments for reporting. SSL used for the SMTP server connection."
                    send_email('data/output.xlsx', 'logs/validation_log_main.log', body_string)
                else:
                    logger.warning("the required data has not been properly converted into pandas dataframes")
                    
            except Exception as e:
                click.echo(e)


