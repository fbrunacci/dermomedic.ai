from dermomedic import database, neuralnet, model
from multiprocessing import Pool


class Analyser:

    def __init__(self, db: database.FSDatabase, neural_net: neuralnet.Masdevallia):
        self.db = db
        self.neural_net = neural_net
        self.pool = Pool(processes=1)

    def launch_analyse(self, analyse: model.Analyse):
        print(f'launch_analyse on {analyse}')
        img = self.db.get_image_path(analyse)
        prediction = self.neural_net.predict_image(img)
        print(f'prediction: {prediction}')
        analyse.malingantEvaluation = prediction[0][0].item()
        print(f'after prediction: {analyse}')
        self.db.save_analyse(analyse)



