"""MST

This is a generalization of the winning mechanism from the
2018 NIST Differential Privacy Synthetic Data Competition.
Unlike the original implementation, this one can work for any discrete
dataset, and does not rely on public provisional data for measurement
selection. Code from `private-pgm <https://github.com/ryan112358/private-pgm/blob/master/mechanisms/mst.py>`_
"""

import itertools
import json

import networkx as nx
import numpy as np
from disjoint_set import DisjointSet
from mbi import Dataset, Domain, FactoredInference
from scipy import sparse
from scipy.special import logsumexp

from reprosyn.methods.mbi.cdp2adp import cdp_rho
from reprosyn.generator import PipelineBase, encode_ordinal, decode_ordinal


def mst(data, epsilon, delta, rows):

    rho = cdp_rho(epsilon, delta)
    sigma = np.sqrt(3 / (2 * rho))
    cliques = [(col,) for col in data.domain]
    log1 = measure(data, cliques, sigma)
    data, log1, undo_compress_fn = compress_domain(data, log1)
    cliques = select(data, rho / 3.0, log1)
    log2 = measure(data, cliques, sigma)
    engine = FactoredInference(data.domain, iters=1000)
    est = engine.estimate(log1 + log2)
    synth = est.synthetic_data(rows)
    return undo_compress_fn(synth)


def measure(data, cliques, sigma, weights=None):

    if weights is None:
        weights = np.ones(len(cliques))
    weights = np.array(weights) / np.linalg.norm(weights)
    measurements = []
    for proj, wgt in zip(cliques, weights):
        x = data.project(proj).datavector()
        y = x + np.random.normal(loc=0, scale=sigma / wgt, size=x.size)
        Q = sparse.eye(x.size)
        measurements.append((Q, y, sigma / wgt, proj))
    return measurements


def compress_domain(data, measurements):
    supports = {}
    new_measurements = []
    for Q, y, sigma, proj in measurements:
        col = proj[0]
        sup = y >= 3 * sigma
        supports[col] = sup
        if supports[col].sum() == y.size:
            new_measurements.append((Q, y, sigma, proj))
        else:  # need to re-express measurement over the new domain
            y2 = np.append(y[sup], y[~sup].sum())
            I2 = np.ones(y2.size)
            I2[-1] = 1.0 / np.sqrt(y.size - y2.size + 1.0)
            y2[-1] /= np.sqrt(y.size - y2.size + 1.0)
            I2 = sparse.diags(I2)
            new_measurements.append((I2, y2, sigma, proj))
    undo_compress_fn = lambda data: reverse_data(data, supports)
    return transform_data(data, supports), new_measurements, undo_compress_fn


def exponential_mechanism(
    q, eps, sensitivity, prng=np.random, monotonic=False
):
    coef = 1.0 if monotonic else 0.5
    scores = coef * eps / sensitivity * q
    probas = np.exp(scores - logsumexp(scores))
    return prng.choice(q.size, p=probas)


def select(data, rho, measurement_log, cliques=[]):
    engine = FactoredInference(data.domain, iters=50)
    est = engine.estimate(measurement_log)

    weights = {}
    candidates = list(itertools.combinations(data.domain.attrs, 2))
    for a, b in candidates:
        xhat = est.project([a, b]).datavector()
        x = data.project([a, b]).datavector()
        weights[a, b] = np.linalg.norm(x - xhat, 1)

    T = nx.Graph()
    T.add_nodes_from(data.domain.attrs)
    ds = DisjointSet()

    for e in cliques:
        T.add_edge(*e)
        ds.union(*e)

    r = len(list(nx.connected_components(T)))
    epsilon = np.sqrt(8 * rho / (r - 1))
    for i in range(r - 1):
        candidates = [e for e in candidates if not ds.connected(*e)]
        wgts = np.array([weights[e] for e in candidates])
        idx = exponential_mechanism(wgts, epsilon, sensitivity=1.0)
        e = candidates[idx]
        T.add_edge(*e)
        ds.union(*e)

    return list(T.edges)


def transform_data(data, supports):
    df = data.df.copy()
    newdom = {}
    for col in data.domain:
        support = supports[col]
        size = support.sum()
        newdom[col] = int(size)
        if size < support.size:
            newdom[col] += 1
        mapping = {}
        idx = 0
        for i in range(support.size):
            mapping[i] = size
            if support[i]:
                mapping[i] = idx
                idx += 1
        assert idx == size
        df[col] = df[col].map(mapping)
    newdom = Domain.fromdict(newdom)
    return Dataset(df, newdom)


def reverse_data(data, supports):
    df = data.df.copy()
    newdom = {}
    for col in data.domain:
        support = supports[col]
        mx = support.sum()
        newdom[col] = int(support.size)
        idx, extra = np.where(support)[0], np.where(~support)[0]
        mask = df[col] == mx
        if extra.size == 0:
            pass
        else:
            df.loc[mask, col] = np.random.choice(extra, mask.sum())
        df.loc[~mask, col] = idx[df.loc[~mask, col]]
    newdom = Domain.fromdict(newdom)
    return Dataset(df, newdom)


def domain_from_metadata(metadata: list[dict]):
    """From the dataset metadata, return dictionary of column names and sizes

    Parameters
    ----------
    metadata : list[dict]
        metadata, see `Data Format <https://privacy-sdg-toolbox.readthedocs.io/en/latest/dataset-schema.html>`_

    Returns
    -------
    Dict
        Dictionary of feature:size
    """

    return {col["name"]: len(col["representation"]) for col in metadata}


class MST(PipelineBase):
    """Generator class for Maximum Spanning Tree algorithm.

    Parameters
    ----------
    epsilon : float
        privacy budget parameter
    delta : float
        privacy parameter

    Notes
    -----

    Uses the package `Private-PGM`. Code adapted from `private-pgm <https://github.com/ryan112358/private-pgm/blob/master/mechanisms/mst.py>`_

    Further reading:

        * `Mckenna et al 2021. Winning the NIST Contest: A scalable and general approach to differentially private synthetic data <https://arxiv.org/abs/2108.04978>`_.
        * `Mckenna et al 2019. Graphical-model based estimation and inference for differential privacy <https://arxiv.org/abs/1901.09136>`_.


    """

    generator = staticmethod(mst)

    def __init__(self, epsilon=1.0, delta=1e-9, **kw):
        parameters = {"epsilon": epsilon, "delta": delta}
        super().__init__(**kw, **parameters)

    def preprocess(self):
        """The preprocessing steps:

        1. encode dataset, see :func:`encode_ordinal`.
        2. Get domain from metadata. see :func:`domain_from_metadata`.
        3. Save encoded data as an mbi class ``Dataset``.

        """
        self.encoded_dataset, self.encoders = encode_ordinal(self.dataset)

        self.domain = domain_from_metadata(self.dataset.metadata)

        self.encoded_dataset = Dataset(
            self.encoded_dataset, Domain.fromdict(self.domain)
        )

    def generate(self):
        """See generator function :func:`mst`"""

        self.output = self.generator(
            self.encoded_dataset,
            self.params["epsilon"],
            self.params["delta"],
            self.size,
        )
        return self.output

    def postprocess(self):
        """Decodes output using :func:`decode_ordinal`"""

        self.output = decode_ordinal(self.output.df, self.encoders)

    def save(self, domain_fn="domain.json"):
        """Saves output, additional saves domain json"""
        super().save()
        with open(self.output_dir / domain_fn, "w") as outfile:
            json.dump(self.domain, outfile)
