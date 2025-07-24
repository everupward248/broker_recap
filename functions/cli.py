import click
import pandas as pd
import os
import sys

@click.command()
@click.argument("broker-report")
def validate_report(broker_report: str) -> pd.DataFrame:
    # take the file path as an argument and then perform the validations
    # type hint the input type which should be an excel file
    """ingest the daily broker recap and perform the validations"""
    
    if not os.path.exists(broker_report):
        raise FileExistsError("Please ensure that you are providing a path to an existing broker report")
    else:
        try:
            broker_report = os.path.abspath(broker_report)
            recap_df = pd.read_excel(broker_report)
            return recap_df
        except Exception as e:
            sys.exit(e)
