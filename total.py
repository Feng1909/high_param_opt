import pandas as pd
import numpy as np
import os

total_length = 0
total_map = 0
total_time = 0

path = 'server/1'
with open(path + '/ML/length.txt', 'r') as f:
    lengths = f.readlines()
length = []
for i in lengths:
    length.append(float(i))
total_length += np.sum(np.array(length))
with open(path + '/ML/time.txt', 'r') as f:
    times = f.readlines()
time = []
for i in times:
    time.append(float(i))
total_time += np.sum(np.array(time))
total_map += len(os.listdir(path+'/map'))

path = 'server/2'
with open(path + '/ML/length.txt', 'r') as f:
    lengths = f.readlines()
length = []
for i in lengths:
    length.append(float(i))
total_length += np.sum(np.array(length))
with open(path + '/ML/time.txt', 'r') as f:
    times = f.readlines()
time = []
for i in times:
    time.append(float(i))
total_time += np.sum(np.array(time))
total_map += len(os.listdir(path+'/map'))

path = 'server/11'
with open(path + '/ML/length.txt', 'r') as f:
    lengths = f.readlines()
length = []
for i in lengths:
    length.append(float(i))
total_length += np.sum(np.array(length))
with open(path + '/ML/time.txt', 'r') as f:
    times = f.readlines()
time = []
for i in times:
    time.append(float(i))
total_time += np.sum(np.array(time))
total_map += len(os.listdir(path+'/map'))

path = 'server/12'
with open(path + '/ML/length.txt', 'r') as f:
    lengths = f.readlines()
length = []
for i in lengths:
    length.append(float(i))
total_length += np.sum(np.array(length))
with open(path + '/ML/time.txt', 'r') as f:
    times = f.readlines()
time = []
for i in times:
    time.append(float(i))
total_time += np.sum(np.array(time))
total_map += len(os.listdir(path+'/map'))

path = 'server/21'
with open(path + '/ML/length.txt', 'r') as f:
    lengths = f.readlines()
length = []
for i in lengths:
    length.append(float(i))
total_length += np.sum(np.array(length))
with open(path + '/ML/time.txt', 'r') as f:
    times = f.readlines()
time = []
for i in times:
    time.append(float(i))
total_time += np.sum(np.array(time))
total_map += len(os.listdir(path+'/map'))

path = 'server/22'
with open(path + '/ML/length.txt', 'r') as f:
    lengths = f.readlines()
length = []
for i in lengths:
    length.append(float(i))
total_length += np.sum(np.array(length))
with open(path + '/ML/time.txt', 'r') as f:
    times = f.readlines()
time = []
for i in times:
    time.append(float(i))
total_time += np.sum(np.array(time))
total_map += len(os.listdir(path+'/map'))

print('total_length: ', total_length)
print('total_map_num: ', total_map)
print('total_run_time: %d hours %d minutes %f seconds'%(total_time/3600, total_time%3600/60, total_time%60))


data_path = 'ML/data_train.csv'
data = pd.read_csv(data_path)
print('train_data: ', len(data.values))

data_path = 'ML/data_eval.csv'
data = pd.read_csv(data_path)
print('test_data: ', len(data.values))