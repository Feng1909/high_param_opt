import yaml
from easydict import EasyDict as edict
from bayes_opt import BayesianOptimization
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events

import sys,os
sys.path.append(os.getcwd())
from simulator.simulate import Simulator
from controller.control import MPC, PurePursuit
from utils.type import ControlCommand

def run(u, x, y, theta, v, omega):
    with open('config/bot.yaml') as yamlfile:
        cfgs = yaml.load(yamlfile, Loader=yaml.FullLoader)
        cfgs = edict(cfgs)
    cfgs.visual = False
    cfgs.MPC.input.ul = u
    cfgs.MPC.input.ur = u
    cfgs.MPC.state.x = x
    cfgs.MPC.state.y = y
    cfgs.MPC.state.theta = theta
    cfgs.MPC.state.v = v
    cfgs.MPC.state.omega = omega
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
    time_ = [0]
    try:
        diff = 0
        while True and not simulator.is_finished():
            time += cfgs.ts
            simulator.next_step(state, cmd)
            state = simulator.get_state()
            path = simulator.get_path()
            diff += simulator.get_diff()
            controller.set_path(path)
            controller.set_state(state)
            cmd = controller.get_cmd()
            
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
            if time >= 20:
                return -10000
        return -diff
    except:
        return -10000

if __name__ == "__main__":
    pbounds = {'u': (0, 10), 'x': (0, 100), 'y': (0, 100),
               'theta': (0, 10), 'v': (0, 10), 'omega': (0, 1)}
    optimizer = BayesianOptimization(
        f=run,
        pbounds=pbounds,
        random_state=1,
    )

    optimizer.probe(
        params={'u': 0.001, 'x': 99, 'y': 99,
               'theta': 0.2, 'v': 1, 'omega': 0.01},
        lazy=True,
    )
    logger = JSONLogger(path="./logs.json")
    optimizer.subscribe(Events.OPTIMIZATION_STEP, logger)

    optimizer.maximize(
        init_points=100,
        n_iter=500,
    )

    print(optimizer.max)