"""This module contains the base pipeline class and helper functions to use when adding methods

"""
from __future__ import annotations

import inspect
import json
import pathlib
import warnings
from os import path

import click

from reprosyn.dataset import Dataset

import pandas as pd


def _base_generate_func(dataset):

    return dataset


class PipelineBase:
    """Base class for a generator pipeline.

    Parameters
    ----------
    dataset : str | pandas.Dataframe, optional
        either a path to a file or a pre-loaded dataframe, by default the `Census 1% <https://raw.githubusercontent.com/alan-turing-institute/reprosyn/main/src/reprosyn/datasets/2011-census-microdata/2011-census-microdata-small.csv>`_
    metadata : str, optional
        metadata list[dict], see `Data Format <https://privacy-sdg-toolbox.readthedocs.io/en/latest/dataset-schema.html>`_, by default `Census Schema <https://raw.githubusercontent.com/alan-turing-institute/privacy-sdg-toolbox/main/prive/datasets/examples/census.json>`_
    output_dir : str, optional
        output directory, by default "./"
    size : int, optional
        number of rows to synthesise, defaults to length of dataset


    Attributes
    ----------
    dataset: Dataset
        A :py:class:`~dataset.Dataset` instance.
    size: int
        The number of rows to synthesise.
    output_dir: Path
        directory for saving outputs. Defaults to root.
    params: dict
        Arbitrary keyword method parameters
    output: pandas.Dataframe
        synthetic dataset
    """

    generator = staticmethod(_base_generate_func)

    def __init__(
        self,
        dataset=None,
        metadata=None,
        out="./",
        size=None,
        **kwargs,
    ):

        # defaults for dev:
        if metadata is None:
            metadata = "https://raw.githubusercontent.com/alan-turing-institute/privacy-sdg-toolbox/main/prive/datasets/examples/census.json"
        if dataset is None:
            dataset = "https://raw.githubusercontent.com/alan-turing-institute/reprosyn/main/src/reprosyn/datasets/2011-census-microdata/2011-census-microdata-small.csv"

        self.dataset = Dataset(dataset, metadata)

        self.size = size or len(self.dataset.data)
        self.output_dir = pathlib.Path(out)
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
        """Preprocessing to be implemented by method"""
        pass

    def generate(self):
        """Call the synthetic generation method

        Returns
        -------
        any
            An output dataset, type will depend on method
        """
        self.output = self.generator(self.dataset, self.size, **self.params)
        return self.output

    def postprocess(self):
        """Postprocessing to be implemented by method"""
        pass

    def save(self):
        self.output.to_csv(self.output_dir / "output.csv", index=False)

    def run(self):
        """Runs pipeline"""
        self.preprocess()
        self.generate()
        self.postprocess()
        self.save()


def encode_ordinal(dataset: Dataset):
    """Using metadata, maps categorical columns to integer encoding

    Parameters
    ----------
    dataset
        A loaded :class:`~dataset.Dataset`

    Returns
    -------
    pandas.Dataframe
        An encoded dataframe
    dict
        An encoding dictionary, with encoded column names as keys,
        and two mapping dictionaries ["to_index", "from_index"] as values,
        see :func:`ordinal_map`
    """

    encoders = {
        col["name"]: ordinal_map(col)
        for col in dataset.metadata
        if "finite" in col["type"]
    }

    df = dataset.data.copy()
    for col, enc in encoders.items():
        df[col] = df[col].apply(lambda x: string_get(enc["to_index"], x))

    return df, encoders


def string_get(d: dict, k: str | int):
    """A hack to help with mapping, robustly returns a metadata dictionary key for both ``int`` or ``str(int)``.

    Parameters
    ----------
    d : dict
        dictionary, assumed encoding mapper
    k : str | int
        key, either a number or a string

    Returns
    -------
    value
        representation value
    """

    val = d.get(k)
    if val is None:
        val = d.get(str(k))

    return val


def ordinal_map(col):
    """Creates directional ordinal mapper dictionary

    Parameters
    ----------
    col
        metadata column, see `Data Format <https://privacy-sdg-toolbox.readthedocs.io/en/latest/dataset-schema.html>`_


    Returns
    -------
    dict
        dictionary with two keys {"from_index","to_index"}, and the corresponding mapping dictionaries.
    """
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


def decode_ordinal(data: pd.DataFrame, encoders: dict):
    """Decodes an ordinal mapping, given an encoder dictionary. See also :func:`encode_ordinal`

    Parameters
    ----------
    data : pd.DataFrame
        Encoded dataframe
    encoders : dict
        Dictionary of encoded columns, and mappings

    Returns
    -------
    pd.DataFrame
        decoded dataframe
    """

    df = data.copy()
    for col, enc in encoders.items():
        df[col] = df[col].apply(lambda x: enc["from_index"][x])

    return df
