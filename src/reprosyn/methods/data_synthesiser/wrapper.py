from reprosyn.generator import PipelineBase

from .data_synthesiser import IndependentHistogram, BayesianNet, PrivBayes


def get_metadata(metadata):

    # TODO: for now, just do everything as categorical. Need to edit to pick up data type from columns
    meta = {}
    meta["columns"] = [
        {
            "name": col["name"],
            "type": "Categorical",
            "size": len(col["representation"]),
            "i2s": col["representation"],
        }
        for col in metadata
    ]
    return meta


class DS_INDHIST(PipelineBase):
    def __init__(self, histogram_bins=10, **kw):
        parameters = {
            "histogram_bins": histogram_bins,
        }

        self.gen = None

        super().__init__(**kw, **parameters)

    def preprocess(self):

        self.domain = get_metadata(self.dataset.metadata)

    def generate(self, refit=False):

        if (not self.gen) or refit:
            self.gen = IndependentHistogram(self.domain, **self.params)
            self.gen.fit(self.dataset.data)

        self.output = self.gen.generate_samples(self.size)


class DS_BAYNET(PipelineBase):
    def __init__(self, histogram_bins=10, degree=1, seed=None, **kw):
        parameters = {
            "histogram_bins": histogram_bins,
            "degree": degree,
            "seed": seed,
        }

        self.gen = None

        super().__init__(**kw, **parameters)

    def preprocess(self):

        self.domain = get_metadata(self.dataset.metadata)

    def generate(self, refit=False):

        if (not self.gen) or refit:
            self.gen = BayesianNet(self.domain, **self.params)
            self.gen.fit(
                self.dataset.data.astype("object")
            )  # hack to get round a not implemented error when dtype=="category"

        self.output = self.gen.generate_samples(self.size)


class DS_PRIVBAYES(PipelineBase):
    def __init__(
        self, histogram_bins=10, degree=1, epsilon=1, seed=None, **kw
    ):
        parameters = {
            "histogram_bins": histogram_bins,
            "degree": degree,
            "seed": seed,
            "epsilon": epsilon,
        }

        self.gen = None

        super().__init__(**kw, **parameters)

    def preprocess(self):

        self.domain = get_metadata(self.dataset.metadata)

    def generate(self, refit=False):

        if (not self.gen) or refit:
            self.gen = PrivBayes(self.domain, **self.params)
            self.gen.fit(self.dataset.data.astype("object"))

        self.output = self.gen.generate_samples(self.size)
