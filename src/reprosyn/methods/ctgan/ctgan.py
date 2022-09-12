""" CTGAN interface to CTGANSynthesiser. See https://github.com/alan-turing-institute/CTGAN/blob/dependencies/ctgan/synthesizer.py """
import pandas as pd

from reprosyn.generator import (
    GeneratorFunc,
    recode_as_category,
    recode_as_original,
)

from ctgan import CTGANSynthesizer

"""
Args:
    embedding_dim (int):
        Size of the random sample passed to the Generator. Defaults to 128.
    gen_dim (tuple or list of ints):
        Size of the output samples for each one of the Residuals. A Resiudal Layer
        will be created for each one of the values provided. Defaults to (256, 256).
    dis_dim (tuple or list of ints):
        Size of the output samples for each one of the Discriminator Layers. A Linear Layer
        will be created for each one of the values provided. Defaults to (256, 256).
    l2scale (float):
        Wheight Decay for the Adam Optimizer. Defaults to 1e-6.
    batch_size (int):
        Number of data samples to process in each step.
"""


def get_metadata(dataset):

    # TODO: for now, just do everything as categorical. Need to edit to pick up data type from columns
    meta = {}
    meta["columns"] = [
        {"name": col, "type": "categorical"} for col in dataset.columns
    ]
    return meta


class CTGAN(GeneratorFunc):
    """Generator class for CTGAN"""

    def __init__(
        self,
        embedding_dim=128,
        gen_dim=(256, 256),
        dis_dim=(256, 256),
        l2scale=1e-6,
        batch_size=500,
        epochs=300,
        **kw
    ):

        parameters = {
            "embedding_dim": embedding_dim,
            "gen_dim": gen_dim,
            "dis_dim": dis_dim,
            "l2scale": l2scale,
            "batch_size": batch_size,
            "epochs": epochs,
        }

        self.ctgan = None

        super().__init__(**kw, **parameters)

    def preprocess(self):

        self.meta = get_metadata(self.dataset)

    def generate(self, refit=False):

        if (not self.ctgan) or refit:
            self.ctgan = CTGANSynthesizer(**self.params)
            self.ctgan.fit(self.dataset, self.meta)

        self.output = self.ctgan.sample(self.size)
