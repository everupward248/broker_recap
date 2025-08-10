import click
import pandas as pd
import os
import sys
from pathlib import Path
from .file_functions import file_ingestion, valid_dir, invalid_dir
from .logger_setup import get_logger
from .validation_logic import *
from .composite_checks import *
from .helper_functions import *


logger = get_logger(__name__)

DEFAULT_PATH = "C:\\Users\\johnj\\OneDrive\\Documents\\programming\\projects\\polar_star\\broker_recap\\data\\broker_daily_recaps"

def get_path():
    while True:
        try:
            broker_report = input("What is your file path: ").strip()
            broker_report = broker_report.replace("\\", "/")
            broker_report = Path(broker_report)
            valid_dir(broker_report)
            invalid_dir(broker_report)
            dir_path = broker_report

            # store all the files in the directory in a list to iterate over
            broker_report = [file for file in broker_report.iterdir() if file.is_file()]
            
            return broker_report, dir_path
        except Exception as e:
            print(type(e))
            

def default_files():
    directory = DEFAULT_PATH
    directory = DEFAULT_PATH.replace("\\", "/")
    directory = Path(directory)
    valid_dir(directory)
    invalid_dir(directory)
    dir_path = directory

    
    # store all the files in the directory in a list to iterate over
    file_paths = [file for file in directory.iterdir() if file.is_file()]
    
    return file_paths, dir_path
 

@click.command()
@click.option("--default", is_flag=True, help="use the default file path for the broker recap reports")
@click.option("--custom", is_flag=True, help="select a different file path for the broker recap reports")
def validate_report(default, custom):
    """ingest the daily broker recap and perform the validations"""
    if default:
        broker_report, dir_path = default_files()
    elif custom:
        broker_report, dir_path = get_path()
    else:
        sys.exit("Must select an option for the broker recap file path")

    for file in broker_report:
        if not os.path.exists(file):
            raise FileNotFoundError("Please ensure that you are providing a path to an existing broker report")
        else:
            try:
                broker_report = os.path.abspath(file)
                data_sets = file_ingestion(broker_report)
                click.echo("the broker report has been successfully ingested and ready for validation")
                
                if data_sets != None:
                    logger.info("Data sets have been converted into pandas dataframes")
                    recap_df, broker_df, contract_df, valid_acct_df = data_sets
                    exec_broker = recap_df["executing_broker"][0]
                    print(f"now performing the data validation for broker: {exec_broker}\n")
                    recap_df = invalid_data(recap_df)
                    validation_df = perform_all_validations(recap_df, broker_df, contract_df, valid_acct_df)
                    perform_all_composite_checks(validation_df, dir_path)

                    body_string = "This is a test to send an email with attachments for reporting. SSL used for the SMTP server connection."
                    # send_email('data/output.xlsx', 'logs/validation_log_main.log', body_string)
                else:
                    logger.warning("the required data has not been properly converted into pandas dataframes")
                    
            except Exception as e:
                click.echo(e)

# consolidate all valid reports
@click.command
@click.option("--default", is_flag=True, help="use the default file path")
@click.option("--custom", is_flag=True, help="select a different file path")
def consolidate_valid(default, custom):
    """consolidates all reports in a specified directory"""
    if default:
        directory = DEFAULT_PATH
        directory = DEFAULT_PATH.replace("\\", "/")
        directory = Path(directory)

    elif custom:
        try:
            while True:
                directory = input("What is your file path: ").strip()
                directory = directory.replace("\\", "/")
                directory = Path(directory)

                if not directory.is_dir():
                    click.echo("Path provided is not a directory. Please provide a valid directory.\n")
                    continue
                else:
                    break
        except Exception as e:
            print(e)
    else:
        sys.exit("Must provide an option. Plese use '--help' to view options\n")

    # TODO: now that the directory is established, add the logic for consolidating all xlxs files in the dir into one valid report
    

