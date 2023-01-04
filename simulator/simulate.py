from distutils.cmd import Command
from math import fabs, cos, sin
import numpy as np

from utils.type import State, ControlCommand

class Simulator:
    ''' 
    cfg: yaml document
    '''
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self.lap_time = 0
        init_state = cfg.initial_position
        state = State(  init_state.x, 
                        init_state.y, 
                        init_state.theta, 
                        init_state.v, 
                        init_state.omega)
        self.state = state
        self.ts = cfg.step_time
        self.is_running = False
        self.sim_time = 0

    def get_state(self):
        return self.state
    
    def get_sim_time(self):
        return self.sim_time

    def next_step(self, state, cmd):
        if not self.is_running:
            self.state = state
            return
        if state == None or not self.isvalid(state):
            raise Exception("please input valid state")
        
        state_next = self.RK4(state, cmd, self.ts)
        self.state = state_next
        self.sim_time += self.cfg.step_time
        # print("haha")

    def isvalid(self, state):
        x = state.x
        y = state.y
        theta = state.theta
        v = state.v
        omega = state.omega
        if x > self.cfg.map.x or x < 0 or y > self.cfg.map.y or y < 0:
            return False
        return True

    def RK4(self, state, control, ts):
        state = self.stateToVector(state=state)
        cmd = self.inputToVector(cmd=control)
        k1 = np.array(self.model(state, cmd))
        k2 = np.array(self.model(state + ts / 2 * k1, cmd))
        k3 = np.array(self.model(state + ts / 2. * k2, cmd))
        k4 = np.array(self.model(state + ts * k3, cmd))
        state_next = np.array(state + ts * (k1/6. + k2/3. + k3/3. + k4/6.))
        return self.vectorToState(state_next)

    def stateToVector(self, state):
        vector = []
        vector.append(state.x)
        vector.append(state.y)
        vector.append(state.theta)
        vector.append(state.v)
        vector.append(state.omega)
        return vector
    
    def inputToVector(self, cmd):
        vector = []
        vector.append(cmd.u_l)
        vector.append(cmd.u_r)
        return vector
    
    def vectorToState(self, state):
        state = State(state[0], state[1], state[2], state[3], state[4])
        return state
    
    def model(self, state, cmd):
        L = self.cfg.model.L
        x, y, theta, v, omega = state
        u_l, u_r = cmd
        f = []

        f.append(v * cos(theta))
        f.append(v * sin(theta))
        f.append(omega)
        f.append((u_l + u_r)/2)
        f.append((u_r - u_l)/L)
        return f

    def begin(self):
        self.is_running = True
        print("begin simulation")
    
    def stop(self):
        self.is_running = False
        print("stop simulation")

    def is_running(self):
        return self.is_running
    
