import click

from reprosyn.cli_utils import wrap_generator
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
def cmd_spop(ctx, **kwargs):
    """Runs SynthPop on --dataset or STDIN

    See rsyn synthpop --help for general use.
    """
    generator = SYNTHPOP(**ctx.parent.params, **kwargs)
    generator.run()
    return generator.output
