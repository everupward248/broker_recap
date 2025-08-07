import pandas as pd
import numpy as np
from functions import helper_functions as func
import datetime as dt
from functions.logger_setup import get_logger
from pandas.api.types import is_numeric_dtype, is_number
from functions import validation_logic as vl
from functions import composite_checks as cc
from functions import cli_args
import click

logger = get_logger(__name__)

@click.group()
def cli() -> None:
    print("cli is intiated...")
    print("This app is used to validate broker recaps and to create email drafts to relevant broker for invalid entries")

cli.add_command(cli_args.validate_report)

def main():
    cli()

if __name__ == '__main__':
    main()










