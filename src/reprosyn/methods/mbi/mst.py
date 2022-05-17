import itertools

#import click
#import networkx as nx
import numpy as np
import pandas as pd
#from disjoint_set import DisjointSet
from reprosyn.methods.mbi.cdp2adp import cdp_rho
from scipy import sparse
from scipy.special import logsumexp

def mstmain(dataset):

    """Runs mst on given data

    Returns
    -------
    Synthetic dataset of mbi type Dataset
    """
    # load data
    return dataset


if __name__ == "__main__":

    mstmain()

    """
    parser.add_argument("--dataset", help="dataset to use")
    parser.add_argument("--domain", help="domain to use")
    parser.add_argument("--epsilon", type=float, help="privacy parameter")
    parser.add_argument("--delta", type=float, help="privacy parameter")

    parser.add_argument("--degree", type=int,
                        help="degree of marginals in workload")
    parser.add_argument(
        "--num_marginals", type=int, help="number of marginals in workload"
    )
    parser.add_argument(
        "--max_cells",
        type=int,
        help="maximum number of cells for marginals in workload",
    )

    parser.add_argument("--save", type=str, help="path to save synthetic data")

    parser.set_defaults(**default_params())
    args = parser.parse_args()

    """
    # data = Dataset.load(args.dataset, args.domain)
