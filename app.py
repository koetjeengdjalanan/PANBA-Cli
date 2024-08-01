import click
import errno
import os

from sys import exit
from rich.console import Console
from rich.prompt import Confirm, Prompt
from dotenv import load_dotenv, dotenv_values

from lib.api.auth import ApiAuth
from lib.api.getlist import ElementOfTenant


console = Console()
errConsole = Console(stderr=True, style="bold red")


@click.group()
def main():
    """
    PANBA-Cli Version, For now it is only utilize for one or Special Needs
    """
    pass


@click.command()
# @click.argument("get-element")
@click.option(
    "-e", "--env-file", help="Provide your own ENV file", type=str, default="./.env"
)
@click.option(
    "-o",
    "--output",
    type=str,
    help="Output file address",
    default="./output/elementOfTenant.xls",
)
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Run program verbosely"
)
def get_element(env_file, output, verbose):
    """
    Get Element of all the tenant
    """
    controller: dict = {}
    try:
        if not load_dotenv(env_file) and env_file is not None:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), env_file)
    except FileNotFoundError as err:
        errConsole.log(err)
        exit(errno.ENOENT)
    envFile = env_file
    if load_dotenv(envFile) and Confirm.ask(
        prompt="Environment Variables Detected, Use?",
        default=True,
        show_default=True,
    ):
        controller["env"] = dict(dotenv_values(envFile, verbose=True))
    else:
        controller["env"] = getCred()
    console.log(controller, output) if verbose else None

    with console.status("Loging In...", spinner="monkey"):
        try:
            auth = ApiAuth(
                userName=controller["env"]["USER_NAME"],
                secret=controller["env"]["SECRET_STRING"],
                tsgId=controller["env"]["TSG_ID"],
                verbose=verbose,
            )
        except Exception as err:
            errConsole.log(err)
    controller["bearerToken"] = auth.bearerToken

    with console.status("Getting Element...", spinner="monkey"):
        elementOfTenant = ElementOfTenant(bearerToken=controller["bearerToken"]).data[
            "items"
        ]
    console.log(elementOfTenant[:3])


def getCred() -> dict:
    userName = Prompt.ask("Username")
    secret = Prompt.ask("Secret String")
    tsg = Prompt.ask("TSG Number")
    return {
        "USER_NAME": userName,
        "SECRET_STRING": secret,
        "TSG_ID": tsg,
    }


main.add_command(get_element)

if __name__ == "__main__":
    main()