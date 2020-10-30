import tensorflow as tf
from tensorflow.keras.models import load_model
import datetime
import os, random, re, math, time
from glob import glob
import numpy as np
import pandas as pd
import tensorflow.keras.backend as K
import efficientnet.tfkeras as efn
import PIL


class EfficientNet:
    __instance = None
    GCS_PATH = './data/'
    files_train = np.sort(np.array(tf.io.gfile.glob(GCS_PATH + 'train14-2174.tfrec')))
    files_test = np.sort(np.array(tf.io.gfile.glob(GCS_PATH + 'test13-687.tfrec')))
    AUTO = tf.data.experimental.AUTOTUNE

    CFG = dict(
        read_size = 512,
        crop_size = 500,
        net_size = 500,

        # DATA AUGMENTATION
        rot = 180.0,
        shr = 1.5,
        hzoom = 6.0,
        wzoom = 6.0,
        hshift = 6.0,
        wshift = 6.0,
        
        # COARSE DROPOUT
        DROP_FREQ = 0, # Determines proportion of train images to apply coarse dropout to / Between 0 and 1.
        DROP_CT = 0, # How many squares to remove from train images when applying dropout.
        DROP_SIZE = 0, # The size of square side equals IMG_SIZE * DROP_SIZE / Between 0 and 1.  
        
        optimizer = 'adam',
        label_smooth_fac = 0.05,
        tta_steps =  25
    )
    model_B6 = load_model('./model/EfficientNetB6_512x512_2019-2020_epoch12_auc_0.97.h5')

    @staticmethod 
    def getInstance():
        """ Static access method. """
        if EfficientNet.__instance == None:
            EfficientNet()
        return EfficientNet.__instance
    def __init__(self):
        """ Virtually private constructor. """
        if EfficientNet.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            EfficientNet.__instance = self

    def read_unlabeled_tfrecord(self, example, return_image_name):
        tfrec_format = {
            'image'                        : tf.io.FixedLenFeature([], tf.string),
            'image_name'                   : tf.io.FixedLenFeature([], tf.string),
        }
        example = tf.io.parse_single_example(example, tfrec_format)
        return example['image'], example['image_name'] if return_image_name else 0

    def read_labeled_tfrecord(self, example):
        tfrec_format = {
            'image'                        : tf.io.FixedLenFeature([], tf.string),
            'image_name'                   : tf.io.FixedLenFeature([], tf.string),
            'patient_id'                   : tf.io.FixedLenFeature([], tf.int64),
            'sex'                          : tf.io.FixedLenFeature([], tf.int64),
            'age_approx'                   : tf.io.FixedLenFeature([], tf.int64),
            'anatom_site_general_challenge': tf.io.FixedLenFeature([], tf.int64),
            'diagnosis'                    : tf.io.FixedLenFeature([], tf.int64),
            'target'                       : tf.io.FixedLenFeature([], tf.int64)
        }           
        example = tf.io.parse_single_example(example, tfrec_format)
        return example['image'], example['target']

    def transform(self, image, cfg):    
        # input image - is one image of size [dim,dim,3] not a batch of [b,dim,dim,3]
        # output - image randomly rotated, sheared, zoomed, and shifted
        DIM = cfg["read_size"]
        XDIM = DIM%2 #fix for size 331
        
        rot = cfg['rot'] * tf.random.normal([1], dtype='float32')
        shr = cfg['shr'] * tf.random.normal([1], dtype='float32') 
        h_zoom = 1.0 + tf.random.normal([1], dtype='float32') / cfg['hzoom']
        w_zoom = 1.0 + tf.random.normal([1], dtype='float32') / cfg['wzoom']
        h_shift = cfg['hshift'] * tf.random.normal([1], dtype='float32') 
        w_shift = cfg['wshift'] * tf.random.normal([1], dtype='float32') 

        # GET TRANSFORMATION MATRIX
        m = get_mat(rot,shr,h_zoom,w_zoom,h_shift,w_shift)

        # LIST DESTINATION PIXEL INDICES
        x   = tf.repeat(tf.range(DIM//2, -DIM//2,-1), DIM)
        y   = tf.tile(tf.range(-DIM//2, DIM//2), [DIM])
        z   = tf.ones([DIM*DIM], dtype='int32')
        idx = tf.stack( [x,y,z] )
        
        # ROTATE DESTINATION PIXELS ONTO ORIGIN PIXELS
        idx2 = K.dot(m, tf.cast(idx, dtype='float32'))
        idx2 = K.cast(idx2, dtype='int32')
        idx2 = K.clip(idx2, -DIM//2+XDIM+1, DIM//2)
        
        # FIND ORIGIN PIXEL VALUES           
        idx3 = tf.stack([DIM//2-idx2[0,], DIM//2-1+idx2[1,]])
        d    = tf.gather_nd(image, tf.transpose(idx3))
            
        return tf.reshape(d,[DIM, DIM,3])

    def get_mat(self, rotation, shear, height_zoom, width_zoom, height_shift, width_shift):
        # returns 3x3 transformmatrix which transforms indicies
            
        # CONVERT DEGREES TO RADIANS
        rotation = math.pi * rotation / 180.
        shear = math.pi * shear / 180.

        def get_3x3_mat(lst):
            return tf.reshape(tf.concat([lst],axis=0), [3,3])
        
        # ROTATION MATRIX
        c1   = tf.math.cos(rotation)
        s1   = tf.math.sin(rotation)
        one  = tf.constant([1],dtype='float32')
        zero = tf.constant([0],dtype='float32')
        
        rotation_matrix = get_3x3_mat([c1,   s1,   zero, 
                                    -s1,  c1,   zero, 
                                    zero, zero, one])    
        # SHEAR MATRIX
        c2 = tf.math.cos(shear)
        s2 = tf.math.sin(shear)    
        
        shear_matrix = get_3x3_mat([one,  s2,   zero, 
                                    zero, c2,   zero, 
                                    zero, zero, one])        
        # ZOOM MATRIX
        zoom_matrix = get_3x3_mat([one/height_zoom, zero,           zero, 
                                zero,            one/width_zoom, zero, 
                                zero,            zero,           one])    
        # SHIFT MATRIX
        shift_matrix = get_3x3_mat([one,  zero, height_shift, 
                                    zero, one,  width_shift, 
                                    zero, zero, one])
        
        return K.dot(K.dot(rotation_matrix, shear_matrix), 
                    K.dot(zoom_matrix,     shift_matrix))

    def prepare_image(self, img, cfg=None):
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, [cfg['read_size'], cfg['read_size']])
        img = tf.cast(img, tf.float32) / 255.0 # # Cast and normalize the image to [0,1]
        img = tf.image.central_crop(img, cfg['crop_size'] / cfg['read_size'])
        img = tf.image.resize(img, [cfg['net_size'], cfg['net_size']])
        img = tf.reshape(img, [cfg['net_size'], cfg['net_size'], 3])        
        return img

    def predict_image(self, img_path):
        hh = tf.io.read_file(img_path)
        images_tf = tf.convert_to_tensor(hh)
        images_prepared = tf.reshape(self.prepare_image(images_tf,cfg=self.CFG), [1, 500, 500, 3])
        preds = self.model_B6.predict((images_prepared, tf.reshape(0, [1])), verbose=1)
        return preds



