import math
import numpy as np
import matplotlib.pyplot as plt
import control as ct

K=22.0
Sbase=6.0e6
Vbase=13.2e3
R=1.21
X=2.834
TauOL=2.2

if __name__ == '__main__':
  Zbase = Vbase*Vbase/Sbase
  Z = math.sqrt(R*R + X*X)/Zbase
  KZ = K*Z
  G = ct.tf([-KZ], [1.0-KZ, TauOL])
  print ('G', G)
  Y = ct.feedback(G, sys2=1.0)
  print ('Y', Y)
  print (ct.stability_margins(Y))
  ct.bode_plot (Y)
  plt.show()
