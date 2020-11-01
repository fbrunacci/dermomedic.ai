from injector import singleton
from flask_injector import request

from dermomedic.database import IDatabase, FSDatabase
from dermomedic.service import IService, Service
from dermomedic.neuralnet import IEfficientNet, Masdevallia
from dermomedic.analyser import IAnalyser, Analyser

def configure(binder):
    binder.bind(IDatabase, to=FSDatabase('/home/fabien/.deeplearning4j/data/analyser'), scope=singleton)
    binder.bind(IService, to=Service, scope=singleton)
    binder.bind(IAnalyser, to=Analyser, scope=singleton)
    binder.bind(IEfficientNet, to=Masdevallia, scope=singleton)
