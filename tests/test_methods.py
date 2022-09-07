""" Tests that generators return syntactically correct dataframes """

import pandas as pd
import numpy as np
from reprosyn.methods import IPF, MST


def choice(arr, n):
    rng = np.random.default_rng()
    if isinstance(arr, np.ndarray):
        out = rng.choice(arr, n)
    elif isinstance(arr, list):
        out = [arr[i] for i in rng.choice(len(arr), n)]
    else:
        raise "unrecognised type"
    return out


rows = 100
names = ["A", "B"]
domains = [["a", "b", "c"], np.arange(5)]

dummy = pd.DataFrame.from_dict(
    {n: choice(d, rows) for n, d in zip(names, domains)}
)

synth_size = 50
epsilon = 1


def check_output(data):

    assert data.shape[0] == synth_size
    assert all(data.columns == names)

    # Check that the domains are identical (needs enough samples to cover domain)
    assert all(
        [
            set(data[col]) == set(domains[i])
            for i, col in enumerate(data.columns)
        ]
    )


def test_mst():
    mst = MST(dataset=dummy.copy(), size=synth_size, epsilon=epsilon)
    mst.run()
    check_output(mst.output)


def test_ipf():
    ipf = IPF(
        dataset=dummy.copy(),
        size=synth_size,
        marginals=[(0, 1)],
        epsilon=epsilon,
    )
    ipf.run()
    check_output(ipf.output)
