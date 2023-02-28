# Copyright (C) 2021-2022 Battelle Memorial Institute
#
import csv
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from numpy import trapz

vbase = 240.0
pbase = 300.0 # 285.0

d1 = np.loadtxt('CloudAdap_Mon_pv1v_1.csv', skiprows=1, delimiter=',')
d2 = np.loadtxt('CloudAdap_Mon_pv1pq_1.csv', skiprows=1, delimiter=',')
d3 = np.loadtxt('CloudAdap_Mon_pv1st_1.csv', skiprows=1, delimiter=',')
va = d1[:,2] / vbase
pa = d2[:,2] / pbase
qa = d2[:,3] / pbase
ra = d3[:,6]
t = np.linspace(0.0,float(len(va) - 1) / 3600.0,len(va))
d1 = np.loadtxt('CloudUnity_Mon_pv1v_1.csv', skiprows=1, delimiter=',')
vb = d1[:,2] / vbase

fig, ax = plt.subplots(1, 2, figsize=(10,4))
xticks = [0, 4, 8, 12, 16, 20, 24]

ax[0].set_title('PV Output - Passive Convention')
ax[0].set_ylabel('[pu of inverter base]')
ax[0].plot(t, pa, color='red',  label='P', linewidth=0.5, linestyle='-')
ax[0].plot(t, qa, color='blue', label='Q', linewidth=0.5, linestyle='-.')
ax[0].set_xticks(xticks)
ax[0].set_xlim(xticks[0], xticks[-1])
ax[0].legend(loc='best')
ax[0].grid(color='grey', which='major', linestyle=':', linewidth=0.5)
ax[0].set_xlabel('Time of Day [hr]')

ax[1].set_title('System and Reference Voltages')
ax[1].set_ylabel('[pu]')
ax[1].plot(t, vb, color='gray', label='Vunity', linewidth=0.5, linestyle='dotted')
ax[1].plot(t, va, color='red',  label='Vsys', linewidth=1.0, linestyle='solid')
ax[1].plot(t, ra, color='blue', label='Vref', linewidth=1.0, linestyle='dashed')
ax[1].set_xticks(xticks)
ax[1].set_xlim(xticks[0], xticks[-1])
ax[1].legend(loc='best')
ax[1].grid(color='grey', which='major', linestyle=':', linewidth=0.5)
ax[1].set_xlabel('Time of Day [hr]')

plt.show()


