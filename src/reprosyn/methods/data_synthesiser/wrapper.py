from reprosyn.generator import (
    GeneratorFunc,
    recode_as_category,
    recode_as_original,
)

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


class DS_INDHIST(GeneratorFunc):
    def __init__(self, histogram_bins=10, **kw):
        parameters = {
            "histogram_bins": histogram_bins,
        }

        self.gen = None

        super().__init__(**kw, **parameters)

    def preprocess(self):
        # domain could be json
        self.domain = get_metadata(self.metadata)

    def generate(self, refit=False):

        if (not self.gen) or refit:
            self.gen = IndependentHistogram(self.domain, **self.params)
            self.gen.fit(self.dataset)

        self.output = self.gen.generate_samples(self.size)
