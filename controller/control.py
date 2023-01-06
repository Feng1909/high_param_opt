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