from functions.logger_setup import get_logger
from functions import cli_args
import click

logger = get_logger(__name__)

@click.group(help="Validate entries in the broker recaps and create email drafts to brokers for their invalid entries")
def cli() -> None:
    print("\ncli is intiated...")
    print("This app is used to validate broker recaps and to create email drafts to relevant broker for invalid entries\n")

cli.add_command(cli_args.validate_report)
cli.add_command(cli_args.consolidate_valid)
cli.add_command(cli_args.email_draft)

def main():
    cli()

if __name__ == '__main__':
    main()










