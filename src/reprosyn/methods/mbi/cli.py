import click
import json
from reprosyn.methods.mbi.mst import MST
from reprosyn.generator import wrap_generator
from reprosyn import run


@click.command(
    "mst",
    short_help="NIST-winning MST",
    options_metavar="[GENERATOR OPTIONS]",
)
@click.option(
    "--domain",
    type=click.File(),
    default=None,
    help="domain to use, default to get_domain_dict()",
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
def mstcommand(h, **kwargs):
    """Runs MST on --file or STDIN

    See rsyn --help for general use.

    Examples:

    rsyn --file census.csv mst  \n
    rsyn mst < census.csv
    """
    print(h.file)
    generator = run(MST, dataset=h.file, size=h.size, output_dir=h.out, **kwargs)
    return generator.output


if __name__ == "__main__":
    mstcommand()
