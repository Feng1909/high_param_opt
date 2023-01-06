class State:
    '''
    x, y, theta in global and v, omega
    '''
    def __init__(self, x=0, y=0, theta=0, v=0, omega=0):
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
    def __init__(self, cmd_l=0, cmd_r=0) -> None:
        self.u_r = cmd_r
        self.u_l = cmd_l
    
    def u_l(self):
        return self.u_l
    
    def u_r(self):
        return self.u_r

    def cmd(self):
        return self.u_l, self.u_r