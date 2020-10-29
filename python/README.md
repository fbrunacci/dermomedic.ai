# isic masdevallia isic 

## init/config sample

### venv
virtualenv venv --python=python3.6.10
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

### model
Get model from
https://www.kaggle.com/masdevallia/melanoma-classification-3rd-place-models?select=EfficientNetB6_512x512_2019-2020_epoch12_auc_0.97.h5

or
cd model
wget http://u2py.com/dermomedic/EfficientNetB6_512x512_2019-2020_epoch12_auc_0.97.h5

### data
And get sample data from 
https://www.kaggle.com/cdeotte/melanoma-512x512

or
cd data
wget http://u2py.com/dermomedic/test13-687.tfrec
wget http://u2py.com/dermomedic/train14-2174.tfrec


