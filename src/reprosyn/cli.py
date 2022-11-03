"""The main `click` command, providing a CLI to `reprosyn.run()`."""

import importlib
import json
import sys
from io import StringIO
import os

import click

from reprosyn.generator import Handler

# from reprosyn.methods.ipf.cli import ipfcommand
from reprosyn.methods import COMMANDS


@click.group(
    options_metavar="[GLOBAL OPTIONS]",
    subcommand_metavar="[GENERATOR]",
)
@click.option(
    "--file",
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
def cli(ctx, **kwargs):
    """A cli tool synthesising the 1% census

    Usage: rsyn <global options> <generator> <generator options>

    If --file/STDIN not given, help is printed.

    Examples: \n

    rsyn --file census.csv mst \n
    census.csv > rsyn mst
    """

    ctx.obj = Handler(**kwargs)

    if os.path.exists(ctx.obj.get_config_path()):
        if ctx.obj.generateconfig:
            click.confirm(
                f"Config file exists at {ctx.obj.get_config_path()},"
                " override?",
                abort=True,
            )
        with click.open_file(ctx.obj.get_config_path(), "r") as f:
            config_params = json.load(f)
    else:
        config_params = json.load(
            StringIO(ctx.obj.configstring)
        )  # if nothing given with not update

    ctx.default_map = {ctx.invoked_subcommand: config_params}
    # print(f"Executing generator {ctx.invoked_subcommand}")


for cmd in COMMANDS:
    cli.add_command(cmd)


@main.command(
    "custom",
    short_help="A custom generator at /path/to/module.py:generator",
)
@click.argument("location", type=click.STRING)
@wrap_generator
def custom(h, location):
    """Find, load and run a custom generator.

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
        `reprosyn.generator.GeneratorFunc`.
    """

    gen = _load_generator_class(location)

    if not issubclass(gen, GeneratorFunc):
        raise ValueError("location must specify a GeneratorFunc subclass.")

    generator = run(gen, dataset=h.file, output_dir=h.out, size=h.size)

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
