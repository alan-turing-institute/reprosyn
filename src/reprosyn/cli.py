import click
import sys

from reprosyn.methods.mbi.cli import mstcommand


class Dataset(object):
    def __init__(self, file=None, out=None, size=None):
        self.file = file
        self.out = out
        self.size = size


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
@click.pass_context
def main(ctx, file, out, size):
    """ "A cli tool synthesising the 1% census"

    Usage: rsyn <global options> <generator> <generator options>

    If --file/STDIN not given, help is printed.

    Examples: \n

    rsyn --file census.csv mst \n
    census.csv > rsyn mst
    """
    ctx.obj = Dataset(file, out, size)
    # print(f"Executing generator {ctx.invoked_subcommand}")


main.add_command(mstcommand)

if __name__ == "__main__":
    main()
