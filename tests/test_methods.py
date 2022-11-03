""" Tests that generators return syntactically correct dataframes """

import pandas as pd
import numpy as np
from reprosyn.methods import (
    IPF,
    MST,
    CTGAN,
    PATEGAN,
    PRIVBAYES,
    DS_INDHIST,
    DS_BAYNET,
    DS_PRIVBAYES,
    SYNTHPOP,
)


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
metadata = [
    {"name": "A", "type": "finite", "representation": ["a", "b", "c"]},
    {
        "name": "B",
        "type": "finite",
        "representation": ["0", "1", "2", "3", "4"],
    },
    {
        "name": "C",
        "type": "finite",
        "representation": ["one", "two", "three"],
    },
]


dummy = pd.DataFrame.from_dict(
    {c["name"]: choice(c["representation"], rows) for c in metadata}
)

names = [m["name"] for m in metadata]
domains = [m["representation"] for m in metadata]

synth_size = 50
epsilon = 1


def check_output(data):

    assert data.shape[0] == synth_size
    assert all(data.columns == names)

    # Check that synthetic domain is subset of data domain
    assert all(
        [
            set(data[col]) <= set(domains[i])
            for i, col in enumerate(data.columns)
        ]
    )


def test_ipf():
    ipf = IPF(
        dataset=dummy.copy(),
        metadata=metadata,
        size=synth_size,
        marginals=[(0, 1)],
    )
    ipf.run()
    check_output(ipf.output)


def test_mst():
    mst = MST(
        dataset=dummy.copy(),
        metadata=metadata,
        size=synth_size,
        epsilon=epsilon,
    )
    mst.run()
    check_output(mst.output)


def test_privbayes():
    pb = PRIVBAYES(dataset=dummy.copy(), metadata=metadata, size=synth_size)
    pb.run()
    check_output(pb.output)


def test_ctgan():
    ctgan = CTGAN(dataset=dummy.copy(), metadata=metadata, size=synth_size)
    ctgan.run()
    check_output(ctgan.output)


def test_PATEGAN():
    gen = PATEGAN(
        dataset=dummy.copy(),
        metadata=metadata,
        size=synth_size,
        batch_size=100,
    )
    gen.run()
    check_output(gen.output)


def test_SYNTHPOP():

    gen = SYNTHPOP(
        dataset=dummy.copy(),
        metadata=metadata,
        size=synth_size,
    )
    gen.run()
    check_output(gen.output)


def test_DS_INDHIST():
    gen = DS_INDHIST(dataset=dummy.copy(), metadata=metadata, size=synth_size)
    gen.run()
    check_output(gen.output)


def test_DS_BAYNET():
    gen = DS_BAYNET(dataset=dummy.copy(), metadata=metadata, size=synth_size)
    gen.run()
    check_output(gen.output)


def test_DS_PRIVBAYES():
    gen = DS_PRIVBAYES(
        dataset=dummy.copy(), metadata=metadata, size=synth_size
    )
    gen.run()
    check_output(gen.output)
