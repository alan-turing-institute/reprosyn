import click
import json
import os


def get_config_path(params):
    if params["configpath"] != "-":
        p = os.path.join(params["configfolder"], params["configpath"])
    else:
        p = params["configpath"]
    return p


def _print_help():
    ctx = click.get_current_context()
    click.echo(ctx.get_help())


def wrap_generator(func):
    """Convenient decorator function for command line use."""

    @click.pass_context
    def wrapper(ctx, **kwargs):
        if ctx.parent.params["generateconfig"]:
            p = get_config_path(ctx.parent.params)
            with click.open_file(p, "w") as outfile:
                # click.echo(f"Saving to config file to {p}")
                json.dump(ctx.params, outfile)
        else:
            if not ctx.parent.params["dataset"].isatty():
                func(ctx, **kwargs)
            else:

                click.echo("Please give a dataset using --dataset or STDIN")
                _print_help()

    return wrapper
