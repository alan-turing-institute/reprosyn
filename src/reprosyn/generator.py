import inspect
import json
import pathlib
import warnings
from os import path

import click

from reprosyn.dataset import Dataset


def _base_generate_func(dataset):

    return dataset


class PipelineBase:
    """Base generator pipeline class"""

    generator = staticmethod(_base_generate_func)

    def __init__(
        self,
        dataset="https://raw.githubusercontent.com/alan-turing-institute/reprosyn/main/src/reprosyn/datasets/2011-census-microdata/2011-census-microdata-small.csv",
        metadata="https://raw.githubusercontent.com/alan-turing-institute/privacy-sdg-toolbox/main/prive/datasets/examples/census.json",
        output_dir="./",
        size=None,
        **kwargs,
    ):
        self.dataset = Dataset(dataset, metadata)

        self.size = size or len(self.dataset.data)
        self.output_dir = pathlib.Path(output_dir)
        self.params = kwargs
        self.output = None

        self.check_generator()

    def check_generator(self):

        if inspect.ismethod(self.generator):
            warnings.warn(
                f"Class attribute `generator` of {type(self).__name__} is not "
                "static. Either wrap in `staticmethod` or ensure there is a "
                "leading argument for the instance in its definition."
            )

    def preprocess(self):
        pass

    def generate(self):
        # inspect signatuere check for size as parameter
        self.output = self.generator(self.dataset, self.size, **self.params)
        return self.output

    def postprocess(self):
        pass

    def save(self):
        self.output.to_csv(self.output_dir / "output.csv", index=False)

    def run(self):
        self.preprocess()
        self.generate()
        self.postprocess()
        self.save()

    def get_parameters(self):
        return self.params


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
        metadata=None,
    ):
        self.file = file
        self.out = out
        self.size = size
        self.generateconfig = generateconfig
        self.configpath = configpath
        self.configfolder = configfolder
        self.configstring = configstring
        self.metadata = metadata

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


# Helper functions to encode categories as ordinal.
def encode_ordinal(dataset: Dataset):

    encoders = {
        col["name"]: ordinal_map(col)
        for col in dataset.metadata
        if "finite" in col["type"]
    }

    df = dataset.data.copy()
    for col, enc in encoders.items():
        df[col] = df[col].apply(lambda x: enc["to_index"][x])

    return df, encoders


def ordinal_map(col):
    r = "representation"
    map_dict = {
        "from_index": dict(
            zip(
                range(len(col[r])),
                sorted(col[r]),
            )
        ),
        "to_index": dict(
            zip(
                sorted(col[r]),
                range(len(col[r])),
            )
        ),
    }
    return map_dict


def decode_ordinal(data, encoders):

    df = data.copy()
    for col, enc in encoders.items():
        df[col] = df[col].apply(lambda x: enc["from_index"][x])

    return df
