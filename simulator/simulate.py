from distutils.cmd import Command
from math import fabs, cos, sin, hypot, pi, atan2
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import interpolate

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
        self.is_running_flag = False
        self.sim_time = 0
        self.path = []
        self.finished = False

        self.load_map()

    def get_state(self):
        return self.state
    
    def get_sim_time(self):
        return self.sim_time

    def next_step(self, state, cmd):
        if not self.is_running_flag:
            self.state = state
            return
        if state == None or not self.isvalid(state):
            raise Exception("please input valid state")
        
        state_next = self.RK4(state, cmd, self.ts)
        while state_next.theta > 2*pi:
            state_next.theta -= 2*pi
        while state_next.theta < - 2*pi:
            state_next.theta += 2*pi
        self.state = state_next
        self.sim_time += self.cfg.step_time

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
        self.is_running_flag = True
        print("begin simulation")
    
    def stop(self):
        self.is_running_flag = False
        print("stop simulation")

    def is_running(self):
        return self.is_running_flag
    
    def load_map(self):
        if not os.path.exists(self.cfg.map_name):
            raise Exception("map do not exist")
        else:
            with open(self.cfg.map_name, 'r') as f:
                pathes = f.readlines()
            if len(pathes) == 0:
                raise Exception("path empty!")
            x = []
            y = []
            for i in pathes:
                i = i.replace('\n', '')
                i = i.replace(' ', '')
                coordinates = i.split(',')
                x.append(float(coordinates[0])+self.cfg.initial_position.x)
                y.append(float(coordinates[1])+self.cfg.initial_position.y)
            x = np.array(x)
            y = np.array(y)
            # get approximate length of track
            stot = 0
            for i in range(x.size-1):
                stot += hypot(x[i+1]-x[i], y[i+1]-y[i])
            stot = (stot//self.cfg.ds)*self.cfg.ds
            print("length of track: stot = ", str(round(stot, 2)))
            N = int(stot/self.cfg.ds)
            unew = np.arange(0, 1.0, 1.0/N)
            # center
            tck, u = interpolate.splprep([x,y], s=0)
            out = interpolate.splev(unew, tck)
            f_x = out[0]
            f_y = out[1]
            
            # set psic
            dx = np.diff(f_x)
            dy = np.diff(f_y)
            psic = np.arctan2(dy, dx)
            psic_final = np.arctan2(f_y[0]-f_y[-1], f_x[0]-f_x[-1])
            psic = np.append(psic, psic_final)
            for i in range(len(f_x)):
                self.path.append([f_x[i], f_y[i], psic[i]])
        print(f"Load map: {self.cfg.map_name} finished")

    def get_path(self):
        x = self.state.x
        y = self.state.y
        min_now = 9999
        index = -1
        num = 0
        for i in self.path:
            if hypot(x - i[0], y - i[1]) < min_now:
                min_now = hypot(x - i[0], y - i[1])
                index = num
            num += 1
        if index == -1:
            raise Exception("find location error")
        path_next = self.path[index+1: index+1+self.cfg.ref_ahead]
        if index+1+self.cfg.ref_ahead > len(self.path):
            self.stop()
            self.is_running_flag = False
            self.finished = True
            print("mission finished")
        path_return = []
        for i in path_next:
            x1 = i[0]-self.state.x
            y1 = i[1]-self.state.y
            D = hypot(x1, y1)
            Phi = atan2(y1, x1)-self.state.theta
            theta = i[2] - self.state.theta
            while theta < -pi:
                theta += 2*pi
            while theta > pi:
                theta -= 2*pi
            path_return.append([D*cos(Phi),
                                D*sin(Phi),
                                theta])
        return path_return
        
    def get_full_path(self):
        x = []
        y = []
        for i in self.path:
            x.append(i[0])
            y.append(i[1])
        return x, y

    def is_finished(self):
        return self.finished
