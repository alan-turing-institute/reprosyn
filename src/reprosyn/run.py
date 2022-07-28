def run(gen, dataset, output_dir, size, **kwargs):
    generator = gen(dataset=dataset, output_dir=output_dir, size=size, **kwargs)
    generator.preprocess()
    generator.generate()
    generator.postprocess()
    generator.save()
    return generator
