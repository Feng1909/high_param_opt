import rosbag

bag = rosbag.Bag('2023-03-10-16-01-03.bag')

print(type(bag))

cmd_data = bag.read_messages('/cmd_vel')
# print(cmd_data)
for topic, msg, t in cmd_data:
    print(t)