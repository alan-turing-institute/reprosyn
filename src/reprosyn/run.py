def run(gen, dataset=None, size=None, output_dir="./", **kwargs):
    generator = gen(
        dataset=dataset, output_dir=output_dir, size=size, **kwargs
    )
    generator.preprocess()
    generator.generate()
    generator.postprocess()
    generator.save()
    return generator
