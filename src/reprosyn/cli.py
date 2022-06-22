import click
import sys
from os import path, getcwd
from datetime import datetime

from reprosyn.methods.mbi.cli import mstcommand

# Helper class for manipulating options across reprosyn


class Generator(object):
    def __init__(
        self,
        file=None,
        out=None,
        size=None,
        generateconfig=None,
        config=None,
        configfolder=None,
    ):
        self.file = file
        self.out = out
        self.size = size
        self.generateconfig = generateconfig
        self.config = config
        self.configfolder = configfolder

    def set_config_path(self, method):
        self.config = path.join(
            self.configfolder,
            f"mst_{self.config}",
        )


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
    help="filepath to write output to, omit for STDOUT",
    type=click.File("at"),
    default=sys.stdout,
)
@click.option(
    "--size",
    type=int,
    help="number of rows to synthesise",
)
@click.option(
    "--generateconfig",
    is_flag=True,
    help="generate input json",
)
@click.option(
    "--config",
    type=click.Path(),
    default="-",
    help="path to config file. If --generateconfig, config file is saved here",
)
@click.option(
    "--configfolder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=path.join(path.dirname(path.realpath(__file__)), "methods/config/"),
    help="directory for method configs",
)
@click.pass_context
def main(ctx, file, out, size, generateconfig, config, configfolder):
    """ "A cli tool synthesising the 1% census"

    Usage: rsyn <global options> <generator> <generator options>

    If --file/STDIN not given, help is printed.

    Examples: \n

    rsyn --file census.csv mst \n
    census.csv > rsyn mst
    """

    ctx.obj = Generator(
        file,
        out,
        size,
        generateconfig,
        config,
        configfolder,
    )

    # print(f"Executing generator {ctx.invoked_subcommand}")


main.add_command(mstcommand)

if __name__ == "__main__":
    main()
