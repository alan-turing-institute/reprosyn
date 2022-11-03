import click

from reprosyn.cli_utils import wrap_generator
from reprosyn.methods.mbi.mst import MST
from reprosyn.methods.mbi.privbayes import PRIVBAYES


@click.command(
    "mst",
    short_help="NIST-winning MST",
    options_metavar="[GENERATOR OPTIONS]",
)
@click.option(
    "--epsilon",
    type=float,
    default=1.0,
    help="privacy parameter epsilon",
)
@click.option(
    "--delta",
    type=float,
    default=1e-9,
    help="privacy parameter delta",
)
@click.option(
    "--degree",
    type=int,
    default=2,
    help="degree of marginals in workload",
)
# @click.option(
#     "--num_marginals",
#     type=int,
#     default=None,
#     help="number of marginals in workload",
# )
# @click.option(
#     "--max_cells",
#     type=int,
#     default=10000,
#     help="maximum number of cells for marginals in workload",
# )
@wrap_generator
def cmd_mst(ctx, **kwargs):
    """Runs MST on --dataset or STDIN

    See rsyn mst --help for general use.

    Examples:

    $ rsyn --dataset census.csv mst
    $ rsyn mst < census.csv
    """
    generator = MST(**ctx.parent.params, **kwargs)
    generator.run()
    return generator.output


# --------------------------------------------------------------------------


@click.command(
    "privbayes",
    short_help="Uses DP Bayesian networks",
    options_metavar="[GENERATOR OPTIONS]",
)
@click.option(
    "--epsilon",
    type=float,
    default=1.0,
    help="privacy parameter epsilon",
)
@click.option(
    "--seed",
    type=int,
    default=1e-9,
    help="random seed",
)
@wrap_generator
def cmd_pb(ctx, **kwargs):
    """Runs PrivBayes on --dataset or STDIN

    See rsyn privbayes --help for general use.

    Examples:

    $ rsyn --dataset census.csv mst
    $ rsyn privbayes < census.csv
    """
    generator = PRIVBAYES(**ctx.parent.params, **kwargs)
    generator.run()
    return generator.output
