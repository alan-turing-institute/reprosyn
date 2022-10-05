from synthpop import Synthpop

from reprosyn.generator import GeneratorFunc


def dtypes_from_metadata(metadata):
    """synthpop.fit() expects a variable dtypes, which has the form dict[colname, dtype]

    dtypes are:
    NUM_COLS_DTYPES = ['int', 'float', 'datetime']
    CAT_COLS_DTYPES = ['category', 'bool']
    """

    def map_type(col):

        r = "representation"

        if "finite" in col["type"]:
            dtype = "category"
        elif col[r] == "integer":
            dtype = "int"
        elif col[r] == "number":
            dtype = "float"
        elif "date" in col[r]:
            dtype = "datetime"
        elif "interval" in col["type"]:
            dtype = "float"
        elif col[r] == "string":
            dtype = "category"
        else:
            raise Exception("unrecognised type in metadata")

        return dtype

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

        self.gen = Synthpop(**parameters)

        super().__init__(**kw, **parameters)

    def preprocess(self):

        self.dtypes = dtypes_from_metadata(self.metadata)

    def generate(self, refit=False):

        if (not self.gen) or refit:
            self.gen = Synthpop(**self.params)
            self.gen.fit(self.dataset, self.dtypes)

        self.output = self.gen.generate(self.size)
