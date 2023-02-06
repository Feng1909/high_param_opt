import paddle
import paddle.nn as nn
import numpy as np


class MyLSTMModel(nn.Layer):
    def __init__(self):
        super(MyLSTMModel,self).__init__()
        self.rnn = paddle.nn.LSTM(input_size=4, hidden_size=10)
        self.flatten = paddle.nn.Flatten()
        self.fc=nn.Linear(10,2)

        
    def forward(self,input):
        out, (h, c)=self.rnn(input)
        out =self.flatten(out)
        out=self.fc(out)
        return out


class MyDataset(paddle.io.Dataset):
    def __init__(self,data,n_in=1,num_features=6,num_labels=1):
        super(MyDataset,self).__init__()
        self.data=data
        self.num_features=num_features
        self.num_labels=num_labels
        x=data[:,:n_in*num_features]
        self.y=data[:,n_in*num_features:]
        self.x=x.reshape((data.shape[0],n_in,num_features))
        self.y=self.y.reshape((data.shape[0],2))
        self.x=np.array(self.x,dtype='float32')
        self.y=np.array(self.y,dtype='float32')
        print(self.y[0])
        self.num_sample=len(x)

    def __getitem__(self,index):
        data=self.x[index]
        label=self.y[index]
        return data,label
    
    def __len__(self):
        return self.num_sample