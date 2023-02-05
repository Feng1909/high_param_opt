import paddle
import paddle.fluid as fluid
import paddle.fluid.layers as layers
import pandas as pd
import numpy as np
import random

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

#数据生成器
def switch_reader(is_val: bool = False):
    def reader():
        # 判断是否是验证集
        if is_val:
            # 抽取数据使用迭代器返回
            for te in test:
                yield [te[:4]],[te[-2:]]
        else:
            # 抽取数据使用迭代器返回
            for tr in train:
                yield [tr[:4]],[tr[-2:]]
        
    return reader   # 注意！此处不需要带括号
# 划分batch
batch_size = 8
train_reader = fluid.io.batch(reader=switch_reader(), batch_size=batch_size)
val_reader = fluid.io.batch(reader=switch_reader(is_val=True), batch_size=batch_size)
# for data in train_reader():
#     # print(data[0].shape,data[1].shape)
#     train_x=np.array([x[0] for x in data],np.float32)
#     train_y = np.array([x[1] for x in data]).astype('int64')
#     print(train_x.shape,train_y.shape)
#定义LSTM网络
class MyLSTMModel(fluid.dygraph.Layer):
    '''
    DNN网络
    '''
    def __init__(self):
        super(MyLSTMModel,self).__init__()
        self.rnn = paddle.nn.LSTM(input_size=4, hidden_size=10, num_layers=8)
        self.flatten = paddle.nn.Flatten()
        self.fc=fluid.dygraph.Linear(10,2)

        
    def forward(self,input):
        # print('input',input.shape)
        out, (h, c)=self.rnn(input)
        out =self.flatten(out)
        # print('flatten: ',out.shape)
        out=self.fc(out)
        return out

Batch=0
Batchs=[]
all_train_loss=[]

place = fluid.CPUPlace()

with fluid.dygraph.guard(place):
    model=MyLSTMModel() #模型实例化
    # model=MyModel()
    model.train() #训练模式
    # opt=fluid.optimizer.SGDOptimizer(learning_rate=0.001, parameter_list=model.parameters())#优化器选用SGD随机梯度下降，学习率为0.001.
    opt=fluid.optimizer.AdamOptimizer(learning_rate=0.01, parameter_list=model.parameters()) 
    epochs_num=100#迭代次数
    batch_size = 1000
    train_reader = fluid.io.batch(reader=switch_reader(), batch_size=batch_size)
    val_reader = fluid.io.batch(reader=switch_reader(is_val=True), batch_size=batch_size)
    Batch=0
    Batchs=[]
    all_train_loss=[]
    all_eval_loss=[]
    for pass_num in range(epochs_num):
        for batch_id, data in enumerate(train_reader()): 
            data_x=np.array([x[0] for x in data],np.float32)
            data_y = np.array([x[1] for x in data]).astype('float32')
            data_x = fluid.dygraph.to_variable(data_x)
            data_y = fluid.dygraph.to_variable(data_y)

            predict=model(data_x)
            
            loss=fluid.layers.mse_loss(predict,data_y)
            avg_loss=fluid.layers.mean(loss)#获取loss值
            avg_loss.backward()       
            opt.minimize(avg_loss)    #优化器对象的minimize方法对参数进行更新 
            model.clear_gradients()   #model.clear_gradients()来重置梯度
            if batch_id!=0 and batch_id%1==0:
                Batch = Batch+1 
                Batchs.append(Batch)
                all_train_loss.append(avg_loss.numpy()[0])
                evalavg_loss=[]
                for eval_data in val_reader():
                    eval_data_x = np.array([x[0] for x in eval_data],np.float32)
                    eval_data_y = np.array([x[1] for x in eval_data]).astype('float32')

                    eval_data_x = fluid.dygraph.to_variable(eval_data_x)
                    eval_data_y = fluid.dygraph.to_variable(eval_data_y)

                    eval_predict=model(eval_data_x)
                    eval_loss=fluid.layers.mse_loss(eval_predict,eval_data_y)
                    eval_loss=fluid.layers.mean(eval_loss)
                    evalavg_loss.append(eval_loss.numpy()[0])#获取loss值
                all_eval_loss.append(sum(evalavg_loss)/len(evalavg_loss))
        print("epoch:{},batch_id:{},train_loss:{},eval_loss:{}".format(pass_num,batch_id,avg_loss.numpy(),sum(evalavg_loss)/len(evalavg_loss)))     

    fluid.save_dygraph(model.state_dict(),'model/LSTMModel')#保存模型
    fluid.save_dygraph(opt.state_dict(),'model/LSTMModel')#保存模型
    print("Final loss: {}".format(avg_loss.numpy()))    