class State:
    '''
    x, y, theta in global and v, omega
    '''
    def __init__(self, x, y, theta, v, omega):
        self.x = x
        self.y = y
        self.theta = theta
        self.v = v
        self.omega = omega
    
    def x(self):
        return self.x
    
    def y(self):
        return self.y
    
    def theta(self):
        return self.theta
    
    def v(self):
        return self.v
    
    def omega(self):
        return self.omega
    
    def state(self):
        return self.x, self.y, self.theta, self.v, self.omega


class ControlCommand:
    def __init__(self, cmd_l, cmd_r) -> None:
        self.u_r = cmd_r
        self.u_l = cmd_l
    
    def u_l(self):
        return self.u_l
    
    def u_r(self):
        return self.u_r

    def cmd(self):
        return self.u_l, self.u_r