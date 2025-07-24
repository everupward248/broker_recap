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
            sys.exit(e)
        except EOFError:
            sys.exit("script exited")

@click.command()
def validate_report() -> pd.DataFrame:
    # take the file path as an argument and then perform the validations
    # type hint the input type which should be an excel file
    """ingest the daily broker recap and perform the validations"""
    broker_report = get_path()
    broker_report = broker_report.replace("\\", "/")
    print(broker_report)

    if not os.path.exists(broker_report):
        raise FileNotFoundError("Please ensure that you are providing a path to an existing broker report")
    else:
        try:
            broker_report = os.path.abspath(broker_report)
            recap_df = pd.read_excel(broker_report)
            click.echo("the broker report has been successfully ingested and ready for validation")
            return recap_df
        except Exception as e:
            sys.exit(e)


