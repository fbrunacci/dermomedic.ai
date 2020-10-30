from dermomedic.masdevallia import EfficientNet

prediction = EfficientNet.getInstance().predict_image('/home/fabien/Work/github/dermomedic.ai/python/data'
                                                      '/ISIC_0000013.jpg')
print(prediction)
