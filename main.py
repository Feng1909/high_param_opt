from tkinter import YES
import yaml
from easydict import EasyDict as edict
import matplotlib.pyplot as plt

from simulator.simulate import Simulator
from utils.type import State, ControlCommand

if __name__ == "__main__":
    with open('config/bot.yaml') as yamlfile:
        cfgs = yaml.load(yamlfile, Loader=yaml.FullLoader)
        cfgs = edict(cfgs)
    simulator = Simulator(cfgs)
    state = simulator.get_state()
    print(state.state())
    cmd = ControlCommand(1, 0)
    time = 0
    x = []
    y = []
    theta = []
    time_ = []
    plt.figure()
    while True:
        time_.append(time)
        x.append(state.x)
        y.append(state.y)
        theta.append(state.theta)
        # plt.ion()
        # plt.plot(x,y)
        # plt.show()
        print(time)
        time += cfgs.step_time
        simulator.next_step(state, cmd)
        state = simulator.get_state()
        print(state.state())
        cmd = ControlCommand(0, 0)
        if time >= 500:
            break
    
    plt.plot(x,y)
    plt.show()

        # break