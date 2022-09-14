import itertools
import json

import numpy as np
import pandas as pd
import privBayesSelect  # should be ektelo.algorithm.privbayes, but I'm struggling with using cython and poetry.
from ektelo.matrix import Identity
from mbi import Dataset, Domain, Factor

from reprosyn.generator import (
    GeneratorFunc,
    recode_as_category,
    recode_as_original,
)

"""
Code adapted from https://github.com/ryan112358/private-pgm/blob/master/examples/privbayes.py


This file implements PrivBayes, with and without graphical-model based inference.
Zhang, Jun, Graham Cormode, Cecilia M. Procopiuc, Divesh Srivastava, and Xiaokui Xiao. "Privbayes: Private data release via bayesian networks." ACM Transactions on Database Systems (TODS) 42, no. 4 (2017): 25.
"""


def privbayes_measurements(data, eps=1.0, seed=0):
    domain = data.domain
    config = ""
    for a in domain:
        values = [str(i) for i in range(domain[a])]
        config += "D " + " ".join(values) + " \n"
    config = config.encode("utf-8")

    values = np.ascontiguousarray(data.df.values.astype(np.int32))
    ans = privBayesSelect.py_get_model(values, config, eps / 2, 1.0, seed)
    ans = ans.decode("utf-8")[:-1]

    projections = []
    for m in ans.split("\n"):
        p = [domain.attrs[int(a)] for a in m.split(",")[::2]]
        projections.append(tuple(p))

    prng = np.random.RandomState(seed)
    measurements = []
    delta = len(projections)
    for proj in projections:
        x = data.project(proj).datavector()
        I = Identity(x.size)
        y = I.dot(x) + prng.laplace(loc=0, scale=4 * delta / eps, size=x.size)
        measurements.append((I, y, 1.0, proj))

    return measurements


def privbayes_inference(domain, measurements, total):
    synthetic = pd.DataFrame()

    _, y, _, proj = measurements[0]
    y = np.maximum(y, 0)
    y /= y.sum()
    col = proj[0]
    synthetic[col] = np.random.choice(domain[col], total, True, y)

    for _, y, _, proj in measurements[1:]:
        # find the CPT
        col, dep = proj[0], proj[1:]
        # print(col)
        y = np.maximum(y, 0)
        dom = domain.project(proj)
        cpt = Factor(dom, y.reshape(dom.shape))
        marg = cpt.project(dep)
        cpt /= marg
        cpt2 = np.moveaxis(cpt.project(proj).values, 0, -1)

        # sample current column
        synthetic[col] = 0
        rng = itertools.product(*[range(domain[a]) for a in dep])
        for v in rng:
            idx = (synthetic.loc[:, dep].values == np.array(v)).all(axis=1)
            p = cpt2[v].flatten()
            if p.sum() == 0:
                p = np.ones(p.size) / p.size
            n = domain[col]
            N = idx.sum()
            if N > 0:
                synthetic.loc[idx, col] = np.random.choice(n, N, True, p)

    return Dataset(synthetic, domain)


def privbayes(dataset, epsilon, seed, size):

    measurements = privbayes_measurements(dataset, epsilon, seed)

    output = privbayes_inference(dataset.domain, measurements, size)

    return output


def get_domain_dict(data):

    return dict(zip(data.columns, data.nunique()))


def domain_from_metadata(metadata: list[dict]):

    return {col["name"]: len(col["representation"]) for col in metadata}


class PRIVBAYES(GeneratorFunc):
    """Generator class for the MST mechanism."""

    generator = staticmethod(privbayes)

    def __init__(self, epsilon=1.0, seed=0, **kw):
        parameters = {
            "epsilon": epsilon,
            "seed": seed,
        }
        super().__init__(**kw, **parameters)

    def preprocess(self):
        df, mapping = recode_as_category(self.dataset)
        self.mapping = mapping

        # domain could be json
        self.domain = domain_from_metadata(self.metadata)

        self.dataset = Dataset(df, Domain.fromdict(self.domain))

    def generate(self):
        self.output = self.generator(
            self.dataset,
            self.params["epsilon"],
            self.params["seed"],
            self.size,
        )
        return self.output

    def postprocess(self):
        self.output = recode_as_original(self.output.df, self.mapping)

    def save(self, domain_fn="domain.json"):
        super().save()
        with open(self.output_dir / domain_fn, "w") as outfile:
            json.dump(self.domain, outfile)
