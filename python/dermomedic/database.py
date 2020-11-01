import glob
from pathlib import Path
from abc import ABC, abstractmethod
from dermomedic.model import Analyse
import json


class IDatabase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def read_analyse(self, idx) -> Analyse:
        pass

    @abstractmethod
    def create_analyse(self, file_name, extension) -> Analyse:
        pass

    @abstractmethod
    def save_analyse(self, analyse: Analyse):
        pass

    @abstractmethod
    def save_prediction(self, analyse: Analyse, prediction):
        pass

    @abstractmethod
    def save_image(self, analyse, uploaded_file):
        pass


class FSDatabase(IDatabase):
    def __init__(self, upload_dir):
        self.upload_dir = upload_dir
        self.biggestId = max(self.ids(), default=0)

    def read_analyse(self, idx) -> Analyse:
        with open(f'{self.upload_dir}/{idx}.idx') as json_file:
            analyse_dict = json.load(json_file)
        return Analyse(**analyse_dict)

    def create_analyse(self, file_name, extension) -> Analyse:
        idx = self.next_id()
        new_analyse = Analyse(idx, file_name, extension)
        self.save_analyse(new_analyse)
        return self.read_analyse(idx)

    def save_analyse(self, analyse: Analyse):
        idx = analyse.idx
        with open(f'{self.upload_dir}/{idx}.idx', 'w') as json_file:
            json.dump(analyse.__dict__, json_file)

    def save_prediction(self, analyse: Analyse, prediction):
        analyse.malingantEvaluation = prediction
        self.save_analyse(analyse)

    def save_image(self, analyse, uploaded_file):
        file_path = f'{self.upload_dir}/{analyse.idx}.{analyse.extension}'
        print(f'saving image to {file_path}')
        uploaded_file.save(file_path)

    def ids(self):
        return list(map(lambda x: int(Path(x).stem), glob.glob(f'{self.upload_dir}/*.idx')))

    def next_id(self) -> int:
        self.biggestId += 1
        return self.biggestId


if __name__ == '__main__':
    db = IDatabase('/home/fabien/.deeplearning4j/data/analyser')
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
