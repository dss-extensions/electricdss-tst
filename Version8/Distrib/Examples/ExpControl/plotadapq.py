import csv
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from numpy import trapz

vbase = 240.0
d1 = np.loadtxt('CloudAdapQ_Mon_pv1v_1.csv', skiprows=1, delimiter=',')
d2 = np.loadtxt('CloudAdapQ_Mon_pv1pq_1.csv', skiprows=1, delimiter=',')
d3 = np.loadtxt('CloudAdapQ_Mon_pv1st_1.csv', skiprows=1, delimiter=',')
va = d1[:,2] / vbase
pa = d2[:,2]
qa = d2[:,3]
ra = d3[:,6]
t = np.linspace(0.0,float(len(va) - 1) / 3600.0,len(va))
d1 = np.loadtxt('ClearAdapQ_Mon_pv1v_1.csv', skiprows=1, delimiter=',')
d2 = np.loadtxt('ClearAdapQ_Mon_pv1pq_1.csv', skiprows=1, delimiter=',')
d3 = np.loadtxt('ClearAdapQ_Mon_pv1st_1.csv', skiprows=1, delimiter=',')
vb = d1[:,2] / vbase
pb = d2[:,2]
qb = d2[:,3]
rb = d3[:,6]

maxval = 0.0
for i in range(60,len(va)):
    val = np.max(va[i-60:i]) - np.min(va[i-60:i])
    if val > maxval:
        maxval = val
#print (np.min(va), np.max(va), np.max(np.abs(np.diff(va))), 100.0 * maxval)
maxval = 0.0
for i in range(60,len(va)):
    val = np.max(vb[i-60:i]) - np.min(vb[i-60:i])
    if val > maxval:
        maxval = val
#print (np.min(vb), np.max(vb), np.max(np.abs(np.diff(vb))), 100.0 * maxval)

fig, ax = plt.subplots(1, 2, figsize=(10,4))
xticks = [5, 9, 13, 17, 21]
vticks = [0.94, 0.96, 0.98, 1.00, 1.02, 1.04, 1.06]
qticks = [-50, 0, 50, 100, 150]

plt.suptitle('Adaptive Voltage Regulation, Tau=300s, Qbias=-90 kvar', fontsize=14)

ax[0].set_ylabel('Voltage [pu]')
ax[0].plot(t, va, color='red',  label='Cloudy Day', linewidth=0.5, linestyle='-')
ax[0].plot(t, vb, color='blue', label='Clear Day', linewidth=1.0, linestyle='-.')
ax[0].set_xticks(xticks)
ax[0].set_xlim(xticks[0], xticks[-1])
ax[0].set_yticks(vticks)
ax[0].set_ylim(vticks[0], vticks[-1])
ax[0].legend(loc='best')
ax[0].grid(color='grey', which='major', linestyle=':', linewidth=0.5)
ax[0].set_xlabel('Time of Day [hr]')

ax[1].set_ylabel('Reactive Power [kvar]')
ax[1].plot(t, qa, color='red',  label='Cloudy Day', linewidth=0.5, linestyle='-')
ax[1].plot(t, qb, color='blue', label='Clear Day', linewidth=1.0, linestyle='-.')
ax[1].set_xticks(xticks)
ax[1].set_xlim(xticks[0], xticks[-1])
ax[1].set_yticks(qticks)
ax[1].set_ylim(qticks[0], qticks[-1])
ax[1].legend(loc='best')
ax[1].grid(color='grey', which='major', linestyle=':', linewidth=0.5)
ax[1].set_xlabel('Time of Day [hr]')

plt.show()


