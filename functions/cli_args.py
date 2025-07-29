import click
import pandas as pd
import os
from .import_files import file_ingestion
from .logger_setup import get_logger
from .validation_logic import *
from .composite_checks import *
from .helper_functions import *


logger = get_logger(__name__)

def get_path() -> str:
    while True:
        try:
            broker_report = input("What is your file path: ")
            return broker_report
        except Exception as e:
            print(type(e))
 
@click.command()
def validate_report():
    """ingest the daily broker recap and perform the validations"""
    broker_report = get_path()
    broker_report = broker_report.replace("\\", "/")

    if not os.path.exists(broker_report):
        raise FileNotFoundError("Please ensure that you are providing a path to an existing broker report")
    else:
        try:
            broker_report = os.path.abspath(broker_report)
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


