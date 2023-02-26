import yaml
from easydict import EasyDict as edict
import random

import sys,os
sys.path.append(os.getcwd())
from simulator.simulate import Simulator
from controller.control import MPC, PurePursuit
from utils.type import ControlCommand

def run(cfgs=None):
    with open('ML/data.csv', 'a') as f:
        # s = 'v,omega,ul,ur,v_next,omega_next\n'
        # f.writelines(s)
        s = '0,0,0,0,'
        simulator = Simulator(cfgs)
        if cfgs.controller == 'purepursuit':
            controller = PurePursuit(cfgs)
        elif cfgs.controller == 'mpc':
            controller = MPC(cfgs)
        else:
            raise Exception("controller empty!")
        state = simulator.get_state()
        simulator.begin()
        cmd = ControlCommand(0, 0)
        time = 0
        while True and not simulator.is_finished():
            time += cfgs.ts
            simulator.next_step(state, cmd)
            state = simulator.get_state()
            path = simulator.get_path()
            controller.set_path(path)
            controller.set_state(state)
            cmd = controller.get_cmd()

            s += str(state.v)+','+str(state.omega)+'\n'
            f.writelines(s)
            s = str(state.v)+','+str(state.omega)+','+str(cmd.u_l)+','+str(cmd.u_r)+','
            
            ref_x = []
            ref_y = []
            ref_theta = []
            for i in path:
                ref_y.append(i[0])
                ref_x.append(-i[1])
                ref_theta.append(i[2])
            if cfgs.controller == 'mpc':
                pre_path = controller.get_pre_path()
                pre_x = []
                pre_y = []
                for i in pre_path:
                    pre_y.append(i[0])
                    pre_x.append(-i[1])
            v_l = state.v - cfgs.model.L * state.omega / 2
            v_r = state.v + cfgs.model.L * state.omega / 2
            # break
            if time >= 700:
                break
        with open('ML/time.txt', 'a') as f:
            f.writelines(str(round(time, 2))+'\n')

if __name__ == "__main__":
    with open('config/bot.yaml') as yamlfile:
        cfgs = yaml.load(yamlfile, Loader=yaml.FullLoader)
        cfgs = edict(cfgs)
    cfgs.visual = False
    # run(cfgs)
    map_num = 10000
    num = 0
    while(num < map_num):
        # print(num)
        try:
            with open('map/auto_'+str(num)+'.csv', 'w') as f:
                f.writelines('0,0\n')
                for i in range(4):
                    n1 = random.randint(0,100)
                    n2 = random.randint(0,100)
                    f.writelines(str(n1/10)+','+str(n2/10)+'\n')
                f.writelines('0,0')
            cfgs.map_name = 'map/auto_'+str(num)+'.csv'
            run(cfgs)
            num += 1
        except:
            pass
