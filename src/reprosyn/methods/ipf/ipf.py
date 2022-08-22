import pandas as pd
import numpy as np
import random as rnd
from tqdm import tqdm
import string

from reprosyn.generator import (
    GeneratorFunc,
    recode_as_category,
    recode_as_original,
)


def get_count_matrix(X):

    """
    Returns the counts of each feature category.

    X is a numpy array with shape (features, individuals).
    count_matrix is a numpy array with ndims = nfeatures and shape determined by the feature categories, e.g. (ncatg1, ncatg2,...)
    """
    count_matrix = np.zeros(
        X.max(axis=1) + 1, dtype=np.uint16
    )  # assumes no cell will have more than 65k persons in it...

    for i in range(X.shape[1]):
        count_matrix[tuple(X.T[i])] += 1

    return count_matrix


def get_margin_grids(X, count_matrix, known_marginals):

    """
    Create some collections of dimensions where the marginal counts are known.
    These will be matched by the sinkhorn algorithm

    X is a numpy array with shape (features, individuals).
    known_marginals should be *ordered* tuples (to save checking ordering issues later...)

    margin_grids is list of len(known_marginals) with entries [known_marginals[i], ndarray]
    """

    dim_set = set(range(X.shape[0]))
    margin_grids = [
        (x, count_matrix.sum(axis=tuple(dim_set - set(x))))
        for x in known_marginals
    ]
    return margin_grids


# Helper function to construct Einstein sum definition strings
def _einsum_construct(ind, full_dim=5):
    alpha = string.ascii_lowercase
    string_pre = alpha[:full_dim] + ","
    string_mid = "".join([alpha[x] for x in ind])
    string_end = "->abcde"
    return string_pre + string_mid + string_end


# A version of iterative proportional fitting algorithm, in high dimension, with multivariate marginals
# Attempts to convert initial_tensor to have specified marginals
# If initial_tensor is constant, then it will yield the maximum entropy distribution with specified marginals
def sinkhorn_tensor(
    initial_tensor,
    marginals,
    max_iterations=1e4,
    iter_tolerance=5e-1,
    eps=1e-5,
    verbose=False,
):

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
        if verbose:
            print(count, err)

    return initial_tensor


def sampler(N, probability_array):
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


def ipf(data, marginals, counts, support, size, iter_tolerance=1e-3 * 1000):

    margin_grids = get_margin_grids(data, counts, marginals)

    approx_count = sinkhorn_tensor(support, margin_grids, iter_tolerance)

    approx_sample = sampler(size, approx_count)

    return approx_sample


class IPF(GeneratorFunc):
    """Generator class for Iterative Proportional Fitting"""

    generator = staticmethod(ipf)

    def __init__(self, marginals=[(0, 1), (3, 4), (1, 2, 3)], **kw):
        parameters = {
            "marginals": marginals,
        }
        super().__init__(**kw, **parameters)

    def preprocess(self):
        self.dataset, self.mapping = recode_as_category(self.dataset)

        data = np.array(self.dataset).T
        self.count_matrix = get_count_matrix(data)
        self.support_matrix = (self.count_matrix * 0 + 1).astype(int)

    def generate(self):
        data = np.array(self.dataset).T
        self.output = self.generator(
            data,
            self.count_matrix,
            self.support_matrix,
            self.params["marginals"],
            self.size,
        )

    def postprocess(self):
        self.output = recode_as_original(
            pd.DataFrame(self.output, cols=self.dataset.columns), self.mapping
        )
