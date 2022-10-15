# Reprosyn: A tool for synthesising the census 1% teaching file.

A python package command-line tool that applies various synthetic data generation methods to the Census 1% teaching file.

Reprosyn is inspired by [QUIPP](https://github.com/alan-turing-institute/QUIPP-pipeline/tree/2011-census-microdata).

## Installation

Reprosyn uses poetry to manage dependencies. See the [poetry installation docs](https://python-poetry.org/docs/#installation) for how to install poetry on your system.

To test the package:

```bash
git clone https://github.com/alan-turing-institute/reprosyn
cd reprosyn
poetry install #installs package and dependences
poetry shell #opens environment in a subshell
rsyn --help
```

You can also install it via pip:

```
pip install git+https://github.com/alan-turing-institute/reprosyn
```

Example usage:

`rsyn [GLOBAL OPTIONS] [GENERATOR] [GENERATOR OPTIONS]` 

```
CENSUS=<census 1% file path>
rsyn --file $CENSUS mst

rsyn mst <  $CENSUS
```

You can also run the package from within another project, assuming you have poetry installed. Though currently you need to run this from within the root of the project: 

```
git clone https://github.com/alan-turing-institute/reprosyn
cd reprosyn
poetry install
poetry run rsyn --size 100 --file ./src/reprosyn/datasets/2011-census-microdata/2011-census-microdata-small.csv mst
```

**Jax/Jaxlib**: Note that by default jax and jaxlib, which are optional dependencies of the `mbi` package, are not installed since they are not available for Windows. To install them (which does not change current functionality but quietens warnings), use `poetry install -E jax`. 


## Building exe

Reprosyn also uses [pyinstaller](https://pyinstaller.org/en/stable/) to generate a binary file that can be executed outside of a python environment, as long as the machine spec is similar to the build machine. 

An executable makes it easier to distribute the package to non-python users.

To build the executable:

```
git clone https://github.com/alan-turing-institute/reprosyn
cd reprosyn
poetry install
poetry shell
pyinstaller src/reprosyn/cli.py --onefile --name rsyn 
```

This will produce a `build` and a `dist` folder. Deactivate the environment and you can run the binary in the `dist` folder: `./dist/rsyn`
