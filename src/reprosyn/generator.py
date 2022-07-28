import click
from os import path
from os import PathLike
import json
import io
import pandas as pd
import pathlib


class GeneratorFunc:
    """Base generator function class"""

    def __init__(self, func, dataset, size=None, output_dir=".", **kwargs):
        self.dataset = self.read_dataset(dataset)
        self.size = size or len(self.dataset)
        self.gen = func
        self.options = kwargs
        self.output_dir = pathlib.Path(output_dir)

    def read_dataset(dataset):
        if isinstance(dataset, (io.StringIO, str, PathLike)):
            return pd.read_csv(dataset)
        elif isinstance(dataset, pd.DataFrame):
            return dataset
        else:
            raise ValueError("Pass a filename, StringIO, or pandas dataframe")

    def preprocess(self):
        pass

    def generate(self):
        # inspect signatuere check for size as parameter
        self.output = self.gen(self.dataset, self.size, **self.options)
        return self.output

    def postprocess(self):
        pass

    def save(self):
        return self.output.to_csv(self.output_dir)


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
