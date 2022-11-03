Installation
============

The simplest install is using pip or poetry.

.. code-block:: bash

    pip install git+https://github.com/alan-turing-institute/reprosyn

.. code-block:: bash

    poetry add git+https://github.com/alan-turing-institute/reprosyn.git#main


This will give a command line tool, `rsyn`, and the python package `reprosyn`.

Dependencies 
------------

Reprosyn uses poetry to manage dependencies. See the  `poetry installation docs <https://python-poetry.org/docs/#installation>`_ for how to install poetry on your system.

Some dependencies do not work well on Windows, or have large sub-dependencies, so are optional by default. 

For optional dependences, see the header ``[tool.poetry.extras]`` in `pyproject.toml <https://github.com/alan-turing-institute/reprosyn/blob/main/pyproject.toml>`_. Briefly: 

- **Jax/Jaxlib**: These optional dependencies of the `mbi` package and are not installed by default. They do not change functionality.
- **Ektelo**: A dependency of an `mbi` privbayes implementation `Ektelo <https://github.com/callummole/ektelo>`_ that relies on C++. Install with ``poetry install -E ektelo``.


Developers
----------

If you are wanting to develop the package you may want to install additional poetry groups. See headers like ``[tool.poetry.group.*]`` in the `pyproject.toml` file.

.. code-block:: bash

    git clone https://github.com/alan-turing-institute/reprosyn
    cd reprosyn
    poetry install --with dev, docs #installs developer and documentation dependencies.


Building an executable
----------------------

Reprosyn also uses `pyinstaller <https://pyinstaller.org/en/stable/>`_ to generate a binary file that can be executed outside of a python environment, as long as the machine spec is similar to the build machine. 

An executable makes it easier to distribute the package to non-python users.

To build the executable:

.. code-block:: bash

    git clone https://github.com/alan-turing-institute/reprosyn
    cd reprosyn
    poetry install
    poetry shell
    pyinstaller src/reprosyn/cli.py --onefile --name rsyn 

This will produce a ``build`` and a ``dist`` folder. Deactivate the environment and you can run the binary in the ``dist`` folder: ``./dist/rsyn``
