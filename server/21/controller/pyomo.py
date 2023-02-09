import numpy as np
from pyomo.environ import *
from pyomo.dae import *

N = 9 # forward predict steps
ns = 6  # state numbers / here: 1: x, 2: y, 3: psi, 4: v, 5: cte, 6: epsi
na = 2  # actuator numbers /here: 1: steering angle, 2: throttle


class MPC(object):
    def __init__(self):
        m = ConcreteModel()
        m.sk = RangeSet(0, N-1)
        m.uk = RangeSet(0, N-2)
        m.uk1 = RangeSet(0, N-3)
        # Parameters
        m.wg       = Param(RangeSet(0, 3), initialize={0:1., 1:10., 2:100., 3:130000}, mutable=True) 
        m.dt       = Param(initialize=0.1, mutable=True)
        m.Lf       = Param(initialize=2.67, mutable=True)
        m.ref_v    = Param(initialize=75., mutable=True)
        m.ref_cte  = Param(initialize=0.0, mutable=True)
        m.ref_epsi = Param(initialize=0.0, mutable=True)
        m.s0       = Param(RangeSet(0, ns-1), initialize={0:0., 1:0., 2:0., 3:0., 4:0., 5:0.}, mutable=True)
        m.coeffs   = Param(RangeSet(0, 3), 
                          initialize={0:-0.000458316, 1:0.00734257, 2:0.0538795, 3:0.080728}, mutable=True)
        
        # Variables 
        m.s      = Var(RangeSet(0, ns-1), m.sk)
        m.f      = Var(m.sk)
        m.psides = Var(m.sk)
        m.ua     = Var(m.uk, bounds=(-1.0, 1.0))
        m.ud     = Var(m.uk, bounds=(-0.436332, 0.436332))
        
        # 0: x, 1: y, 2: psi, 3: v, 4: cte, 5: epsi
        # Constrainsts
        m.s0_update      = Constraint(RangeSet(0, ns-1), rule = lambda m, i: m.s[i,0] == m.s0[i])
        m.x_update       = Constraint(m.sk, rule=lambda m, k: 
                                      m.s[0,k+1]==m.s[0,k]+m.s[3,k]*cos(m.s[2,k])*m.dt 
                                      if k<N-1 else Constraint.Skip)
        m.y_update       = Constraint(m.sk, rule=lambda m, k: 
                                      m.s[1,k+1]==m.s[1,k]+m.s[3,k]*sin(m.s[2,k])*m.dt 
                                      if k<N-1 else Constraint.Skip)
        m.psi_update     = Constraint(m.sk, rule=lambda m, k: 
                                       m.s[2,k+1]==m.s[2,k]-m.s[3,k]*m.ud[k]/m.Lf*m.dt 
                                       if k<N-1 else Constraint.Skip)
        m.v_update       = Constraint(m.sk, rule=lambda m, k: 
                                       m.s[3,k+1]==m.s[3,k]+m.ua[k]*m.dt 
                                       if k<N-1 else Constraint.Skip)
        m.f_update      = Constraint(m.sk, rule=lambda m, k: 
                                       m.f[k]==m.coeffs[0]*m.s[0,k]**3+m.coeffs[1]*m.s[0,k]**2+
                                       m.coeffs[2]*m.s[0,k]+m.coeffs[3])
        m.psides_update = Constraint(m.sk, rule=lambda m, k: 
                                           m.psides[k]==atan(3*m.coeffs[0]*m.s[0,k]**2
                                                              +2*m.coeffs[1]*m.s[0,k]+m.coeffs[2]))
        m.cte_update     = Constraint(m.sk, rule=lambda m, k: 
                                        m.s[4,k+1]==(m.f[k]-m.s[1,k]+m.s[3,k]*sin(m.s[5,k])*m.dt) 
                                       if k<N-1 else Constraint.Skip)
		# 下面这行代码与上面的公式多了个负号，这是因为udapcity的无人车仿真环境的方向盘（注意不是航向角）往左打为负，往右打为正，正好与坐标系的航向角相反（右手定则，左正右负）
        m.epsi_update    = Constraint(m.sk, rule=lambda m, k: 
                                   m.s[5, k+1]==m.s[2,k]-m.psides[k]-m.s[3,k]*m.ud[k]/m.Lf*m.dt 
                                        if k<N-1 else Constraint.Skip) 
        # Objective function
        m.cteobj  = m.wg[2]*sum((m.s[4,k]-m.ref_cte)**2 for k in m.sk)
        m.epsiobj = m.wg[2]*sum((m.s[5,k]-m.ref_epsi)**2 for k in m.sk)
        m.vobj    = m.wg[0]*sum((m.s[3,k]-m.ref_v)**2 for k in m.sk)
        m.udobj   = m.wg[1]*sum(m.ud[k]**2 for k in m.uk)
        m.uaobj   = m.wg[1]*sum(m.ua[k]**2 for k in m.uk)
        m.sudobj  = m.wg[3]*sum((m.ud[k+1]-m.ud[k])**2 for k in m.uk1)
        m.suaobj  = m.wg[2]*sum((m.ua[k+1]-m.ua[k])**2 for k in m.uk1) 
        m.obj = Objective(expr = m.cteobj+m.epsiobj+m.vobj+m.udobj+m.uaobj+m.sudobj+m.suaobj, sense=minimize)
        
        self.iN = m#.create_instance()
        
    def Solve(self, state, coeffs):        
        self.iN.s0.reconstruct({0:state[0], 1: state[1], 2:state[2], 3:state[3], 4:state[4], 5:state[5]})
        self.iN.coeffs.reconstruct({0:coeffs[0], 1:coeffs[1], 2:coeffs[2], 3:coeffs[3]})
        self.iN.f_update.reconstruct()
        self.iN.s0_update.reconstruct()
        self.iN.psides_update.reconstruct()
        SolverFactory('ipopt').solve(self.iN)
        x_pred_vals = [self.iN.s[0,k]() for k in self.iN.sk]
        y_pred_vals = [self.iN.s[1,k]() for k in self.iN.sk]
        steering_angle = self.iN.ud[0]()
        throttle = self.iN.ua[0]()
        return x_pred_vals, y_pred_vals, steering_angle, throttle
