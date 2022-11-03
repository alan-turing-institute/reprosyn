from reprosyn.generator import PipelineBase


class RAW(PipelineBase):
    def __init__(self, replace=False, **kw):
        super().__init__(**kw, replace=replace)

    def preprocess(self):

        if not self.params["replace"]:
            self.size = min(self.size, len(self.dataset.data))

    def generate(self):
        self.output = self.dataset.data.sample(
            self.size, replace=self.params["replace"]
        )
