
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)![tests](https://github.com/alan-turing-institute/reprosyn/actions/workflows/ci.yml/badge.svg) [![Documentation Status](https://readthedocs.org/projects/reprosyn/badge/?version=latest)](https://reprosyn.readthedocs.io/en/latest/?badge=latest)


# Reprosyn: synthesising tabular data

Reprosyn is a python library for generating synthetic data.

Reprosyn's aim is to wrap generators so that they can be easily used with same interface. See how to [add generators](https://reprosyn.readthedocs.io/en/latest/addingmethods.html).

It can be used either as a python package or a command-line tool.

The [Documentation](https://reprosyn.readthedocs.io/en/latest/index.html) is the best place to get started.

## Installation

You can install it via pip:

```
pip install git+https://github.com/alan-turing-institute/reprosyn.git
```

or, if using poetry:
```
poetry add git+https://github.com/alan-turing-institute/reprosyn.git#main
```

This will give you the command line tool `rsyn`, and the python package `reprosyn`.

Reprosyn uses poetry to manage dependencies. See the [poetry installation docs](https://python-poetry.org/docs/#installation) for how to install poetry on your system.

### Additional dependencies

Some dependencies are optional by default to support cross-platform use. If you are installing on mac it is recommended to install with an `--all-extras` flag. See the [installation documentation](https://reprosyn.readthedocs.io/en/latest/install.html) for more information.

## For developers

To install locally:

```bash
git clone https://github.com/alan-turing-institute/reprosyn
cd reprosyn
poetry install #installs package and dependences
poetry shell #opens environment in a subshell
rsyn --help
```

## Example Usage

The [Documentation](https://reprosyn.readthedocs.io/en/latest/index.html) is the best place to get started.

See also the [Examples notebook](https://github.com/alan-turing-institute/reprosyn/blob/main/examples/reprosyn_as_package.ipynb) for examples of using all methods.


## Related Projects

Reprosyn is under active development as a companion library for [Toolbox for Adversarial Privacy Auditing](https://github.com/alan-turing-institute/privacy-sdg-toolbox), to support research comparing synthetic data generators.

There are lots of other great synthetic data packages. Such as:

- [Synthetic Data Vault](https://github.com/sdv-dev/SDV)
- [SmartNoise SDK](https://github.com/opendp/smartnoise-sdk)

Note that some of Reprosyn's design is inspired by [QUIPP](https://github.com/alan-turing-institute/QUIPP-pipeline/).
