import click
from os import path
import json

# Helper class for manipulating options across reprosyn
class Generator(object):
    def __init__(
        self,
        file=None,
        out=None,
        size=None,
        generateconfig=None,
        configpath=None,
        configfolder=None,
        configstring=None,
    ):
        self.file = file
        self.out = out
        self.size = size
        self.generateconfig = generateconfig
        self.configpath = configpath
        self.configfolder = configfolder
        self.configstring = configstring

    def get_config_path(self):
        if self.configpath != "-":
            p = path.join(self.configfolder, self.configpath)
        else:
            p = self.configpath
        return p


# Wrapper for any generator subcommand
def wrap_generator(func):
    @click.pass_obj
    def wrapper(sdg, **kwargs):
        if sdg.generateconfig:
            p = sdg.get_config_path()
            with click.open_file(p, "w") as outfile:
                # click.echo(f"Saving to config file to {p}")
                json.dump(kwargs, outfile)
        else:
            if not sdg.file.isatty():
                df = func(sdg, **kwargs)
                click.echo(df.to_csv(None, index=False), file=sdg.out)
            else:
                click.echo("Please give a dataset using --file or STDIN")
                func.main(["--help"])

    return wrapper
