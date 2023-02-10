import paddle
import paddle.nn as nn
import pandas as pd
import numpy as np
import random

from ML.model import MyDataset, MyLSTMModel

data_path = 'ML/data_eval.csv'
data = pd.read_csv(data_path)
data.info()
print(data.head(3))
data = data.values
print(data.shape)

eval = np.array(data)
# print(eval.shape)


eval_dataset = MyDataset(eval,n_in=1,num_features=4)

paddle.set_device('gpu:0')
model = paddle.Model(MyLSTMModel())
model.load('model/final')
model.prepare(metrics=paddle.metric.Accuracy())
# callback = paddle.callbacks.VisualDL(log_dir='visualdl_log_dir')
# evaluate(eval_data, batch_size=1, log_freq=10, verbose=2, num_workers=0, callbacks=None, num_iters=None)
result = model.evaluate(eval_dataset,
               batch_size=1000,
               log_freq=10,
            #    callbacks=callback,
               verbose=1)
print(result)