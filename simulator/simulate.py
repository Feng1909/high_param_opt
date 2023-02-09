from distutils.cmd import Command
from math import fabs, cos, sin, hypot, pi, atan2, acos
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import interpolate
from paddle.inference import Config
from paddle.inference import create_predictor

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
        self.ts = cfg.ts
        self.is_running_flag = False
        self.sim_time = 0
        self.path = []
        self.finished = False

        self.load_map()

        if self.cfg.is_ai:
            self.config = Config("inference_model/LSTMModel.pdmodel", "inference_model/LSTMModel.pdiparams")
            self.config.disable_gpu()

            # 创建 PaddlePredictor
            self.predictor = create_predictor(self.config)

            # 获取输入的名称
            self.input_names = self.predictor.get_input_names()
            self.input_handle = self.predictor.get_input_handle(self.input_names[0])

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
        if self.cfg.is_ai == True:
            self.state = self.ai_infer(self.state, cmd, self.ts)
        else:
            for i in range(int(self.cfg.ts / self.cfg.step_time)):
                self.state = self.RK4(self.state, cmd, self.ts)
        self.sim_time += self.cfg.ts
        # self.state = state_next
        # self.sim_time += self.cfg.step_time

    def isvalid(self, state):
        x = state.x
        y = state.y
        theta = state.theta
        v = state.v
        omega = state.omega
        if x > self.cfg.map.x or x < 0 or y > self.cfg.map.y or y < 0:
            return False
        return True
    
    def ai_infer(self, state, control, ts):
        # fake_input = np.array([[[0.6526019700600132,-0.9479607045698846,9.9999998760563,6.092632976836683]]]).astype('float32')
        input_date = np.array([[[state.v, state.omega, control.u_l, control.u_r]]]).astype('float32')
        self.input_handle.copy_from_cpu(input_date)

        # 运行 predictor
        self.predictor.run()

        # 获取输出
        output_names = self.predictor.get_output_names()
        output_handle = self.predictor.get_output_handle(output_names[0])
        output_data = output_handle.copy_to_cpu() # numpy.ndarray 类型

        v_next, omega_next = output_data[0]
        omega_tmp = (omega_next + state.omega)/2
        v_tmp = (v_next + state.v)/2
        theta_next = omega_tmp*ts + state.theta
        theta_tmp = (theta_next + state.theta)/2
        x_next = v_tmp*cos(theta_tmp)*ts + state.x
        y_next = v_tmp*sin(theta_tmp)*ts + state.y

        state = State(x_next,
                      y_next,
                      theta_next,
                      max(v_next, 0),
                      omega_next)
        return state
        

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
        if self.cfg.is_print:
            print("begin simulation")
    
    def stop(self):
        self.is_running_flag = False
        if self.cfg.is_print:
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
            N = int(stot/self.cfg.ds)
            unew = np.arange(0, 1.0, 1.0/N)
            # center
            # Find the B-spline representation of an N-D curve
            tck, u = interpolate.splprep([x,y], s=0)
            # Evaluate a B-spline or its derivatives.
            out = interpolate.splev(unew, tck)
            f_x = out[0]
            f_y = out[1]
            # get approximate length of track
            stot = 0
            for i in range(len(out[0])-1):
                stot += hypot(out[0][i+1]-out[0][i], out[1][i+1]-out[1][i])
            if self.cfg.is_print:
                print("length of track: stot = ", str(round(stot, 2)))
            with open('ML/length.txt', 'a') as f:
                f.writelines(str(round(stot, 2))+'\n')
            N = int(stot/self.cfg.ds)
            unew = np.arange(0, 1.0, 1.0/N)
            # center
            # Find the B-spline representation of an N-D curve
            tck, u = interpolate.splprep([x,y], s=0)
            # Evaluate a B-spline or its derivatives.
            out = interpolate.splev(unew, tck)
            f_x = out[0]
            f_y = out[1]
            
            # set psic
            dx = np.diff(f_x)
            dy = np.diff(f_y)
            theta = np.arctan2(dy, dx)
            psic_final = np.arctan2(f_y[0]-f_y[-1], f_x[0]-f_x[-1])
            theta = np.append(theta, psic_final)

            for j in range(len(theta)-1):
                while(theta[j] - theta[j+1] > np.pi):
                    theta[j+1] = theta[j+1] + 2*np.pi
                    
                while(theta[j] - theta[j+1] <= -np.pi):
                    theta[j+1] = theta[j+1] - 2*np.pi

            s = np.arange(0, stot-0.01, self.cfg.ds)
            psic = theta[:len(s)]
            t, c, k = interpolate.splrep(s, psic, s=0, k=4)
            psic_spl = interpolate.BSpline(t, c, k, extrapolate=False)
            kappac_spl_one = psic_spl.derivative(nu=1)
            kappac_spl_one = kappac_spl_one(s)
            kappac_spl_two = psic_spl.derivative(nu=2)
            kappac_spl_two = kappac_spl_two(s)

            for i in range(len(f_x)):
                self.path.append([f_x[i], f_y[i], theta[i], kappac_spl_one[i], kappac_spl_two[i]])
        if self.cfg.is_print:
            print(f"Load map: {self.cfg.map_name} finished")
    
    def get_diff(self):
        return self.l

    def get_path(self):
        x = self.state.x
        y = self.state.y
        min_now = 9999
        index = -1
        num = 0
        a_1 = []
        a_2 = []
        b = [x,y]
        for i in self.path:
            if hypot(x - i[0], y - i[1]) < min_now:
                min_now = hypot(x - i[0], y - i[1])
                index = num
                a_2 = a_1
                a_1 = [i[0], i[1]]
            num += 1
        
        # cal l #
        if a_2 != []:
            a1_b = [b[0]-a_1[0], b[1]-a_1[1]]
            a1_a2 = [a_2[0]-a_1[0], a_2[1]-a_1[1]]
            self.l = abs(hypot(a1_b[0], a1_b[1])) * sin(acos(abs(
                (a1_a2[0]*a1_b[0]+a1_a2[1]*a1_b[1]) /
                (hypot(a1_a2[0], a1_a2[1])*hypot(a1_b[0], a1_b[1]))
            )))
        else:
            self.l = hypot(a_1[0]-b[0], a_1[1]-b[1])
        # print(self.l)

        if index == -1:
            raise Exception("find location error")
        path_next = self.path[index+1: index+1+self.cfg.ref_ahead]
        if index+1+self.cfg.ref_ahead > len(self.path):
            self.stop()
            self.is_running_flag = False
            self.finished = True
            if self.cfg.is_print:
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
                                theta,
                                i[3],
                                i[4]])
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
