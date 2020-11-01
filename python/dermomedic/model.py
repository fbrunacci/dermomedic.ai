import json

class Analyse:
    def __init__(self, idx, fileName, extension, malingantEvaluation = None):
        self.idx = idx
        self.fileName = fileName
        self.extension = extension
        self.malingantEvaluation = malingantEvaluation

    def __str__(self):
        return json.dumps(self.__dict__)
