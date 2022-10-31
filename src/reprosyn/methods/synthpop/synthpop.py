from synthpop import Synthpop

from reprosyn.generator import PipelineBase
from reprosyn.dataset import Dataset

import warnings


class SYNTHPOP(PipelineBase):
    def __init__(
        self,
        method=None,
        visit_sequence=None,
        proper=False,
        cont_na=None,
        smoothing=False,
        default_method="cart",
        numtocat=None,
        catgroups=None,
        seed=None,
        **kw
    ):
        parameters = {
            "method": method,
            "visit_sequence": visit_sequence,
            "proper": proper,
            "cont_na": cont_na,
            "smoothing": smoothing,
            "default_method": default_method,
            "numtocat": numtocat,
            "catgroups": catgroups,
            "seed": seed,
        }

        self.gen = None

        super().__init__(**kw, **parameters)

    def preprocess(self):

        self.dtypes = Dataset.dtypes_from_metadata(self.dataset.metadata)

    def generate(self, refit=False):

        warnings.filterwarnings("ignore", category=FutureWarning)

        if (not self.gen) or refit:
            self.gen = Synthpop(**self.params)
            self.gen.fit(self.dataset.data, self.dtypes)

        self.output = self.gen.generate(self.size)
