import click

from reprosyn.generator import wrap_generator
from reprosyn.methods.ipf.ipf import IPF


@click.command(
    "ipf",
    short_help="Iterative proportional fitting",
    options_metavar="[GENERATOR OPTIONS]",
)
@wrap_generator
def cmd_ipf(h, **kwargs):
    """Runs IPF on --file or STDIN

    See rsyn --help for general use.

    Examples:

    rsyn --file census.csv mst  \n
    rsyn ipf < census.csv
    """
    generator = IPF(dataset=h.file, size=h.size, output_dr=h.out, **kwargs)
    generator.run()
    return generator.output


if __name__ == "__main__":
    ipfcmd()
