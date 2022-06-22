import click
import json
from reprosyn.methods.mbi.mst import mstmain


@click.command(
    "mst",
    short_help="NIST-winning MST",
    options_metavar="[GENERATOR OPTIONS]",
)
# @click.option("--degree", type=int, default=2, help="degree of marginals in workload")
# @click.option(
#     "--max_cells",
#     type=int,
#     default=10000,
#     help="maximum number of cells for marginals in workload",
# )
@click.option(
    "--epsilon",
    type=float,
    default=1.0,
    help="privacy parameter",
)
@click.pass_obj
@click.pass_context
def mstcommand(ctx, obj, epsilon):
    """Runs MST on --file or STDIN

    See rsyn --help for general use.

    Examples:

    rsyn --file census.csv mst  \n
    rsyn mst < census.csv
    """
    # all methods will need the config generation so this should be moved to a global method.
    if obj.generateconfig:
        if obj.config != "-":
            obj.set_config_path("mst")
        with click.open_file(obj.config, "w") as outfile:
            click.echo(f"Saving to config file to {obj.config}")
            json.dump(ctx.params, outfile)
    else:
        if not obj.file.isatty():
            output = mstmain(dataset=obj.file, size=obj.size)
            click.echo(output.df, file=obj.out)
        else:
            print("here")
            mstcommand.main(["--help"])


if __name__ == "__main__":
    mstcommand()
