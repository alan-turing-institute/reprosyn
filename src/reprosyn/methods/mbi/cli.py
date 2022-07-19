import click
import json
from reprosyn.methods.mbi.mst import mstmain

# params = {}
# params["dataset"] = "../data/adult.csv"
# params["domain"] = "../data/adult-domain.json"
# params["epsilon"] = 1.0
# params["delta"] = 1e-9
# params["degree"] = 2
# params["num_marginals"] = None
# params["max_cells"] = 10000


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
@click.pass_obj
def mstcommand(sdg, **kwargs):
    """Runs MST on --file or STDIN

    See rsyn --help for general use.

    Examples:

    rsyn --file census.csv mst  \n
    rsyn mst < census.csv
    """

    if sdg.generateconfig:
        p = sdg.get_config_path()
        with click.open_file(p, "w") as outfile:
            # click.echo(f"Saving to config file to {p}")
            json.dump(kwargs, outfile)
    else:
        if not sdg.file.isatty():
            output = mstmain(dataset=sdg.file, size=sdg.size, args=kwargs)
            click.echo(output.df.to_csv(None, index=False), file=sdg.out)
        else:
            click.echo("Please give a dataset using --file or STDIN")
            mstcommand.main(["--help"])


if __name__ == "__main__":
    mstcommand()
