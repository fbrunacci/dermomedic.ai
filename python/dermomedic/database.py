import json
import glob
from pathlib import Path


class Analyse:
    def __init__(self, idx, fileName, extension, malingantEvaluation):
        self.idx = idx
        self.fileName = fileName
        self.extension = extension
        self.malingantEvaluation = malingantEvaluation

    def __str__(self):
        return json.dumps(self.__dict__)


class Database:

    def __init__(self, upload_dir):
        self.upload_dir = upload_dir
        self.biggestId = max(self.ids())

    def read_analyse(self, idx) -> Analyse:
        with open(f'{self.upload_dir}/{idx}.idx') as json_file:
            analyse_dict = json.load(json_file)
        return Analyse(**analyse_dict)

    def create_analyse(self, fileName, extension) -> Analyse:
        idx = self.next_id()
        new_analyse = Analyse(idx, fileName, extension, None)
        self.save_analyse(new_analyse)
        return self.read_analyse(idx)

    def save_analyse(self, analyse: Analyse):
        idx = analyse.idx
        with open(f'{self.upload_dir}/{idx}.idx', 'w') as json_file:
            json.dump(analyse.__dict__, json_file)

    def save_prediction(self, analyse: Analyse, prediction):
        analyse.malingantEvaluation = prediction
        self.save_analyse(analyse)

    def ids(self):
        return list(map(lambda x: int(Path(x).stem), glob.glob(f'{self.upload_dir}/*.idx')))

    def next_id(self) -> int:
        self.biggestId += 1
        return self.biggestId


if __name__ == '__main__':
    db = Database('/home/fabien/.deeplearning4j/data/analyser')
    analyse = db.read_analyse(1)
    print(analyse.malingantEvaluation)
    cc = db.create_analyse("fileName", "ext")
    print(cc)
    cc.malingantEvaluation = 0.42
    db.save_analyse(cc)

    # print(db)
    # analyse = db.read_analyse(1)
    # print(analyse)
    # analyse.malingantEvaluation = 0.001
    # print(analyse)
    # db.save_analyse(analyse)
    # print(db.read_analyse(1))
    # print(db.ids())
    # print(db.biggestId)
    # print(db.next_id())
    # print(db.biggestId)
