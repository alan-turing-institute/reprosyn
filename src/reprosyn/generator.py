import click
from os import path
from os import PathLike
import json
import pandas as pd

import pathlib


def _basegenerate(gen):
    pass


class GeneratorFunc:
    """Base generator function class"""

    generator = _basegenerate

    def __init__(self, dataset, output_dir, size=None, **kwargs):
        self.dataset = self.read_dataset(dataset)
        self.size = size or len(self.dataset)
        self.options = kwargs
        self.output_dir = pathlib.Path(output_dir)

    def read_dataset(self, dataset):
        if isinstance(dataset, pd.DataFrame):
            return dataset
        else:
            return pd.read_csv(dataset)

    def preprocess(self):
        pass

    def generate(self):
        # inspect signatuere check for size as parameter
        self.output = self.generator(self.dataset, self.size, **self.options)
        return self.output

    def postprocess(self):
        pass

    def save(self):
        self.output.to_csv(self.output_dir / "output.csv")


class Handler(object):
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
    def wrapper(h, **kwargs):
        if h.generateconfig:
            p = h.get_config_path()
            with click.open_file(p, "w") as outfile:
                # click.echo(f"Saving to config file to {p}")
                json.dump(kwargs, outfile)
        else:
            if not h.file.isatty():
                func(h, **kwargs)
            else:
                click.echo("Please give a dataset using --file or STDIN")
                func.main(["--help"])

    return wrapper
