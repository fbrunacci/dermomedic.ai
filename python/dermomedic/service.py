from dermomedic.database import FSDatabase, Analyse
import pathlib
import os
from multiprocessing import Pool


class DermomedicService:

    def __init__(self, db: FSDatabase):
        self.db = db
        self.pool = Pool(processes=1)

    def create_analyse(self, filename):
        file_name_no_ext = pathlib.Path(filename).resolve().stem
        extension = os.path.splitext(filename)[1][1:]
        return self.db.create_analyse(file_name_no_ext, extension)

    def read_analyse(self, idx):
        return self.db.read_analyse(idx)

    def save_image(self, analyse: Analyse, uploaded_file):
        self.db.save_image(analyse, uploaded_file)

    def process_analyse(self, uploaded_file):
        new_analyse = self.create_analyse(uploaded_file.filename)
        self.save_image(new_analyse, uploaded_file)
        return new_analyse

