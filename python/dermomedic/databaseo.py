import json
from types import SimpleNamespace


class Database:

    def __init__(self, upload_dir):
        self.upload_dir = upload_dir

    def read_analyse(self, idx):
        with open(f'{self.upload_dir}/{idx}.idx') as json_file:
            analyse = json.load(json_file)
        return analyse

    def save_analyse(self, analyse):
        idx = analyse['id']
        with open(f'{self.upload_dir}/{idx}.idx', 'w') as json_file:
            json.dump(analyse, json_file)

    def save_prediction(self, analyse, prediction):
        analyse['malingantEvaluation'] = prediction
        self.save_analyse(analyse)


class Analyse():
    def __init__(self, id, fileName, extension , malingantEvaluation):
        self.id = id
        self.fileName = fileName
        self.extension = extension
        self.malingantEvaluation = malingantEvaluation


if __name__ == '__main__':
    db = Database('/home/fabien/.deeplearning4j/data/analyser')
    print(db)
    analyse = db.read_analyse(1)
    print(analyse)
    analyse['malingantEvaluation'] = 0.001
    print(analyse)
    db.save_analyse(analyse)
    db.save_prediction(analyse, 0.24244242)
    print(db.read_analyse(1))
