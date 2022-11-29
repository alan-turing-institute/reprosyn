from synthpop import Synthpop

from reprosyn.generator import PipelineBase
from reprosyn.dataset import Dataset

import warnings


class SYNTHPOP(PipelineBase):
    """Generator Class for Synthpop. Uses ``py-synthpop``.

    Parameters
    ----------
    method : list[string], optional
        synthesising method for each variable. See `methods/__init__ <https://github.com/hazy/synthpop/blob/64ec0cdcc10febf6eaceef47a9586462ed2807b6/synthpop/method/__init__.py#>`_ for valid methods.
    visit_sequence : nd.array | list[int | str], optional
        iterable of columns indices. Default is 0:len(cols) .
    proper : bool, optional
        boolean, default to False. If True proper synthesis is conducted.
    cont_na : dict, optional
        dict of column names and corresponding `NA_METHOD <https://github.com/hazy/synthpop/blob/master/synthpop/method/__init__.py#L34>`_
    smoothing : bool | str | dict, optional
        smoothing method
    default_method : str, optional
        by default 'cart'
    numtocat : list[int | str], optional
        columns to be made into a number of categories given by ``catgroups``.
    catgroups : int | dict, optional
        size of categories specified ``numtocat``.
    seed : int
        random seed


    Notes
    -----

    Code at `hazy/synthpop <https://github.com/hazy/synthpop>`_.

    Which is itself a reimplementation of the `R package synthpop <https://www.jstatsoft.org/article/view/v074i11>`_.

    The best source of documentation is currently the `R package <https://cran.r-project.org/web/packages/synthpop/synthpop.pdf>`_.


    """

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
        """Saves pandas dtypes using :func:`Dataset.dtypes_from_metadata`"""

        self.dtypes = Dataset.dtypes_from_metadata(self.dataset.metadata)

    def generate(self, refit=False):
        """See `Synthpop.fit() <https://github.com/hazy/synthpop/blob/master/synthpop/synthpop.py#L44>`_ and `Synthpop.generate() <https://github.com/hazy/synthpop/blob/master/synthpop/synthpop.py#L84>`_

        Parameters
        ----------
        refit : bool, optional
           If true refits a `Synthpop <https://github.com/hazy/synthpop/blob/master/synthpop/synthpop.py>`_ class
        """

        warnings.filterwarnings("ignore", category=FutureWarning)

        if (not self.gen) or refit:
            self.gen = Synthpop(**self.params)
            self.gen.fit(self.dataset.data, self.dtypes)

        self.output = self.gen.generate(self.size)
