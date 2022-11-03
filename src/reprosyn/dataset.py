"""module for the Dataset class"""

from __future__ import annotations

import json
from os import path
import io

import pandas as pd
import requests
import validators


class Dataset:
    """Class for holding a raw dataset and metadata information

    Parameters
    ----------
    dataset : pd.DataFrame | str
        raw dataset
    metadata : list[dict] | str
        either a metadata list, a url, or a file path.


    Attributes
    ----------
    data : pd.DataFrame
        The raw data
    metadata : list[dict]
        metadata as described in `Data Format <https://privacy-sdg-toolbox.readthedocs.io/en/latest/dataset-schema.html>`_
    """

    def __init__(
        self, dataset: pd.DataFrame | str, metadata: list[dict] | str
    ) -> None:

        self.data = self.read_dataset(dataset)
        self.metadata = self.read_metadata(metadata)
        self.validate_metadata(self.metadata)
        self._check_correspondence()
        self.data = self.data.astype(self.dtypes_from_metadata(self.metadata))

    def _check_correspondence(self):
        """Checks if data columns are represented in metadata

        If there are more metadata columns, metadata is subsetted.

        Raises
        ------
        Exception
            If data columns are not represented
        """

        metadata_cols = [col["name"] for col in self.metadata]
        columns = list(self.data.columns)

        if set(columns) <= set(metadata_cols):
            # subset metadata.
            self.metadata = [c for c in self.metadata if c["name"] in columns]
        elif set(columns) > set(metadata_cols):
            raise Exception(
                f"The following columns are not represented in metadata: {set(columns)-set(metadata_cols)}"
            )

    @staticmethod
    def validate_metadata(metadata):
        """Ensures metadata corresponds to `Data Format <https://privacy-sdg-toolbox.readthedocs.io/en/latest/dataset-schema.html>`_

        Parameters
        ----------
        metadata : list[dict]
            Should be a list of dictionaries.
        """

        assert isinstance(metadata, list)
        assert all(isinstance(c, dict) for c in metadata)
        assert all(
            [
                all(
                    k in col.keys() for k in ["name", "type", "representation"]
                )
                for col in metadata
            ]
        )
        assert all(isinstance(x["name"], str) for x in metadata)
        # TODO: further assertions could check for 'type' and 'representation' entries

    @staticmethod
    def dtypes_from_metadata(metadata):
        """
        our metadata uses the TAPAS `Data Format <https://privacy-sdg-toolbox.readthedocs.io/en/latest/dataset-schema.html>`_
        """

        representation_map = {
            "integer": "int",
            "date": "datetime",
            "string": "string",
            "number": "float",
            "datetime": "datetime",
        }

        def map_type(col):

            if "finite" in col["type"]:
                return "category"
            else:
                return representation_map[col["representation"]]

        return {col["name"]: map_type(col) for col in metadata}

    @staticmethod
    def read_dataset(dataset: pd.DataFrame | str) -> pd.DataFrame:

        if dataset is None:
            raise Exception("a dataset must be passed")
        elif isinstance(dataset, pd.DataFrame):
            return dataset
        elif isinstance(dataset, io.TextIOWrapper):
            return pd.read_csv(dataset)
        elif any(
            [
                path.isfile(dataset),
                _is_url(dataset),
            ]
        ):
            return pd.read_csv(dataset)
        else:
            raise Exception("dataset must be a dataframe or csv")

    @staticmethod
    def read_metadata(metadata: list | str):

        if metadata is None:
            raise Exception("metadata must be passed")
        if isinstance(metadata, list):
            return metadata
        elif isinstance(metadata, io.TextIOWrapper):
            return json.loads(metadata)
        elif path.isfile(metadata):
            return json.loads(metadata)
        elif _is_url(metadata):
            return _json_from_url(metadata)
        else:
            raise Exception(
                "Metadata needs to be a real file, a url to a file, or a list[dict]"
            )


# HELPERS -----------------------
def _json_from_url(url):
    """loads json from url"""

    resp = requests.get(url)
    data = json.loads(resp.text)
    return data


def _is_url(s):
    """checks if valid url"""
    valid = validators.url(s)
    if valid is True:
        return True
    else:
        return False
