import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from scipy import interpolate
from math import hypot

t = np.arange(0, 2.5, .1)  # 一维数组（start,stop,step）
x = np.sin(2*np.pi*t)
y = np.cos(2*np.pi*t)

tcktuples,uarray = interpolate.splprep([x,y], s=0)
  # tcktuple:(t,c,k)包含节点向量，B样条系数，样条度的元组
  # uarray:参数值的数组
# print(tcktuples)
# print(uarray)
unew = np.arange(0, 1.01, 0.01)
splinevalues = interpolate.splev(unew, tcktuples)
# print(splinevalues)
fcl_X = splinevalues[0]
fcl_Y = splinevalues[1]
stot = 0
for i in range(len(splinevalues[0])-1):
    stot += hypot(splinevalues[0][i+1]-splinevalues[0][i], splinevalues[1][i+1]-splinevalues[1][i])

   
dX = np.diff(fcl_X)
dY = np.diff(fcl_Y)

psic = np.arctan2(dY,dX)
s = np.arange(0, stot, 1.0)
psic = psic[:len(s)]
print(psic)
print(s)

t, c, k = interpolate.splrep(s, psic, s=0, k=4)
psic_spl = interpolate.BSpline(t, c, k, extrapolate=False)

kappac_spl = psic_spl.derivative(nu=1)
print(kappac_spl(s))
kappac_spl = psic_spl.derivative(nu=2)
print(kappac_spl(s))

# plt.figure(figsize=(10,10))
# plt.plot(x,y, 'x', splinevalues[0], splinevalues[1],
#     np.sin(2*np.pi*unew), np.cos(2*np.pi*unew), x, y, 'b')

# plt.legend(['Linear', 'Cubic Spline', 'True'])
# plt.axis([-1.25, 1.25, -1.25, 1.25])
# plt.title('Parametric Spline Interpolation Curve')

# plt.show()
