import click

from reprosyn.cli_utils import wrap_generator
from reprosyn.methods.gans.gans import CTGAN, PATEGAN


@click.command(
    "ctgan",
    short_help="Conditional Tabular GAN",
    options_metavar="[GENERATOR OPTIONS]",
)
@click.option(
    "--embedding_dim",
    type=int,
    default=128,
    help="Size of the random sample passed to the Generator. Defaults to 128",
)
@click.option(
    "--gen_dim",
    multiple=True,
    type=int,
    default=(256, 256),
    help="Size of the output samples for each one of the Residuals. Defaults to (256, 256)",
)
@click.option(
    "--dis_dim",
    multiple=True,
    type=int,
    default=(256, 256),
    help="Size of the output samples for each one of the Discriminator Layers. Defaults to (256, 256).",
)
@click.option(
    "--l2scale",
    type=float,
    default=1e-6,
    help="Weight Decay for the Adam Optimizer. Defaults to 1e-6",
)
@click.option(
    "--batch_size",
    type=int,
    default=500,
    help="Number of data samples to process in each step.",
)
@click.option(
    "--epochs",
    type=int,
    default=300,
    help="Number of iterations",
)
@wrap_generator
def cmd_ctgan(ctx, **kwargs):
    """Runs ctgan on --dataset or STDIN

    See rsyn ctgan --help.
    """
    generator = CTGAN(**ctx.parent.params, **kwargs)
    generator.run()
    return generator.output


# --------------------------------------------------------------------
@click.command(
    "pategan",
    short_help="PATEGAN...",
    options_metavar="[GENERATOR OPTIONS]",
)
@click.option(
    "--epsilon",
    type=float,
    default=1.0,
    help="Privacy parameter",
)
@click.option(
    "--delta",
    type=float,
    default=1e-5,
)
@click.option(
    "--num_teachers",
    type=int,
    default=10,
)
@click.option(
    "--n_iters",
    type=int,
    default=100,
)
@click.option(
    "--batch_size",
    type=int,
    default=128,
)
@click.option(
    "--learning_rate",
    type=float,
    default=1e-4,
)
@wrap_generator
def cmd_pategan(ctx, **kwargs):

    generator = PATEGAN(**ctx.parent.params, **kwargs)
    generator.run()
    return generator.output
