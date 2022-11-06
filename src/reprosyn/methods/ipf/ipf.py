import random as rnd
import string

import numpy as np
import pandas as pd
from tqdm import tqdm

from reprosyn.generator import PipelineBase, encode_ordinal, decode_ordinal


def get_count_matrix(X, metadata):
    """Returns the counts of each feature category.

    Parameters
    ----------
    X : np.ndarray
        X is a numpy array with shape (features, individuals).
    metadata : list[dict]
        metadata, see `Data Format <https://privacy-sdg-toolbox.readthedocs.io/en/latest/dataset-schema.html>`_

    Returns
    -------
    nd.ndarray
        a numpy array with ndims = nfeatures and shape determined by the size of feature categories, taken from metadata e.g. (ncatg1, ncatg2,...)
    """

    category_sizes = [
        len(col["representation"]) for col in metadata
    ]  # list of columns sizes

    # creates an ndim, and shape with size of columnss
    count_matrix = np.zeros(
        category_sizes, dtype=np.uint16
    )  # assumes no cell will have more than 65k persons in it...

    for i in range(X.shape[1]):
        count_matrix[tuple(X.T[i])] += 1

    return count_matrix


def get_margin_grids(X, count_matrix, known_marginals):
    """Create some collections of dimensions where the marginal counts are known.

    These will be matched by the :func:`sinkhorn algorithm`

    Parameters
    ----------
    X : np.ndarray
        numpy array with shape (features, individuals).
    count_matrix : np.ndarry
        matrix of shape (len(catg1), len(catg2)...), with occurence counts for each category cell
    known_marginals : list[tuple]
       known_marginals should be *ordered* tuples (to save checking ordering issues later...)

    Returns
    -------
    list
        margin_grids is list of len(known_marginals) with entries [known_marginals[i], ndarray]
    """

    dim_set = set(range(X.shape[0]))
    margin_grids = [
        (x, count_matrix.sum(axis=tuple(dim_set - set(x))))
        for x in known_marginals
    ]
    return margin_grids


# Helper function to construct Einstein sum definition strings
def _einsum_construct(ind, full_dim):
    alpha = string.ascii_lowercase[:full_dim]
    string_pre = alpha + ","
    string_mid = "".join([alpha[x] for x in ind])
    string_end = "->" + alpha
    return string_pre + string_mid + string_end


def sinkhorn_tensor(
    initial_tensor,
    marginals,
    max_iterations=1e4,
    iter_tolerance=5e-1,
    eps=1e-5,
):
    """A version of iterative proportional fitting algorithm, in high dimension, with multivariate marginals

    Attempts to convert initial_tensor to have specified marginals
    If initial_tensor is constant, then it will yield the maximum entropy distribution with specified marginals

    Parameters
    ----------
    initial_tensor : np.ndarray
        beginning probability tensor of shape (len(catg1), len(catg2)...)
    marginals : list
        list of len(known_marginals) with entries [known_marginals[i], ndarray], see :func:`get_margin_grids`
    max_iterations : float, optional
        maximum number of iterations
    iter_tolerance : float, optional
        tolerance value for stopping
    eps : _type_, optional
        _description_, by default 1e-5

    Returns
    -------
    np.ndarray
        probability matrix with probabilities for each category cell
    """
    count = 0
    err = 1 + iter_tolerance
    while (count < max_iterations) and (err > iter_tolerance):
        run_tensor = initial_tensor + 0
        count += 1
        dim_set = set(range(len(initial_tensor.shape)))
        for margin_ind in marginals:
            factors = margin_ind[1] / (
                eps + run_tensor.sum(axis=tuple(dim_set - set(margin_ind[0])))
            )
            run_tensor = np.einsum(
                _einsum_construct(margin_ind[0], len(dim_set)),
                run_tensor,
                factors,
            )

        err = abs(run_tensor - initial_tensor).sum()
        initial_tensor = run_tensor

    return initial_tensor


def sampler(N, probability_array):
    """Samples from the probability matrix

    Parameters
    ----------
    N : int
        number of samples
    probability_array : np.ndarray
        probability matrix with probabilities for each category cell

    Returns
    -------
    np.array
        matrix of samples (features, individuals)
    """
    dim_vec = tuple(range(len(probability_array.shape)))

    outlist = []
    for i in tqdm(range(N)):
        temp_array = probability_array + 0
        samplist = []
        for dim in range(len(dim_vec)):
            newsample = rnd.choices(
                range(probability_array.shape[dim]),
                weights=temp_array.sum(
                    axis=tuple(range(1, len(temp_array.shape)))
                ),
            )[0]
            temp_array = temp_array[newsample]
            samplist.append(newsample)
        outlist.append(samplist)
    return np.array(outlist).T


def ipf(
    data, counts, support, size, marginals, max_iterations, iter_tolerance
):
    """Runs ipf algorithm steps: :func:`get_margin_grids`, :func:`sinkhorn_tensor`, :func:`sampler`

    Parameters
    ----------
    data : np.ndarray
        numpy array with shape (features, individuals).
    counts : np.ndarray
        matrix of shape (len(catg1), len(catg2)...), see :func:`get_count_matrix`
    support : np.ndarray
        beginning probability tensor of shape (len(catg1), len(catg2)...)
    size : int
        number of samples
    marginals : list[tuples]
        list of marginals to preserve, specified by tuples of column indices
    max_iterations : float
        maximum number of iterations
    iter_tolerance : float
        tolerance value for stopping

    Returns
    -------
    np.ndarray
        probability matrix with probabilities for each category cell


    Notes
    -----

    The output of :func:`sinkhorn_tensor` could be saved for repeat sampling
    """

    margin_grids = get_margin_grids(data, counts, marginals)

    approx_count = sinkhorn_tensor(
        initial_tensor=support,
        marginals=margin_grids,
        max_iterations=max_iterations,
        iter_tolerance=iter_tolerance,
    )

    approx_sample = sampler(size, approx_count)

    return approx_sample


class IPF(PipelineBase):
    """Generator class for iterative proportional fitting.

    Parameters
    ----------
    marginals : list[tuple[int]]
        A list of marginal combinations to preserve.

    Notes
    -----

    IPF deals solely with categorical data.

    The count matrix (see :func:`count_matrix`) is the computational bottleneck,
    so is calculated once during preprocessing. This is the key obstacle to scaling.

    Code adapted from original draft by Sam Cohen.

    """

    generator = staticmethod(ipf)

    def __init__(
        self,
        marginals=[(0, 1), (0, 2)],
        max_iterations=1e4,
        iter_tolerance=5e-1,
        **kw
    ):
        # TODO: check that marginals are ordered tuples.
        parameters = {
            "marginals": marginals,
            "max_iterations": max_iterations,
            "iter_tolerance": iter_tolerance,
        }
        super().__init__(**kw, **parameters)

    def preprocess(self):
        """The preprocessing steps:

        1. encode dataset, see :func:`encode_ordinal`.
        2. save encoded data as a transposed numpy array.
        3. calculate count matrix, see :func:`count_matrix`."""

        data, self.encoders = encode_ordinal(self.dataset)
        self.data_array = data.to_numpy().T

        # TODO: To avoid hanging, check matrix size and warn if too much
        self.count_matrix = get_count_matrix(
            self.data_array, self.dataset.metadata
        )

    def generate(self):
        """See generator function :func:`ipf`"""

        self.output = self.generator(
            self.data_array,
            counts=self.count_matrix,
            support=(self.count_matrix * 0 + 1).astype(int),
            size=self.size,
            **self.params
        )

    def postprocess(self):
        """Decodes output, see :func:`decode_ordinal` and saves as pd.DataFrame"""
        self.output = decode_ordinal(
            pd.DataFrame(self.output.T, columns=self.dataset.data.columns),
            self.encoders,
        )
