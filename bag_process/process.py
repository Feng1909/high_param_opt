import rosbag
from rospy.rostime import Time
from math import hypot

bag = rosbag.Bag('2023-03-10-16-01-03.bag')

print(type(bag))

cmd_data = bag.read_messages('/cmd_vel')
state_data = bag.read_messages('/state')
datas = []

for topic, msg, time in cmd_data:
    cmd_v = msg.linear.x
    cmd_r = msg.angular.z
    v_l = cmd_v - 0.308*cmd_r/20
    v_r = cmd_v + 0.308*cmd_r/20
    datas.append(['cmd', Time.to_sec(time), [v_l, v_r]])

for topic, msg, time in state_data:
    x = msg.pose.position.x
    y = msg.pose.position.y
    theta = msg.pose.orientation.y
    datas.append(['state', Time.to_sec(time), [x, y, theta]])

print(len(datas))

x_old = 0
y_old = 0
theta_old = 0
time_old = 0

for state in datas:
    if state[0] != 'state':
        continue
    if x_old == 0 and y_old == 0 and time_old == 0:
        x_old = state[2][0]
        y_old = state[2][1]
        theta_old = state[2][2]
        time_old = state[1]
        continue
    if state[1] - time_old < 0.01:
        continue
    delta_time = state[1] - time_old
    delta_s = hypot(x_old - state[2][0], y_old - state[2][1])
    delta_theta = state[2][2] - theta_old

    v = delta_s / delta_time
    omega = delta_theta / delta_time
    
    datas.append(['delta_state', (time_old + state[1])/2, [v, omega]])
    x_old = state[2][0]
    y_old = state[2][1]
    theta_old = state[2][2]
    time_old = state[1]

# print(len(datas))
datas.sort(key=lambda e:e[1])
# print(datas)
with open('finetune.csv', 'w') as f:
    # s = 'v,omega,ul,ur,v_next,omega_next\n'
    s = ''
    for data in datas:
        if data[0] == 'delta_state':
            s += str(data[2][0])+','+str(data[2][1])+'\n'
            f.writelines(s)
            s = str(data[2][0])+','+str(data[2][1])+','
        if data[0] == 'cmd':
            s += str(data[2][0])+','+str(data[2][1])+','