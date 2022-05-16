import sys

import click
from reprosyn.methods.mbi.mst import mstmain


@click.command("mst", short_help="NIST-winning MST")
@click.option(
    "--file",
    type=click.File("rt"),
    help="filepath to dataset or STDIN",
    default=sys.stdin,
)
@click.option(
    "--out",
    help="filepath to write output to, omit for STDOUT",
    type=click.File("at"),
    default=sys.stdout,
)
# @click.option("--degree", type=int, default=2, help="degree of marginals in workload")
# @click.option(
#     "--max_cells",
#     type=int,
#     default=10000,
#     help="maximum number of cells for marginals in workload",
# )
# @click.option(
#     "--epsilon",
#     type=float,
#     default=1.0,
#     help="privacy parameter",
# )
def mst(file, out):
    """Runs MST on --file

    Usage

    rsyn mst --file census.csv \n
    rsyn mst < census.csv
    """

    if not file.isatty():
        output = mstmain(dataset=file)
        click.echo(output.df, file=out)
    else:
        mst.main(["--help"])


if __name__ == "__main__":
    mst()
