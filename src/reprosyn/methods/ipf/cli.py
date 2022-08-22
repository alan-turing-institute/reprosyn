import click
from reprosyn.methods.ipf.ipf import ipfmain
from reprosyn.generator import wrap_generator


@click.command(
    "ipf",
    short_help="Iterative proportional fitting",
    options_metavar="[GENERATOR OPTIONS]",
)
@wrap_generator
def ipfcommand(sdg, **kwargs):
    """Runs IPF on --file or STDIN

    See rsyn --help for general use.

    Examples:

    rsyn --file census.csv mst  \n
    rsyn ipf < census.csv
    """
    output = ipfmain(data=sdg.file, size=sdg.size, args=kwargs)
    return output


if __name__ == "__main__":
    ipfcommand()
