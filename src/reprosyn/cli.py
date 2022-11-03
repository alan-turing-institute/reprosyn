"""The main `click` command, providing a CLI to `reprosyn.run()`."""

import importlib
import json
import sys
from io import StringIO
import os

import click

from reprosyn.generator import PipelineBase
from reprosyn.cli_utils import wrap_generator, get_config_path

# from reprosyn.methods.ipf.cli import ipfcommand
from reprosyn.methods import COMMANDS


@click.group(
    options_metavar="[GLOBAL OPTIONS]", subcommand_metavar="[GENERATOR]"
)
@click.option(
    "--dataset",
    type=click.File("rt"),
    help="[REQUIRED] filepath to dataset or STDIN",
    default=sys.stdin,
)
@click.option(
    "--out",
    help="filepath to write output to",
    type=click.Path(),
    default=".",
)
@click.option(
    "--size",
    type=int,
    help="number of rows to synthesise",
)
@click.option(
    "--generateconfig",
    is_flag=True,
    help="flag to generate input json",
)
@click.option(
    "--configpath",
    type=click.Path(),
    default="-",
    help="path to config file. If --generateconfig, config file is saved here",
)
@click.option(
    "--configstring",
    type=click.STRING,
    default="{}",
    help="configuration string as a dictionary. Overrided by --configpath",
)
@click.option(
    "--configfolder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "methods/config/"
    ),
    help="directory for method configs",
)
@click.option(
    "--metadata",
    type=click.File(),
    default=None,
    help="domain to use, in privacy toolbox format, defaults to census",
)
@click.pass_context
def cli(ctx, **params):
    """A cli tool synthesising the 1% census

    Usage: rsyn <global options> <generator> <generator options>

    If --dataset/STDIN not given, help is printed.

    Examples: \n

    rsyn --dataset census.csv mst \n
    census.csv > rsyn mst
    """

    if os.path.exists(get_config_path(params)):
        if params["generateconfig"]:
            click.confirm(
                f"Config file exists at {get_config_path(params)},"
                " override?",
                abort=True,
            )
        with click.open_file(get_config_path(params), "r") as f:
            config_params = json.load(f)
    else:
        config_params = json.load(
            StringIO(params["configstring"])
        )  # if nothing given with not update

    ctx.default_map = {ctx.invoked_subcommand: config_params}
    # print(f"Executing generator {ctx.invoked_subcommand}")


for cmd in COMMANDS:
    cli.add_command(cmd)


@cli.command(
    "custom",
    short_help="A custom generator at /path/to/module.py:generator",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.argument("location", type=click.STRING)
@wrap_generator
def custom(ctx, location):
    """Find, load and run a custom generator.

    You can add any additional options the method needs after the location.

    E.g. ``rsyn --size <size> --dataset <path> custom './tests/custom_method.py:RAW' --replace True``


    Parameters
    ----------
    location : str
        Location of generator class. Given in the form
        `/path/to/module.py:generator`. The module path can be relative.

    Returns
    -------
    output : dataframe
        The dataframe-like object stored in `generator.output`.

    Raises
    ------
    ValueError
        If `location` does not point to a subclass of
        `reprosyn.generator.PipelineBase`.
    """

    method_args = {
        ctx.args[i][2:]: ctx.args[i + 1] for i in range(0, len(ctx.args), 2)
    }

    gen = _load_generator_class(location)

    if not issubclass(gen, PipelineBase):
        raise ValueError("location must specify a GeneratorFunc subclass.")

    generator = gen(**ctx.parent.params, **method_args)
    generator.run()

    return generator.output


def _load_generator_class(location):
    """Find and load a generator class from a `path:name` string."""

    path, name = location.split(":")

    spec = importlib.util.spec_from_file_location("__main__", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    gen = getattr(module, name)

    return gen


if __name__ == "__main__":
    cli()
