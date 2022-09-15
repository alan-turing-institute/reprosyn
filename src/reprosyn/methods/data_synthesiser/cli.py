import click

from reprosyn.generator import wrap_generator
from reprosyn.methods.data_synthesiser.wrapper import (
    DS_BAYNET,
    DS_INDHIST,
    DS_PRIVBAYES,
)

# ------------------------------------
@click.command(
    "baynet",
    short_help="Data Synthesiser Bayesian Networks",
    options_metavar="[GENERATOR OPTIONS]",
)
@click.option(
    "--histogram_bins",
    type=int,
    default=10,
    help="number of bins",
)
@click.option(
    "--degree",
    type=int,
    default=1,
)
@wrap_generator
def baynet(h, **kwargs):

    generator = DS_BAYNET(
        dataset=h.file, size=h.size, output_dr=h.out, **kwargs
    )
    generator.run()
    return generator.output


# ------------------------------------
@click.command(
    "indhist",
    short_help="Data Synthesiser Independent Histograms",
    options_metavar="[GENERATOR OPTIONS]",
)
@click.option(
    "--histogram_bins",
    type=int,
    default=10,
    help="number of bins",
)
def indhist(h, **kwargs):

    generator = DS_INDHIST(
        dataset=h.file, size=h.size, output_dr=h.out, **kwargs
    )
    generator.run()
    return generator.output


# ------------------------------------
@click.command(
    "ds_privbayes",
    short_help="Data Synthesiser PrivBayes",
    options_metavar="[GENERATOR OPTIONS]",
)
@click.option(
    "--histogram_bins",
    type=int,
    default=10,
    help="number of bins",
)
@click.option(
    "--degree",
    type=int,
    default=1,
    help="",
)
@click.option(
    "--epsilon",
    type=float,
    default=1.0,
    help="privacy parameter epsilon",
)
def ds_privbayes(h, **kwargs):

    generator = DS_PRIVBAYES(
        dataset=h.file, size=h.size, output_dr=h.out, **kwargs
    )
    generator.run()
    return generator.output
