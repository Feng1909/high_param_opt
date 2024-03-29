from math import hypot, cos, sin, atan2, pi, sqrt
import numpy as np
import casadi as ca
import time
from scipy import interpolate

from utils.type import ControlCommand, State

class PurePursuit:
    def __init__(self, cfgs) -> None:
        self.path = []
        self.cfgs = cfgs
        self.cmd = ControlCommand(0.1, 0)
        self.state = State()

    def set_path(self, path):
        if len(path) == 0:
            raise Exception("path empty!")
        self.path = path

    def set_state(self, state):
        self.state = state
    
    def calculate_cmd(self):
        destination = self.path[self.cfgs.look_ahead]
        D = hypot(destination[0], destination[1])
        theta = destination[2]
        R = D/(2*sin(theta)) * 0.4
        L = self.cfgs.model.L
        v_l = 2*R/(L+2*R) * self.cfgs.model.max_v
        v_r = 2*(L+R)/(L+2*R) * self.cfgs.model.max_v
        self.cmd.u_l = (v_l-(self.state.v - self.cfgs.model.L * self.state.omega / 2))
        self.cmd.u_r = (v_r-(self.state.v + self.cfgs.model.L * self.state.omega / 2))
    
    def get_cmd(self):
        self.calculate_cmd()
        return self.cmd

class MPC:
    def __init__(self, cfgs) -> None:
        self.cfg = cfgs
        self.N = self.cfg.MPC.N
        self.dt = self.cfg.MPC.dt
        self.L = self.cfg.model.L
        self.max_a = self.cfg.model.max_a
        self.max_v = self.cfg.model.max_v
        self.ref_path = []
        self.pre_path = []
        self.cmd = ControlCommand(0, 0)
        self.state = State()

        self.opti = ca.Opti()
        # ul, ur
        self.opt_controls = self.opti.variable(self.N, 2)
        self.ul = self.opt_controls[:, 0]
        self.ur = self.opt_controls[:, 1]
        self.cmd_all = np.zeros((self.N, 2))
        # x, y, theta, v, omega
        self.opt_states = self.opti.variable(self.N+1, 5)
        self.pos_x = self.opt_states[:, 0]
        self.pos_y = self.opt_states[:, 1]
        self.pos_theta = self.opt_states[:, 2]
        self.pos_v = self.opt_states[:, 3]
        self.pos_omega = self.opt_states[:, 4]
        # ref_path
        self.ref_path = self.opti.parameter(self.N, 5)
        # kinetic model
        self.f = lambda x, u: ca.vertcat(*[x[3]*np.cos(x[2]),
                                           x[3]*np.sin(x[2]),
                                           x[4],
                                           (u[0]+u[1])/2,
                                           (u[1]-u[0])/self.L])

        # init condition
        self.opti.subject_to(self.opt_states[0, :] == self.ref_path[0, :])
        for k in range(self.N): # loop over control intervals
            # Runge-Kutta 4 integration
            k1 = self.f(self.opt_states[k, :],              self.opt_controls[k, :])
            k2 = self.f(self.opt_states[k, :]+self.dt/2*k1.T, self.opt_controls[k, :])
            k3 = self.f(self.opt_states[k, :]+self.dt/2*k2.T, self.opt_controls[k, :])
            k4 = self.f(self.opt_states[k, :]+self.dt*k3.T,   self.opt_controls[k, :])
            x_next = self.opt_states[k, :] + self.dt*(k1/6.+k2/3.+k3/3.+k4/6.).T
            self.opti.subject_to(self.opt_states[k+1, :] == x_next)
        
        # cost function
        # some addition parameters
        self.Q = np.diag([self.cfg.MPC.state.x,
                          self.cfg.MPC.state.y,
                          self.cfg.MPC.state.theta,
                          self.cfg.MPC.state.v,
                          self.cfg.MPC.state.omega])
        self.R = np.diag([self.cfg.MPC.input.ul,
                          self.cfg.MPC.input.ur])
        self.obj = 0 # cost
        for i in range(self.N):
            self.obj = self.obj + ca.mtimes([(self.opt_states[i, :]-self.ref_path[i, :]),
                                              self.Q,
                                              (self.opt_states[i, :]-self.ref_path[i, :]).T]) + \
                                  ca.mtimes([(self.opt_controls[i, :]), self.R, (self.opt_controls[i, :]).T])
        
        self.opti.minimize(self.obj)
        self.opti.subject_to(self.opti.bounded(0, self.pos_v, self.max_v))
        self.opti.subject_to(self.opti.bounded(-self.max_a, self.ul, self.max_a))
        self.opti.subject_to(self.opti.bounded(-self.max_a, self.ur, self.max_a))

        opts_setting = {'ipopt.max_iter':100, 'ipopt.print_level':0, 'print_time':0, 'ipopt.acceptable_tol':1e-8, 'ipopt.acceptable_obj_change_tol':1e-6}

        self.opti.solver('ipopt', opts_setting)


        ## test mpc once
        ref_v = 0.5
        next_states = np.zeros((self.N+1, 5))
        for i in range(self.N):
            x = i
            state = [x,x,0,ref_v,0]
            self.opti.set_value(self.ref_path[i, :], state)
        self.opti.set_initial(self.opt_controls, np.zeros((self.N, 2)))
        self.opti.set_initial(self.opt_states, next_states)
        sol = self.opti.solve()
        
        if self.cfg.MPC.N > self.cfg.ref_ahead:
            raise Exception("ref_ahead should upper than MPC.N")
        if self.cfg.is_print:
            print("successfully initialize mpc")

    def set_path(self, path):
        if len(path) == 0:
            raise Exception("path empty!")
        self.path = path

    def set_state(self, state):
        self.state = state
    
    def calculate_cmd(self):
        desire_v = self.cfg.MPC.desire_v
        init_state = []
        init_state.append([0,0,0,self.state.v,self.state.omega])
        stot = 0
        v_old = self.state.v
        for i in range(self.N):
            path_ref = self.path[stot]

            k = abs(path_ref[4])/pow(sqrt(1+pow(path_ref[3], 2)), 3)
            r = 1/k
            v = max(min(min(desire_v, v_old+self.cfg.model.max_a*self.dt), sqrt(self.cfg.model.max_a*r)), 0.1)

            state = []
            for j in path_ref[:3]:
                state.append(j)
            state.append(v)
            state.append(path_ref[3])
            if i == 0:
                state = [0,0,0,self.state.v, self.state.omega]
            init_state.append([state[0],
                               state[1],
                               state[2],
                               state[3],
                               state[4]])
            self.opti.set_value(self.ref_path[i, :], state)
            stot += int(self.dt*v*100)
            v_old = v

        self.opti.set_initial(self.opt_controls, self.cmd_all)
        init_state = np.array(init_state)
        self.opti.set_initial(self.opt_states, init_state)
        sol = self.opti.solve()
        self.cmd_all = sol.value(self.opt_controls)
        [self.cmd.u_l, self.cmd.u_r] = self.cmd_all[0]
        pre = sol.value(self.opt_states)
        self.pre_path = []
        for i in pre:
            self.pre_path.append([round(i[0],3), round(i[1],3), round(i[2],3), round(i[3],3), round(i[4],3)])
        
    def get_cmd(self):
        t1 = time.time()
        self.calculate_cmd()
        t2 = time.time()
        if self.cfg.is_print:
            print('solve time: ', t2-t1)
        return self.cmd
    
    def get_pre_path(self):
        return self.pre_path