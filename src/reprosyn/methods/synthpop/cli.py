import click

from reprosyn.generator import wrap_generator
from reprosyn.methods.synthpop.synthpop import SYNTHPOP


# Only a subset of parameters are available since currently you cannot pass lists/tuples on the command line.


@click.command(
    "synthpop",
    short_help="Synthpop",
    options_metavar="[GENERATOR OPTIONS]",
)
@click.option(
    "--seed",
    type=int,
    default=1e-9,
    help="random seed",
)
@wrap_generator
def cmd_spop(h, **kwargs):
    """Runs SynthPop on --file or STDIN

    See rsyn --help for general use.

    Examples:

    $ rsyn --file census.csv mst
    $ rsyn synthpop < census.csv
    """
    generator = SYNTHPOP(
        dataset=h.file,
        metadata=h.metadata,
        size=h.size,
        output_dir=h.out,
        **kwargs
    )
    generator.run()
    return generator.output
