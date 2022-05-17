# Reprosyn: A tool for synthetising the census 1% teaching file.

A command-line tool that applies various synthetic data generation methods to the Census 1% teaching file.

Reprosyn is inspired by [QUIPP](https://github.com/alan-turing-institute/QUIPP-pipeline/tree/2011-census-microdata).

Example usage:

```
CENSUS=<census 1% file path>
rsyn mst --file $CENSUS

rsyn mst <  $CENSUS
```
