import click

from reprosyn.cli_utils import wrap_generator
from reprosyn.methods.ipf.ipf import IPF


@click.command(
    "ipf",
    short_help="Iterative proportional fitting",
    options_metavar="[GENERATOR OPTIONS]",
)
# TODO: Add marginals as a click.unprocessed option
@wrap_generator
def cmd_ipf(ctx, **params):
    """Runs IPF on --dataset or STDIN

    See rsyn --help for general use.

    Examples:

    rsyn --dataset census.csv mst  \n
    rsyn ipf < census.csv
    """

    generator = IPF(**ctx.parent.params, **params)
    generator.run()
    return generator.output


if __name__ == "__main__":
    cmd_ipf()
