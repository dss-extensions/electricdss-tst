# Copyright (C) 2021-2022 Battelle Memorial Institute
#
import win32com.client # pip install pywin32
import math
import numpy as np
import matplotlib.pyplot as plt
import os

template = """
Clear
New Circuit.Nantucket pu=1.0 R1=0.0001 X1=0.0001 R0=0.0001 X0=0.0001 basekv=13.2

// these PCC impedances include the effect of loading, so they have a lower X/R ratio
new line.pcc1 bus1=sourcebus bus2=pcc1 r1=1.743 x1=2.679 r0=3.704 x0=3.024 c1=0.0 c0=0.0
new line.pcc2 bus1=sourcebus bus2=pcc2 r1=1.743 x1=2.679 r0=3.704 x0=3.024 c1=0.0 c0=0.0
new monitor.pcc1vi element=line.pcc1 terminal=2 mode=96
new monitor.pcc2vi element=line.pcc2 terminal=2 mode=96

New Loadshape.cycle npts=10 interval=0 hour=[0.00,0.49,0.50,0.99,1.00,1.49, 1.50, 1.99,2.00,2.50] 
~                                      mult=[0.00,0.00,1.00,1.00,0.00,0.00,-1.00,-1.00,0.00,0.00]
~ action=normalize
New Loadshape.halfcycle npts=10 interval=0 hour=[0.00,0.49,0.50,0.99,1.00,1.49, 1.50, 1.99,2.00,2.50] 
~                                          mult=[0.00,0.00,0.00,0.00,0.00,0.00,-1.00,-1.00,0.00,0.00]
~ action=normalize

// two similar battery systems, one for each PCC
new Storage.bess1 bus1=bess1 phases=3 kV=13.2 kWrated=6000 kva=7000 kWhrated=48000 kWhstored=24000 
~ dispmode=follow daily=cycle
new transformer.bess1 windings=2 buses=[pcc1 BESS1] conns=[w,w] kvas=[7500,7500] kvs=[13.2,13.2] xhl=0.1 %loadloss=0.1
new Storage.BESS2 like=BESS1 bus1=BESS2
New Transformer.BESS2 like=BESS1 buses=[pcc2 BESS2]
New Monitor.bess1pq Element=Storage.BESS1 Terminal=1 mode=65 PPolar=No
New Monitor.bess2pq Element=Storage.BESS2 Terminal=1 mode=65 PPolar=No

// 1547-2018 default volt-var settings for category B, on VARMAX
New XYcurve.voltvar1547b npts=6 Yarray=[1,1,0,0,-1,-1] Xarray=[.5,0.92,0.98,1.02,1.08,1.5]
// volt-watt settings to start limiting at 1.03 pu, can't absorb P (note that maximum V2 is 1.10)
New XYcurve.voltwatt1547pv npts=4 Yarray=[1.0,1.0,0.0,0.0] Xarray=[0.0,1.03,1.06,2.00]

// PVSystem in parallel with BESS1, has 0.5 kW and 3600 kVA rating to superimpose volt-var on BESS1
New PVSystem.PV1 bus1=pcc1 phases=3 kV=13.2 irradiance=0.5 pmpp=1 kVA=3600 kvarmax=3600 kvarmaxabs=3600 varfollowinverter=false
New InvControl.pv1 pvsystemlist=(pv1) mode=VOLTVAR RefReactivePower=VARMAX
~ voltage_curvex_ref=rated vvc_curve1=voltvar1547b deltaQ_factor=0.2 LPFtau=2.2 RateOfChangeMode=LPF // eventlog=yes
new monitor.pv1pq element=PVSystem.PV1 terminal=1 mode=65 PPolar=NO

// PVSystem in place of BESS2, superimposing volt-watt on the BESS2 dispatch, with zero Q
// the PVSystem by itself can absorb P when %cutin and %cutout < 0, but this is unstable with VOLTWATT
New PVSystem.PV2 bus1=pcc2 phases=3 kV=13.2 irradiance=1.0 pmpp=6000 kVA=6000 kvarmax=6000 kvarmaxabs=6000
~ daily=cycle varfollowinverter=false %cutin=0.01 %cutout=0.01
New InvControl.pv2 pvsystemlist=(pv2) mode=VOLTWATT
~ voltage_curvex_ref=rated voltwatt_curve=voltwatt1547pv deltaP_factor=0.1 LPFtau=2.2 RateOfChangeMode=LPF // eventlog=yes
new monitor.pv2pq element=PVSystem.PV2 terminal=1 mode=65 PPolar=NO
// let the BESS handle charging half of the cycle, not responsive to undervoltage
edit storage.bess2 daily=halfcycle

// PV system state variables: 
//    1 = irradiance
//    2 = panel kW
//    3 = Power temperature factor
//    4 = efficiency,
//    5 = Vreg from the parent ExpControl or InvControl
// Storage system state variables:
//    1 = kwh stored
//    2 = state
//    3 = kw out
//    4 = kw in
//    5 = kw total losses
//    6 = kw idling losses
//    7 = kwh change
new monitor.bess1st element=storage.bess1 terminal=1 mode=3
//new monitor.bess2st element=storage.bess2 terminal=1 mode=3
//new monitor.pv1st element=PVSystem.PV1 terminal=1 mode=3

set controlmode=static
set maxcontroliter=1000
set voltagebases=[13.2]

CalcV
solve
solve mode=daily number=9000 stepsize=1s
"""

class DSS:
  def __init__(self):
    self.engine = win32com.client.Dispatch("OpenDSSEngine.DSS")
    self.engine.Start("0")
    self.text = self.engine.Text
    self.text.Command = "clear"
    self.circuit = self.engine.ActiveCircuit
    print (self.engine.Version)

if __name__ == '__main__':
  case_str = template
  fp = open ('case.dss', mode='w')
  print (case_str, file=fp)
  fp.close ()

  cwd = os.getcwd() # the DSS engine may change directories!
  # run the base case
  d = DSS()
  d.text.command = 'cd {:s}'.format(cwd)
  d.text.command = 'redirect case.dss'
  monitors = {}
  mon = d.circuit.monitors
  more = mon.first
  npts = 0
  vbase = 7621.0
  while more > 0:
    key = mon.Name
    npts = mon.SampleCount
    nchan = mon.NumChannels
    print ('Monitor {:s} has {:d} samples and {:d} channels:'.format (key, npts, nchan), mon.Header)
    if 'vi' in key:
      monitors[key] = {'V': np.array (mon.Channel(1))/vbase, 'I': np.array (mon.Channel(2))}
    elif 'pq' in key:
      monitors[key] = {'P': np.array (mon.Channel(1)), 'Q': np.array (mon.Channel(2))}
    more = mon.next

  t = np.linspace(0.0, npts - 1.0, npts)

  # summarize the step changes
  print ('Note: P and Q follow load convention')
  print ('PCC   Vstep1   Pstep1   Qstep1   Vstep2   Pstep2   Qstep2')
  for idx in range(2):
    pcc = idx+1
    keyvi = 'pcc{:d}vi'.format(pcc)
    keypq = 'bess{:d}pq'.format(pcc)
    keypv = 'pv{:d}pq'.format(pcc)
    vchan = monitors[keyvi]['V']
    pchan = monitors[keypq]['P']
    qchan = monitors[keypq]['Q']
    pvqchan = monitors[keypv]['Q']
    print ('{:3d} {:8.4f} {:8.2f} {:8.2f} {:8.4f} {:8.2f} {:8.2f}'.format(pcc, 
      vchan[3550]-1.0, pchan[3550], qchan[3550]+pvqchan[3550], 
      vchan[7150]-1.0, pchan[7150], qchan[7150]+pvqchan[7150]))
  # make a publication-quality plot
  plt.rc('font', family='serif')
  plt.rc('xtick', labelsize=8)
  plt.rc('ytick', labelsize=8)
  plt.rc('axes', labelsize=8)
  plt.rc('legend', fontsize=8)
  pWidth = 5.0
  pHeight = pWidth / 1.618
  pHeight = 7.0

  fig, ax = plt.subplots(3, 1, figsize=(pWidth, pHeight), constrained_layout=True)
  fig.suptitle ('Nantucket Steps with InvControl', fontsize=10)

  ax[0].plot (t, monitors['pcc1vi']['V'], label='PCC1', linestyle='-', color='red')
  ax[0].plot (t, monitors['pcc2vi']['V'], label='PCC2', linestyle='--', color='blue')
  ax[0].set_ylabel ('Voltage [pu]')

  ax[1].set_ylabel ('Real Power [kW]')
  ax[1].plot (t, -monitors['bess1pq']['P'] + monitors['pv1pq']['P'], label='BESS1', linestyle='-', color='red')
  ax[1].plot (t, -monitors['bess2pq']['P'] + monitors['pv2pq']['P'], label='BESS2', linestyle='--', color='blue')

  ax[2].set_ylabel ('Reactive Power [kvar]')
  ax[2].plot (t, -monitors['bess1pq']['Q'] + monitors['pv1pq']['Q'], label='BESS1', linestyle='-', color='red')
  ax[2].plot (t, -monitors['bess2pq']['Q'] + monitors['pv2pq']['Q'], label='BESS2', linestyle='--', color='blue')

  xticks = [0, 1800, 3600, 5400, 7200, 9000]
  for i in range(3):
    ax[i].set_xticks (xticks)
    ax[i].set_xlim(xticks[0], xticks[-1])
    ax[i].legend (loc='best')
    ax[i].grid()
  ax[2].set_xlabel ('Time [s]')

  plt.show()

