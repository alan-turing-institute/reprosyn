import inspect
import json
import requests
import pathlib
import warnings
from os import path

import click
import pandas as pd


def _base_generate_func(dataset, size):

    return dataset


def load_json(fname):

    resp = requests.get(fname)
    data = json.loads(resp.text)
    return data


class GeneratorFunc:
    """Base generator function class"""

    generator = staticmethod(_base_generate_func)

    def __init__(
        self,
        dataset="https://raw.githubusercontent.com/alan-turing-institute/reprosyn/main/src/reprosyn/datasets/2011-census-microdata/2011-census-microdata-small.csv",
        metadata=None,
        output_dir="./",
        size=None,
        **kwargs,
    ):
        self.dataset = self.read_dataset(dataset)
        self.metadata = metadata or load_json(
            "https://raw.githubusercontent.com/alan-turing-institute/privacy-sdg-toolbox/main/prive/datasets/examples/census.json"
        )

        self.size = size or len(self.dataset)
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

    def read_dataset(self, dataset):
        if isinstance(dataset, pd.DataFrame):
            return dataset
        else:
            return pd.read_csv(dataset)

    def preprocess(self):
        """Need to encode domain data into method's format"""
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

    @staticmethod
    def get_category_map(metadata: list[dict]):

        """Returns a mapping dictionary from the metadata.

        Keys are column names. Entries are dictionaries.

        Entries have two keys "to_index", which maps from column values to 0-n, and "from_index" which does the reverse.
        """

        def build_maps(col):
            return {
                "from_index": dict(
                    zip(
                        range(len(col["representation"])),
                        sorted(col["representation"]),
                    )
                ),
                "to_index": dict(
                    zip(
                        sorted(col["representation"]),
                        range(len(col["representation"])),
                    )
                ),
            }

        return {col["name"]: build_maps(col) for col in metadata}

    @staticmethod
    def recode_as_category(self, mapping):
        """Recodes a dataset as categorical integers

        Returns
        -------
        Pandas dataframe recoded as categorical integers

        Mapping dictionary with columns as keys and a lookup dict as values
        """

        for col in data.columns:
            orig = data[col]
            data[col] = data[col].astype("category").cat.codes
            mapping[col] = dict(zip(data[col], orig))

        return data, mapping


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


def recode_as_original(data, mapping):

    """Given a dataframe encoded as categorical codes and a mapping dictionary, retrieves original values

    Returns
    -------
    Pandas dataframe mapped to original values.
    """

    for col in data.columns:
        data[col] = data[col].apply(lambda x: mapping[col][x])

    return data
