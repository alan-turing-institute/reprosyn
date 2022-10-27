from __future__ import annotations

import json
from os import path

import pandas as pd
import requests
import validators


class Dataset:
    def __init__(self, dataset, metadata) -> None:

        self.data = self.read_dataset(dataset)
        self.metadata = self.read_metadata(metadata)
        self.data = self.data.astype(self.dtypes_from_metadata(self.metadata))

    @staticmethod
    def dtypes_from_metadata(metadata):
        """
        our metadata uses the prive datatypes, see: https://privacy-sdg-toolbox.readthedocs.io/en/latest/dataset-schema.html
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
        if isinstance(dataset, pd.DataFrame):
            return dataset
        elif path.isfile(dataset):
            return pd.read_csv(dataset)
        else:
            raise Exception("dataset must be a dataframe or csv")

    @staticmethod
    def read_metadata(metadata):
        if isinstance(metadata, list):
            return metadata
        elif path.isfile(metadata):
            return json.loads(metadata)
        elif is_url(metadata):
            return json_from_url(metadata)
        else:
            raise Exception(
                "Metadata needs to be a real file, a url to a file, or a dictionary"
            )


# HELPERS -----------------------
def json_from_url(url):

    resp = requests.get(url)
    data = json.loads(resp.text)
    return data


def is_url(s):
    valid = validators.url(s)
    if valid is True:
        return True
    else:
        return False
