import click
import pandas as pd
import os
import sys
from pathlib import Path
from broker_recap_package.functions.file_functions import file_ingestion, valid_dir, invalid_dir, concat_valid_reports, invalid_directory_for_email
from broker_recap_package.functions.logger_setup import get_logger
from broker_recap_package.functions.validation_logic import *
from broker_recap_package.functions.composite_checks import *
from broker_recap_package.functions.helper_functions import *
from broker_recap_package.functions.email_functions import test_email, create_email_draft, obtain_email_address


logger = get_logger(__name__)

DEFAULT_PATH = "C:\\Users\\johnj\\OneDrive\\Documents\\programming\\projects\\polar_star\\broker_recap\\broker_recap_package\\data\\broker_daily_recaps"

def get_path():
    while True:
        try:
            broker_report = input("What is your file path: ").strip()
            broker_report = broker_report.replace("\\", "/")
            broker_report = Path(broker_report)

            if not broker_report.is_dir():
                click.echo("Path provided is not a directory. Please provide a valid directory.\n")
                continue
            # this check is necessary as Path("") returns the current directory "."
            elif str(broker_report) == ".":
                click.echo("Path provided is not a directory. Please provide a valid directory.\n")
                continue

            valid_dir(broker_report)
            invalid_dir(broker_report)
            dir_path = broker_report

            # store all the files in the directory in a list to iterate over
            broker_report = [file for file in broker_report.iterdir() if file.is_file()]
            
            return broker_report, dir_path
        except FileNotFoundError:
            print("file not found\n")
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
        logger.info(f"Default file path chosen: {dir_path}")
    elif custom:
        broker_report, dir_path = get_path()
        logger.info(f"Custom file path provided: {dir_path}")
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
                    logger.info(f"Data sets have been converted into pandas dataframes: {file}")
                    recap_df, broker_df, contract_df, valid_acct_df = data_sets
                    exec_broker = recap_df["executing_broker"][0]
                    print(f"now performing the data validation for broker: {exec_broker}\n")
                    recap_df = invalid_data(recap_df)
                    validation_df = perform_all_validations(recap_df, broker_df, contract_df, valid_acct_df)
                    perform_all_composite_checks(validation_df, dir_path)

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
        logger.info(F"Default file path provided: {DEFAULT_PATH}")

        concat_valid_reports(directory)
    elif custom:
        try:
            while True:
                directory = input("What is your file path: ").strip()
                directory = directory.replace("\\", "/")
                directory = Path(directory)
                logger.info(F"Custom file path provided: {directory}")
                
                if not directory.is_dir():
                    click.echo("Path provided is not a directory. Please provide a valid directory.\n")
                    continue
                # this check is necessary as Path("") returns the current directory "."
                elif str(directory) == ".":
                    click.echo("Path provided is not a directory. Please provide a valid directory.\n")
                    continue
                else:
                    break
            concat_valid_reports(directory)
        except Exception as e:
            print(e)
    else:
        sys.exit("Must provide an option. Plese use '--help' to view options\n")


# creates email drafts for all invalid reports
@click.command
@click.option("--default", is_flag=True, help="use the default file path")
@click.option("--custom", is_flag=True, help="select a different file path")
@click.option("--test", is_flag=True, help="create a test email draft to ensure proper functioning")
def email_draft(default, custom, test):
    """
    creates email drafts per broker for all invalid broker reports
    """
    if test:
        try:
            while True:
                attachment = input("Please provide the excel attachment: ").strip()
                attachment = attachment.replace("\\", "/")
                attachment = Path(attachment)
                logger.info(f"Excel attachment provided: {attachment}")

                if not attachment.is_file():
                    click.echo("Please provide a valid excel file\n")
                    continue
                else:
                    break 
            test_email(attachment)    
        except EOFError:
            sys.exit("Program exited...")

    elif default:
        directory = DEFAULT_PATH
        directory = DEFAULT_PATH.replace("\\", "/")
        directory = Path(directory)
        logger.info(F"Default file path provided: {DEFAULT_PATH}")
        invalid_broker_file_path = invalid_directory_for_email(directory)
        
        for file in invalid_broker_file_path:
            recipient = obtain_email_address(file)
            body_string = "testing the default flag for email draft command"
            subject = "Invalid Entries Detected in Daily Recap"
            parameters = {"recipient": recipient, "subject": subject, "body": body_string, "attachments": file}
            create_email_draft(**parameters)

    elif custom:
        try:
            while True:
                directory = input("What is your file path: ").strip()
                directory = directory.replace("\\", "/")
                directory = Path(directory)
                logger.info(F"Custom file path provided: {directory}")
                
                if not directory.is_dir():
                    click.echo("Path provided is not a directory. Please provide a valid directory.\n")
                    continue
                # this check is necessary as Path("") returns the current directory "."
                elif str(directory) == ".":
                    click.echo("Path provided is not a directory. Please provide a valid directory.\n")
                    continue
                else:
                    break
            invalid_broker_file_path = invalid_directory_for_email(directory)
        
            for file in invalid_broker_file_path:
                recipient = obtain_email_address(file)
                body_string = "testing the default flag for email draft command"
                subject = "Invalid Entries Detected in Daily Recap"
                parameters = {"recipient": recipient, "subject": subject, "body": body_string, "attachments": file}
                create_email_draft(**parameters)
        except Exception as e:
            print(e)
    else:
        sys.exit("Must provide an option. Plese use '--help' to view options\n")