# Copyright (C) 2021-2022 Battelle Memorial Institute
#

import csv
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from numpy import trapz

vbase = 240.0
d1 = np.loadtxt('CloudAdap_Mon_pv1v_1.csv', skiprows=1, delimiter=',')
d2 = np.loadtxt('CloudAdap_Mon_pv1pq_1.csv', skiprows=1, delimiter=',')
d3 = np.loadtxt('CloudAdap_Mon_pv1st_1.csv', skiprows=1, delimiter=',')
vcloud = d1[:,2] / vbase
pcloud = d2[:,2]
qcloud = d2[:,3]
rcloud = d3[:,6]
tcloud = np.linspace(0.0,float(len(vcloud) - 1) / 3600.0,len(vcloud))

d1 = np.loadtxt('ClearAdap_Mon_pv1v_1.csv', skiprows=1, delimiter=',')
d2 = np.loadtxt('ClearAdap_Mon_pv1pq_1.csv', skiprows=1, delimiter=',')
d3 = np.loadtxt('ClearAdap_Mon_pv1st_1.csv', skiprows=1, delimiter=',')
vclear = d1[:,2] / vbase
pclear = d2[:,2]
qclear = d2[:,3]
rclear = d3[:,6]
tclear = np.linspace(0.0,float(len(vclear) - 1) / 3600.0,len(vclear))

fig, ax = plt.subplots(2, 2, figsize=(10,7))
xticks = [5, 9, 13, 17, 21]
vticks = [0.96, 0.98, 1.00, 1.02, 1.04, 1.06]
pticks = [-300, -250, -200, -150, -100, -50, 0, 50]

plt.suptitle('Adaptive Voltage Regulation, Tau=300s, Clear and Cloudy Days', fontsize=14)

ax[0,0].set_ylabel('Power [kVA]')
ax[0,0].plot(tclear, pclear, color='blue', label='Real', linewidth=1.0, linestyle='-.')
ax[0,0].plot(tclear, qclear, color='red',  label='Reactive', linewidth=0.5, linestyle='-')
ax[0,0].legend(loc='best')
ax[0,0].set_xticks(xticks)
ax[0,0].set_xlim(xticks[0], xticks[-1])
ax[0,0].set_yticks(pticks)
ax[0,0].set_ylim(pticks[0], pticks[-1])
ax[0,0].grid(color='grey', which='major', linestyle=':', linewidth=0.5)

ax[0,1].set_ylabel('Power [kVA]')
ax[0,1].plot(tcloud, pcloud, color='blue', label='Real', linewidth=1.0, linestyle='-.')
ax[0,1].plot(tcloud, qcloud, color='red',  label='Reactive', linewidth=0.5, linestyle='-')
ax[0,1].legend(loc='best')
ax[0,1].set_xticks(xticks)
ax[0,1].set_xlim(xticks[0], xticks[-1])
ax[0,1].set_yticks(pticks)
ax[0,1].set_ylim(pticks[0], pticks[-1])
ax[0,1].grid(color='grey', which='major', linestyle=':', linewidth=0.5)

ax[1,0].set_ylabel('Voltage [pu]')
ax[1,0].plot(tclear, rclear, color='blue', label='Target Vreg', linewidth=1.0, linestyle='-.')
ax[1,0].plot(tclear, vclear, color='red',  label='PCC Voltage', linewidth=0.5, linestyle='-')
ax[1,0].set_xticks(xticks)
ax[1,0].set_xlim(xticks[0], xticks[-1])
ax[1,0].set_yticks(vticks)
ax[1,0].set_ylim(vticks[0], vticks[-1])
ax[1,0].legend(loc='best')
ax[1,0].grid(color='grey', which='major', linestyle=':', linewidth=0.5)

ax[1,1].set_ylabel('Voltage [pu]')
ax[1,1].plot(tcloud, rcloud, color='blue', label='Target Vreg', linewidth=1.0, linestyle='-.')
ax[1,1].plot(tcloud, vcloud, color='red',  label='PCC Voltage', linewidth=0.5, linestyle='-')
ax[1,1].set_xticks(xticks)
ax[1,1].set_xlim(xticks[0], xticks[-1])
ax[1,1].set_yticks(vticks)
ax[1,1].set_ylim(vticks[0], vticks[-1])
ax[1,1].legend(loc='best')
ax[1,1].grid(color='grey', which='major', linestyle=':', linewidth=0.5)

ax[1,0].set_xlabel('Time of Day [hr]')
ax[1,1].set_xlabel('Time of Day [hr]')

plt.show()


