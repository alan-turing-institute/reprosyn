# Reprosyn: A tool for synthetising the census 1% teaching file.

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

Example usage:

```
CENSUS=<census 1% file path>
rsyn mst --file $CENSUS

rsyn mst <  $CENSUS
```

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

