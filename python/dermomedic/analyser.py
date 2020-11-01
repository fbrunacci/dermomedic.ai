from injector import inject
from dermomedic.neuralnet import Masdevallia
from dermomedic.database import IDatabase, Analyse
from dermomedic.neuralnet import IEfficientNet
import pathlib
import os
from multiprocessing import Pool
import time
from abc import ABC, abstractmethod


class IAnalyser(ABC):
    def __init__(self):
        pass

    def launch_analyse(self, analyse):
        pass


class Analyser(IAnalyser):

    @inject
    def __init__(self, db: IDatabase, neural_net: IEfficientNet):
        self.db = db
        self.neural_net = neural_net
        self.pool = Pool(processes=1)

    def launch_analyse(self, analyse):
        prediction = self.neural_net.predict_image('/home/fabien/.deeplearning4j/data/analyser/1.jpg')
        print(f'prediction: {prediction}')



