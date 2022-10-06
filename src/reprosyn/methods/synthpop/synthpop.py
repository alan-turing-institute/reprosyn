from synthpop import Synthpop

from reprosyn.generator import GeneratorFunc


def dtypes_from_metadata(metadata):
    """synthpop.fit() expects a variable dtypes, which has the form dict[colname, dtype]

    dtypes are:
    NUM_COLS_DTYPES = ['int', 'float', 'datetime']
    CAT_COLS_DTYPES = ['category', 'bool']

    our metadata uses the prive datatypes, see: https://privacy-sdg-toolbox.readthedocs.io/en/latest/dataset-schema.html
    """

    representation_map = {
        "integer": "int",
        "date": "datetime",
        "string": "category",
        "number": "float",
        "datetime": "datetime",
    }

    def map_type(col):

        if "finite" in col["type"]:
            return "category"
        else:
            return representation_map[col["representation"]]

    return {col["name"]: map_type(col) for col in metadata}


class SYNTHPOP(GeneratorFunc):
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

        self.dtypes = dtypes_from_metadata(self.metadata)
        print(self.dtypes)

    def generate(self, refit=False):

        if (not self.gen) or refit:
            self.gen = Synthpop(**self.params)
            self.gen.fit(self.dataset, self.dtypes)

        self.output = self.gen.generate(self.size)
