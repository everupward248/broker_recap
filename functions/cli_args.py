import click
import pandas as pd
import os
import sys

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
            recap_df = pd.read_excel(broker_report)
            click.echo("the broker report has been successfully ingested and ready for validation")
            return recap_df
        except Exception as e:
            print(e)


# add the rest of the logic for validating the report in this function as it will need to be executed from within
# the click command based on how click handles return values