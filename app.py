import click
import errno
import os

from sys import exit
from rich.console import Console
from rich.prompt import Confirm, Prompt
from dotenv import load_dotenv, dotenv_values

from lib.api.auth import ApiAuth
from lib.api.getlist import ElementOfTenant
from lib.filehandler import SaveAsExcel
from lib.helper import split_list, split_task_with_progress


console = Console()
errConsole = Console(stderr=True, style="bold red")


@click.group()
def main():
    """
    PANBA-Cli Version, For now it is only utilize for one or Special Needs
    """
    os.system("cls" if os.name == "nt" else "clear")
    pass


@click.command()
@click.option(
    "-t",
    "--thread-count",
    help="Number of thread use for this program to run",
    type=int,
    default=os.cpu_count(),
)
@click.option(
    "-e", "--env-file", help="Provide your own ENV file", type=str, default="./.env"
)
@click.option(
    "-o",
    "--output",
    type=str,
    help="Output file address",
    default="./output/elementOfTenant.xlsx",
)
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Run program verbosely"
)
def get_element(thread_count: int, env_file: str, output: str, verbose: bool):
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
    console.log(controller) if verbose else None

    with console.status("Loging In...", spinner="monkey") as status:
        try:
            auth = ApiAuth(
                userName=controller["env"]["USER_NAME"],
                secret=controller["env"]["SECRET_STRING"],
                tsgId=controller["env"]["TSG_ID"],
                verbose=verbose,
            )
        except Exception as err:
            errConsole.log(err)
            exit(1)
        controller["bearerToken"] = auth.bearerToken
        status.update("Getting Element of Tenant...")
        elementOfTenant: list = ElementOfTenant(
            bearerToken=controller["bearerToken"]
        ).data["items"]
        if verbose:
            console.print(f"Number of Tenant: {elementOfTenant.count()}")
        splitEOT = split_list(elementOfTenant, thread_count)
        if verbose:
            for i in len(splitEOT):
                console.print(f"splitEOT[{i}] Count: {len(splitEOT[i])}")

    res = split_task_with_progress(data=splitEOT, env=controller)
    if res["err"] is not None:
        errConsole.log("[bold red]ERROR! [/]", res["err"], sep="\n")
    with console.status("Saving file ...", spinner="monkey") as status:
        saves = SaveAsExcel(data=res["res"], output=output)
        console.print("[blue]Saved File [/]", saves)


# TODO: Add push-interface-changes Command


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
