import glob
from pathlib import Path
from dermomedic.model import Analyse
import json


class FSDatabase:
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
        file_path = self.get_image_path(analyse)
        print(f'saving image to {file_path}')
        uploaded_file.save(file_path)

    def get_image_path(self, analyse):
        return f'{self.upload_dir}/{analyse.idx}.{analyse.extension}'

    def ids(self):
        return list(map(lambda x: int(Path(x).stem), glob.glob(f'{self.upload_dir}/*.idx')))

    def next_id(self) -> int:
        self.biggestId += 1
        return self.biggestId

