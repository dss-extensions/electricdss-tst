# Copyright (C) 2021-2022 Battelle Memorial Institute
#
# plots the secondary circuit results from 2023 PES GM submittal
#  invoke 'python SCEplot.py no' after 'python SCErun.py no', without ExpControl
#  invoke 'python SCEplot.py yes' after 'python SCErun.py yes', with ExpControl

import win32com.client # pip install pywin32
import math
import numpy as np
from numpy import trapz
import matplotlib.pyplot as plt
import h5py
import sys

LINEWIDTH=0.5

def update_voltage_summary (row, vmin, vmax, vdiff, vwin):
  row['n'] += 1
  row['vmin'] = min (vmin, row['vmin'])
  row['vmax'] = max (vmax, row['vmax'])
  row['vdiff'] = max (vdiff, row['vdiff'])
  row['vwin'] = max (vwin, row['vwin'])

def tabulate_voltages (dict):
  summ = {'pvv':{'n':0, 'vmin': 1.0e9, 'vmax': 0.0, 'vdiff': 0.0, 'vwin': 0.0},
          'xfv':{'n':0, 'vmin': 1.0e9, 'vmax': 0.0, 'vdiff': 0.0, 'vwin': 0.0}}
  max_vwin = {'pvv':{'key':'', 'val':0.0},'xfv':{'key':'', 'val':0.0}}
  for key, v in dict.items():
    vmin = np.min(v)
    vmax = np.max(v)
    vwin = 0.0
    for i in range(60,len(v)):
      val = np.max(v[i-60:i]) - np.min(v[i-60:i])
      if val > vwin:
        vwin = val
    vdiff = np.max(np.abs(np.diff(v)))
    if 'pvv' in key:
      update_voltage_summary (summ['pvv'], vmin, vmax, vdiff, vwin)
      if vwin > max_vwin['pvv']['val']:
        max_vwin['pvv']['val'] = vwin
        max_vwin['pvv']['key'] = key
    elif 'xfv' in key:
      update_voltage_summary (summ['xfv'], vmin, vmax, vdiff, vwin)
      if vwin > max_vwin['xfv']['val']:
        max_vwin['xfv']['val'] = vwin
        max_vwin['xfv']['key'] = key
    else:
      print ('unrecognized voltage monitor', key)
  print ('Voltage Summary')
  for tag in ['xfv', 'pvv']:
    row = summ[tag]
    print (' {:s} {:6.4f} {:6.4f} {:6.4f} {:6.4f}'.format(tag, row['vmin'], row['vmax'], row['vdiff'], row['vwin']))
  return max_vwin

def tabulate_powers (dp, dq):
  ep = 0.0
  for key, vals in dp.items():
    ep += trapz(vals,dx=1.0/3600.0)
  eq = 0.0
  for key, vals in dq.items():
    eq += trapz(vals,dx=1.0/3600.0)
  print ('Power Summary: {:10.2f} + j{:10.2f} kvah over {:d} locations'.format(ep, eq, len(dp)))

def scan_vreg (dict):
  ret = {'min':{'key':'','val':1.0e6},'max':{'key':'','val':0.0}}
  for key, v in dict.items():
    test = v[43200]
    if test < ret['min']['val']:
      ret['min']['val'] = test
      ret['min']['key'] = key
    if test > ret['max']['val']:
      ret['max']['val'] = test
      ret['max']['key'] = key
  return ret

def plot_setpoints(ax, hrs, vreg, keymin, keymax):
  ax.set_ylabel ('Setpoint [pu]')
  ax.plot (hrs[3600:], vreg[keymax][3600:], label='Highest DER $V_{ref}$', color='red', linestyle='solid', linewidth=LINEWIDTH)
  ax.plot (hrs[3600:], vreg[keymin][3600:], label='Lowest DER $V_{ref}$', color='blue', linestyle='dotted', linewidth=2*LINEWIDTH)
  ax.legend(loc='best')

def plot_voltages(ax, hrs, vreg, keyxf, keypv):
  ax.set_ylabel ('Most-Fluctuating Voltage [pu]')
  ax.plot (hrs[3600:], volts[keypv][3600:], label='DER $V_T$', color='red', linestyle='solid', linewidth=LINEWIDTH)
  ax.plot (hrs[3600:], volts[keyxf][3600:], label='Transformer $V_T$', color='blue', linestyle='dotted', linewidth=2*LINEWIDTH)
  ax.legend(loc='best')

def plot_pvp(ax, hrs, p):
  ax.set_ylabel ('Total Solar P [kW]')
  ax.plot (hrs[3600:], -p[3600:], color='red', linewidth=LINEWIDTH)

def plot_pvq(ax, hrs, q):
  ax.set_ylabel ('Total Solar Q [kvar]')
  ax.plot (hrs[3600:], -q[3600:], color='red', linewidth=LINEWIDTH)

if __name__ == '__main__':
  EXPON = 'yes'
  if len(sys.argv) > 1:
    EXPON = sys.argv[1]
  volts = {}
  vreg = {}
  xfp = {}
  xfq = {}
  pvp = {}
  pvq = {}
  groups = {'volts':volts, 'vreg':vreg, 'xfp': xfp, 'xfq': xfq, 'pvp': pvp, 'pvq': pvq}
  with h5py.File('SCE_{:s}.hdf5'.format(EXPON), 'r') as f:
    data = f['hrs']['hrs']
    npts = data.len()
    hrs = np.zeros(npts)
    data.read_direct (hrs)
    for grp_name, dict in groups.items():
      grp = f[grp_name]
      for key in grp:
        dict[key] = np.zeros (npts)
        grp[key].read_direct (dict[key])

  tabulate_powers (pvp, pvq)
  max_vwin = tabulate_voltages (volts)
  minmax_vreg = scan_vreg (vreg)

  total_pv_p = np.zeros(npts)
  total_pv_q = np.zeros(npts)
  for key in pvp:
    total_pv_p += pvp[key]
    total_pv_q += pvq[key]

  # make a publication-quality plot
  plt.rc('font', family='serif')
  plt.rc('xtick', labelsize=8)
  plt.rc('ytick', labelsize=8)
  plt.rc('axes', labelsize=8)
  plt.rc('legend', fontsize=8)
  pWidth = 5.0
  pHeight = 7.0

  nrows = 4
  keymin = minmax_vreg['min']['key']
  keymax = minmax_vreg['max']['key']
  keyxf = max_vwin['xfv']['key']
  keypv = max_vwin['pvv']['key']
  if EXPON == 'yes':
    fig, ax = plt.subplots(4, 1, figsize=(pWidth, pHeight), constrained_layout=True)
    fig.suptitle ('Cloudy-Day Response of 180 DER With AARV', fontsize=10)
    plot_setpoints (ax[0], hrs, vreg, keymin, keymax)
    plot_voltages (ax[1], hrs, volts, keyxf, keypv)
    plot_pvp (ax[2], hrs, total_pv_p)
    plot_pvq (ax[3], hrs, total_pv_q)
  else:
    nrows = 2
    fig, ax = plt.subplots(2, 1, figsize=(pWidth, 0.6 * pHeight), constrained_layout=True)
    fig.suptitle ('Cloudy-Day Response of 180 DER at Unity Power Factor', fontsize=10)
    plot_voltages (ax[0], hrs, volts, keyxf, keypv)
    plot_pvp (ax[1], hrs, total_pv_p)

  ax[nrows-1].set_xlabel ('Time of Day [hr]')
  tticks = [6, 8, 10, 12, 14, 16, 18, 20]
  for i in range(nrows):
    ax[i].set_xlim (tticks[0], tticks[-1])
    ax[i].set_xticks (tticks)
    ax[i].grid()

  if EXPON == 'no':
    plt.savefig('Fig7.png', dpi=300)
  else: # yes
    plt.savefig('Fig8.png', dpi=300)
  plt.show()

