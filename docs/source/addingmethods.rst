Adding Methods
==============

There are two ways of adding methods, into the package itself, or dynamically at the command line.

For a method to be `Reprosyn Method`, it simply needs to subclass the ``PipelineBase`` class. The class is a minimal wrapper so that all generators can be called with a consistent interface.

Any `method parameters` should be passed to the parent class as a keyword dictionary, these get saved as ``self.params`` for later use. 

A template:

.. code-block:: python

    from reprosyn.generator import PipelineBase, encode_ordinal, decode_ordinal

    def mymodel(data, size, param1, param2, param3):
        # generate synthetic data

    class MyMethod(PipelineBase):
    
        generator = staticmethod(mymodel)

        def __init__(
            self,
            param1, 
            param2, 
            param3, 
            **kw
        ):
            
            params = {
                "param1": param1,
                "param2": param2,
                "param3": param3,
            }
            super().__init__(**kw, **params)

        def preprocess(self):
            self.encoded_data, self.encoders = encode_ordinal(self.dataset)

        def generate(self):

            self.output = self.generator(
                data = self.encoded_data
                size = self.size,
                **self.params
            )

        def postprocess(self):
            self.output = decode_ordinal(
                self.output
                self.encoders,
            )



The class is flexible. For example, it is common for methods to separate ``fit`` and ``sample`` stages. You can do this easily:

.. code-block:: python

    class MyMethod(PipelineBase):

        def __init__(
            self,
            param1, 
            param3, 
            **kw
        ):
            
            params = {
                "param1": param1,
            }

            self.fit = None

            super().__init__(**kw, **params)


        def generate(self, refit=False):

            if (not self.fit) or refit:
                self.fit = FitModel(**self.params)

            self.output = self.fit.sample(self.size)



.. note::
    Most generation methods require metadata about the type and extent of data features. It is vital that this information is provided separately to the dataset so that the metadata is resistent to change if a new dataset was sampled (which can leak information).

    Reprosyn uses this `metadata specification <https://privacy-sdg-toolbox.readthedocs.io/en/latest/dataset-schema.html>`_.

    Generators often have bespoke metadata that they recognise. Developers will probably need to add a preprocessing method to translate the Reprosyn format into a form that makes sense to the generator.




Adding a Reprosyn method
------------------------
 
It is simple to add a method into the package. Do the following:

1) Make a new folder in `Methods <https://github.com/alan-turing-institute/reprosyn/tree/main/src/reprosyn/methods>`_.

2) Add a file named after your method ``<method.py>``. Inside there should be a method class as described above.

3) For convenience, in `methods.__init__ <https://github.com/alan-turing-institute/reprosyn/blob/main/src/reprosyn/methods/__init__.py>`_ add your method, so that it will be available simply as ``from reprosyn.methods import MyMethod``

4) Add a test named after your methods to `test_methods.py <https://github.com/alan-turing-institute/reprosyn/blob/main/tests/test_methods.py>`_. These tests simply check if the method runs and returns recognisable data.


To add your method to **CLI**, do the following:

5) Add a file ``cli.py`` in your method folder. Template:

.. code-block:: python

    import click

    from reprosyn.generator import wrap_generator
    from reprosyn.methods import MyMethod

    @click.command(
        "method",
        short_help="hey it's a new method",
        options_metavar="[GENERATOR OPTIONS]",
    )
    @click.option(
        "--param1",
        type=int,
        default=1,
        help="first parameter",
    )
    @wrap_generator # a helper function so that you can pass data using STDIN
    def cmd_method(h, **kwargs):
        """Here put help to show on rsyn method --help
        """
        generator = MyMethod(dataset=h.file, size=h.size, output_dir=h.out, **kwargs)
        generator.run()
        return generator.output

6) Finally add your command to the ``COMMAND`` group in `methods.__init__ <https://github.com/alan-turing-institute/reprosyn/blob/main/src/reprosyn/methods/__init__.py>`_. This will get automatically added to the main click command group.

Adding a Method dynamically
---------------------------

TODO: Merge PR and document
