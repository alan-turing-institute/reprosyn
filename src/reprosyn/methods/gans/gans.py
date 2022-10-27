""" CTGAN interface to CTGANSynthesiser. See https://github.com/alan-turing-institute/CTGAN/blob/dependencies/ctgan/synthesizer.py """

from reprosyn.generator import PipelineBase

from ctgan import CTGANSynthesizer
from reprosyn.methods.gans.pate_gan import PateGan

"""
CTGAN Args:
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


def get_metadata(metadata, col_type="categorical"):

    # TODO: for now, just do everything as categorical. Need to edit to pick up data type from columns
    meta = {}
    meta["columns"] = [
        {
            "name": col["name"],
            "type": col_type,
            "size": len(col["representation"]),
            "i2s": col["representation"],
        }
        for col in metadata
    ]
    return meta


class CTGAN(PipelineBase):
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

        self.meta = get_metadata(self.dataset.metadata)

    def generate(self, refit=False):

        if (not self.ctgan) or refit:
            self.ctgan = CTGANSynthesizer(**self.params)
            self.ctgan.fit(self.dataset.data, self.meta)

        self.output = self.ctgan.sample(self.size)


class PATEGAN(PipelineBase):
    def __init__(
        self,
        epsilon=1,
        delta=1e-5,
        num_teachers=10,
        n_iters=100,
        batch_size=128,
        learning_rate=1e-4,
        **kw
    ):

        parameters = {
            "epsilon": epsilon,
            "delta": delta,
            "num_teachers": num_teachers,
            "n_iters": n_iters,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
        }

        self.gen = None

        super().__init__(**kw, **parameters)

    def preprocess(self):

        self.meta = get_metadata(self.dataset.metadata, col_type="Categorical")

    def generate(self, refit=False):

        if (not self.gen) or refit:
            self.gen = PateGan(self.meta, **self.params)
            self.gen.fit(self.dataset.data)

        self.output = self.gen.generate_samples(self.size)
