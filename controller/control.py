from math import hypot, sin, atan2

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
        D = hypot(self.state.x - destination[0], self.state.y - destination[1])
        theta = destination[2] - self.state.theta
        R = D/(2*sin(theta))
        L = self.cfgs.model.L
        v_l = 2*R/(L+2*R) * self.cfgs.model.max_v
        v_r = 2*(L+R)/(L+2*R) * self.cfgs.model.max_v
        print()
        self.cmd.u_l = min(self.cfgs.model.max_a, v_l-self.state.omega*(1-L/2))
        self.cmd.u_l = max(self.cmd.u_l, - self.cfgs.model.max_a)
        self.cmd.u_r = min(self.cfgs.model.max_a, v_r-self.state.omega*(1+L/2))
        self.cmd.u_r = max(self.cmd.u_r, - self.cfgs.model.max_a)

    
    def get_cmd(self):
        self.calculate_cmd()
        return self.cmd