import paddle
import paddle.nn as nn
import pandas as pd
import numpy as np
import random

from ML.model import MyDataset, MyLSTMModel

data_path = 'ML/data.csv'
data = pd.read_csv(data_path)
data.info()
print(data.head(3))
data = data.values
print(data.shape)

train = []
test = []
for i in data:
    n = random.randint(0,10)
    if n > 8:
        test.append(i)
    else:
        train.append(i)
train = np.array(train)
test = np.array(test)
print('train shape: ', train.shape)
print('test shape: ', test.shape)


train_dataset = MyDataset(train,n_in=1,num_features=4)
test_dataset = MyDataset(test,n_in=1,num_features=4)

paddle.set_device('gpu:0')  # can only be used on AI Studio
# paddle.set_device('cpu')
model = paddle.Model(MyLSTMModel())
# model.load('model/final')
model.prepare(optimizer=paddle.optimizer.Adam(learning_rate=0.001, parameters=model.parameters()),
              loss=paddle.nn.MSELoss(reduction='mean'))
callback = paddle.callbacks.VisualDL(log_dir='visualdl_log_dir')
model.fit(train_dataset,
          eval_data=test_dataset,
          eval_freq=1,
          epochs=100,
          batch_size=10000,
          save_dir='model',
          log_freq=100,
          save_freq=10,
          shuffle=True, 
          drop_last=True,
          callbacks=callback,
          verbose=1)
model.save('inference_model/LSTMModel', training=False)