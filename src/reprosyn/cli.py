"""The main `click` command, providing a CLI."""

import json
import sys
from io import StringIO
from os import path

import click

from reprosyn.generator import Handler
from reprosyn.methods.ipf.cli import ipfcommand
from reprosyn.methods.mbi.cli import mstcommand, pbcommand
from reprosyn.methods.ctgan.cli import ctgancommand


@click.group(
    options_metavar="[GLOBAL OPTIONS]",
    subcommand_metavar="[GENERATOR]",
)
@click.option(
    "--file",
    type=click.File("rt"),
    help="[REQUIRED] filepath to dataset or STDIN",
    default=sys.stdin,
)
@click.option(
    "--out",
    help="filepath to write output to",
    type=click.Path(),
    default=".",
)
@click.option(
    "--size",
    type=int,
    help="number of rows to synthesise",
)
@click.option(
    "--generateconfig",
    is_flag=True,
    help="flag to generate input json",
)
@click.option(
    "--configpath",
    type=click.Path(),
    default="-",
    help="path to config file. If --generateconfig, config file is saved here",
)
@click.option(
    "--configstring",
    type=click.STRING,
    default="{}",
    help="configuration string as a dictionary. Overrided by --configpath",
)
@click.option(
    "--configfolder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=path.join(
        path.dirname(path.realpath(__file__)), "methods/config/"
    ),
    help="directory for method configs",
)
@click.option(
    "--metadata",
    type=click.File(),
    default=None,
    help="domain to use, in privacy toolbox format, defaults to census",
)
@click.pass_context
def main(ctx, **kwargs):
    """ "A cli tool synthesising the 1% census"

    Usage: rsyn <global options> <generator> <generator options>

    If --file/STDIN not given, help is printed.

    Examples: \n

    rsyn --file census.csv mst \n
    census.csv > rsyn mst
    """

    ctx.obj = Handler(**kwargs)

    if path.exists(ctx.obj.get_config_path()):
        if ctx.obj.generateconfig:
            click.confirm(
                f"Config file exists at {ctx.obj.get_config_path()},"
                " override?",
                abort=True,
            )
        with click.open_file(ctx.obj.get_config_path(), "r") as f:
            config_params = json.load(f)
    else:
        config_params = json.load(
            StringIO(ctx.obj.configstring)
        )  # if nothing given with not update

    ctx.default_map = {ctx.invoked_subcommand: config_params}
    # print(f"Executing generator {ctx.invoked_subcommand}")


main.add_command(mstcommand)
main.add_command(pbcommand)
main.add_command(ipfcommand)
main.add_command(ctgancommand)

if __name__ == "__main__":
    main()
