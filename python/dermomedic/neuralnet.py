import tensorflow as tf
from tensorflow.keras.models import load_model
import os
import efficientnet.tfkeras as efn
from abc import ABC, abstractmethod


class IEfficientNet(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def predict_image(self, img_path):
        pass


class Masdevallia(IEfficientNet):
    AUTO = tf.data.experimental.AUTOTUNE

    def __init__(self):
        flask_path = os.path.dirname(os.path.realpath(__file__))
        model_path = f'{flask_path}/../model/EfficientNetB6_512x512_2019-2020_epoch12_auc_0.97.h5'
        efn.EfficientNetB6
        self.neural_net = load_model(model_path)

    CFG = dict(
        read_size=512,
        crop_size=500,
        net_size=500,
    )

    def prepare_image(self, img, cfg=None):
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, [cfg['read_size'], cfg['read_size']])
        img = tf.cast(img, tf.float32) / 255.0  # # Cast and normalize the image to [0,1]
        img = tf.image.central_crop(img, cfg['crop_size'] / cfg['read_size'])
        img = tf.image.resize(img, [cfg['net_size'], cfg['net_size']])
        img = tf.reshape(img, [cfg['net_size'], cfg['net_size'], 3])
        return img

    def predict_image(self, img_path):
        hh = tf.io.read_file(img_path)
        images_tf = tf.convert_to_tensor(hh)
        images_prepared = tf.reshape(self.prepare_image(images_tf, cfg=self.CFG), [1, 500, 500, 3])
        prediction = self.neural_net.predict((images_prepared, tf.reshape(0, [1])), verbose=1)
        return prediction


if __name__ == '__main__':
    # print(EfficientNet.model_path)
    # load_model(EfficientNet.model_path)
    Masdevallia()
    Masdevallia().predict_image('/home/fabien/.deeplearning4j/data/analyser/1.jpg')
