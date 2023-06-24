# Copyright (C) 2021-2023 Battelle Memorial Institute
# Adapted for DSS-Extensions by Paulo Meira
#

from expcontrol_common import get_dss_engine, dss_suffix
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

template = """
Clear
New Circuit.Nantucket pu=1.0 R1=0.0001 X1=0.0001 R0=0.0001 X0=0.0001 basekv=13.2

// comparing uncontrolled inverters at unity pf, two different PCC impedances
new line.pcc1 bus1=sourcebus bus2=pcc1 r1=1.744 x1=2.6797 r0=3.7061 x0=3.0256 c1=0.0 c0=0.0
new line.pcc2 bus1=sourcebus bus2=pcc2 r1=1.210 x1=2.8339 r0=3.9612 x0=3.2135 c1=0.0 c0=0.0

New Loadshape.cycle npts=10 interval=0 hour=[0.00,0.124,0.125,0.700,0.701,1.790, 1.800, 2.375, 2.376, 2.500] 
~                                      mult=[0.00,0.000,1.000,1.000,0.000,0.000,-1.000,-1.000, 0.000, 0.000]
~ action=normalize

// two similar battery systems, one for each PCC
new Storage.bess1 bus1=bess1 phases=3 kV=13.2 kWrated={DKW} kva=7000 kWhrated=48000 kWhstored=24000 
~ dispmode=follow daily=cycle
new transformer.bess1 windings=2 buses=[pcc1 BESS1] conns=[w,w] kvas=[7500,7500] kvs=[13.2,13.2] xhl={XHL} %loadloss={XLL}
new Storage.BESS2 like=BESS1 bus1=BESS2
New Transformer.BESS2 like=BESS1 buses=[pcc2 BESS2]

// PV systems for Q response
New PVSystem.PV1 bus1=pcc1 phases=3 kV=13.2 irradiance=1.0 pmpp=1 kVA=6000 kvarmax=6000 kvarmaxabs=6000 varfollowinverter=false %cutin=0.01 %cutout=0.01
New PVSystem.PV2 bus1=pcc2 phases=3 kV=13.2 irradiance=1.0 pmpp=1 kVA=6000 kvarmax=6000 kvarmaxabs=6000 varfollowinverter=false %cutin=0.01 %cutout=0.01
New ExpControl.pv1 deltaQ_factor=0.3 vreg=1.0 slope=22 vregtau=300 vregmax=1.05 Tresponse=5 preferQ=yes

new monitor.pcc1vi element=transformer.bess1 terminal=2 mode=96
new monitor.pcc2vi element=transformer.bess2 terminal=2 mode=96
//new monitor.pcc1vi element=line.pcc1 terminal=2 mode=96
//new monitor.pcc2vi element=line.pcc2 terminal=2 mode=96
New Monitor.bess1pq Element=Storage.BESS1 Terminal=1 mode=65 PPolar=No
New Monitor.bess2pq Element=Storage.BESS2 Terminal=1 mode=65 PPolar=No
New Monitor.pv1pq Element=PVSystem.PV1 Terminal=1 mode=65 PPolar=No
New Monitor.pv2pq Element=PVSystem.PV2 Terminal=1 mode=65 PPolar=No
New Monitor.pv1st Element=PVSystem.PV1 Terminal=1 mode=3
New Monitor.pv2st Element=PVSystem.PV2 Terminal=1 mode=3

set controlmode=static
set maxcontroliter=1000
set voltagebases=[13.2]

CalcV
solve
solve mode=daily number=9000 stepsize=1s
"""

upf_template = """
Clear
New Circuit.Nantucket pu=1.0 R1=0.0001 X1=0.0001 R0=0.0001 X0=0.0001 basekv=13.2

// comparing uncontrolled inverters at unity pf, two different PCC impedances
new line.pcc1 bus1=sourcebus bus2=pcc1 r1=1.744 x1=2.6797 r0=3.7061 x0=3.0256 c1=0.0 c0=0.0
new line.pcc2 bus1=sourcebus bus2=pcc2 r1=1.210 x1=2.8339 r0=3.9612 x0=3.2135 c1=0.0 c0=0.0

New Loadshape.cycle npts=10 interval=0 hour=[0.00,0.124,0.125,0.700,0.701,1.790, 1.800, 2.375, 2.376, 2.500] 
~                                      mult=[0.00,0.000,1.000,1.000,0.000,0.000,-1.000,-1.000, 0.000, 0.000]
~ action=normalize

// two similar battery systems, one for each PCC
new Storage.bess1 bus1=bess1 phases=3 kV=13.2 kWrated={DKW} kva=7000 kWhrated=48000 kWhstored=24000 
~ dispmode=follow daily=cycle
new transformer.bess1 windings=2 buses=[pcc1 BESS1] conns=[w,w] kvas=[7500,7500] kvs=[13.2,13.2] xhl={XHL} %loadloss={XLL}
new Storage.BESS2 like=BESS1 bus1=BESS2
New Transformer.BESS2 like=BESS1 buses=[pcc2 BESS2]

new monitor.pcc3vi element=transformer.bess1 terminal=2 mode=96
new monitor.pcc4vi element=transformer.bess2 terminal=2 mode=96
New Monitor.bess3pq Element=Storage.BESS1 Terminal=1 mode=65 PPolar=No
New Monitor.bess4pq Element=Storage.BESS2 Terminal=1 mode=65 PPolar=No

set controlmode=static
set maxcontroliter=1000
set voltagebases=[13.2]

CalcV
solve
solve mode=daily number=9000 stepsize=1s
"""

dflt_template = """
Clear
New Circuit.Nantucket pu=1.0 R1=0.0001 X1=0.0001 R0=0.0001 X0=0.0001 basekv=13.2

// these PCC impedances include the effect of loading, so they have a lower X/R ratio
new line.pcc1 bus1=sourcebus bus2=pcc1 r1=1.743 x1=2.679 r0=3.704 x0=3.024 c1=0.0 c0=0.0
new monitor.pcc5vi element=line.pcc1 terminal=2 mode=96

New Loadshape.cycle npts=10 interval=0 hour=[0.00,0.124,0.125,0.700,0.701,1.790, 1.800, 2.375, 2.376, 2.500] 
~                                      mult=[0.00,0.000,1.000,1.000,0.000,0.000,-1.000,-1.000, 0.000, 0.000]
~ action=normalize

// two similar battery systems, one for each PCC
new Storage.bess1 bus1=bess1 phases=3 kV=13.2 kWrated={DKW} kva=7000 kWhrated=48000 kWhstored=24000 
~ dispmode=follow daily=cycle
new transformer.bess1 windings=2 buses=[pcc1 BESS1] conns=[w,w] kvas=[7500,7500] kvs=[13.2,13.2] xhl=0.1 %loadloss=0.1
New Monitor.bess5pq Element=Storage.BESS1 Terminal=1 mode=65 PPolar=No

// 1547-2018 default volt-var settings for category B, on VARMAX
New XYcurve.voltvar1547b npts=6 Yarray=[1,1,0,0,-1,-1] Xarray=[.5,0.92,0.98,1.02,1.08,1.5]
// volt-watt settings to start limiting at 1.03 pu, can't absorb P (note that maximum V2 is 1.10)
New XYcurve.voltwatt1547pv npts=4 Yarray=[1.0,1.0,0.0,0.0] Xarray=[0.0,1.03,1.06,2.00]

// PVSystem in parallel with BESS1, has 0.5 kW and 3600 kVA rating to superimpose volt-var on BESS1
New PVSystem.PV1 bus1=pcc1 phases=3 kV=13.2 irradiance=0.5 pmpp=1 kVA=3600 kvarmax=6000 kvarmaxabs=6000 varfollowinverter=false
New InvControl.pv1 pvsystemlist=(pv1) mode=VOLTVAR RefReactivePower=VARMAX
~ voltage_curvex_ref=rated vvc_curve1=voltvar1547b deltaQ_factor=0.3 LPFtau=2.2 RateOfChangeMode=LPF // eventlog=yes
new monitor.pv5pq element=PVSystem.PV1 terminal=1 mode=65 PPolar=NO

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
//new monitor.bess5st element=storage.bess1 terminal=1 mode=3
//new monitor.pv5st element=PVSystem.PV1 terminal=1 mode=3

set controlmode=static
set maxcontroliter=1000
set voltagebases=[13.2]

CalcV
solve
solve mode=daily number=9000 stepsize=1s
"""

DKW = 6000.0 # 2000.0

class DSS:
  def __init__(self):
    self.engine = get_dss_engine()
    self.engine.Start(0)
    self.text = self.engine.Text
    self.text.Command = "clear"
    self.circuit = self.engine.ActiveCircuit
    print (self.engine.Version)

if __name__ == '__main__':
  XHL = 0.0001
  XLL = 0.0001
  FullLoadOnly = False
  if len(sys.argv) > 1:
    if sys.argv[1] == 'xfmr':
      XHL=5.72
      XLL=0.55
    elif sys.argv[1] == 'FL':
      FullLoadOnly = True

  # running ExpControl cases; channel 1 = Full-Load Impedance, channel 2 = No-Load Impedance
  case_str = template.format(XHL=XHL, XLL=XLL, DKW=DKW)
  fp = open ('case.dss', mode='w')
  print (case_str, file=fp)
  fp.close ()
  cwd = os.getcwd() # the DSS engine may change directories!
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
    elif 'st' in key:
      monitors[key] = {'Vreg': np.array (mon.Channel(5))}
      # patch for the COM engine
      monitors[key]['Vreg'][0] = monitors[key]['Vreg'][1]
    more = mon.next

  t = np.linspace(0.0, npts - 1.0, npts)

  # running Unity Power Factor cases for baseline; channel 3 = Full-Load Impedance, channel 4 = No-Load Impedance
  case_str = upf_template.format(XHL=XHL, XLL=XLL, DKW=DKW)
  fp = open ('case.dss', mode='w')
  print (case_str, file=fp)
  fp.close ()
  d.text.command = 'cd {:s}'.format(cwd)
  d.text.command = 'redirect case.dss'
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
    elif 'st' in key:
      monitors[key] = {'Vreg': np.array (mon.Channel(5))}
      # patch for the COM engine
      monitors[key]['Vreg'][0] = monitors[key]['Vreg'][1]
    more = mon.next
  nopv = np.zeros(npts)

  # running Volt-Var Cat B case; channel 5 = Full-Load Impedance
  case_str = dflt_template.format(DKW=DKW)
  fp = open ('case.dss', mode='w')
  print (case_str, file=fp)
  fp.close ()
  d.text.command = 'cd {:s}'.format(cwd)
  d.text.command = 'redirect case.dss'
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

  # summarize the step changes
  print ('Note: P and Q follow load convention')
  print ('PCC   Vstep1   Pstep1   Qstep1  Vfinal1   Vstep2   Pstep2   Qstep2  Vfinal2')
  for idx in range(5):
    pcc = idx+1
    keyvi = 'pcc{:d}vi'.format(pcc)
    keypq = 'bess{:d}pq'.format(pcc)
    keypv = 'pv{:d}pq'.format(pcc)
    vchan = monitors[keyvi]['V']
    pchan = monitors[keypq]['P']
    qchan = monitors[keypq]['Q']
    if keypv in monitors:
      pvqchan = monitors[keypv]['Q']
    else:
      pvqchan = nopv
    print ('{:3d} {:8.4f} {:8.2f} {:8.2f} {:8.4f} {:8.4f} {:8.2f} {:8.2f} {:8.4f}'.format(pcc, 
      vchan[450]-1.0, pchan[450], qchan[450]+pvqchan[450], vchan[2520] - 1.0,
      vchan[6480]-1.0, pchan[6480], qchan[6480]+pvqchan[6480], vchan[8550] - 1.0,))
  # make a publication-quality plot
  plt.rc('font', family='serif')
  plt.rc('xtick', labelsize=8)
  plt.rc('ytick', labelsize=8)
  plt.rc('axes', labelsize=8)
  plt.rc('legend', fontsize=8)
  pWidth = 5.0
  pHeight = pWidth / 1.618
  pHeight = 7.0

  if FullLoadOnly: # summary plot for the 2023 PES General Meeting
    fig, ax = plt.subplots(3, 1, figsize=(pWidth, pHeight), constrained_layout=True)

    ax[0].set_title ('BESS Discharges and then Charges at $\Delta$P = $\pm$ {:.1f} MW'.format(DKW*0.001))
    ax[0].set_ylabel ('Real Power [MW]')
    ax[0].plot (t, (-monitors['bess1pq']['P'] - monitors['pv1pq']['P'])*0.001, color='red')

    ax[1].set_title ('$V_T$ Changes Slowly and $V_{ref}$ Approaches $V_T$')
    ax[1].plot (t, monitors['pcc3vi']['V'], label='$V_T$ (Unity  PF)', linestyle='dotted', color='green')
    ax[1].plot (t, monitors['pcc5vi']['V'], label='$V_T$ (Volt-Var)', linestyle='dashed', color='magenta')
    ax[1].plot (t, monitors['pcc1vi']['V'], label='$V_T$ (AARV)', linestyle='-', color='red')
    ax[1].plot (t, monitors['pv1st']['Vreg'], label='$V_{ref}$ (AARV)', linestyle='-.', color='blue')
    ax[1].set_ylabel ('Voltage [pu]')
    ax[1].legend (loc='best')

    ax[2].set_title ('$\Delta$Q Resists $V_T$, Reduces Worst $d$ from -6.95% to -2.75%')
    ax[2].set_ylabel ('Reactive Power [Mvar]')
    ax[2].plot (t, nopv, label='$\Delta$Q (Unity  PF)', linestyle='dotted', color='green')
    ax[2].plot (t, (-monitors['bess5pq']['Q'] - monitors['pv5pq']['Q'])*0.001, label='$\Delta$Q (Volt-Var)', linestyle='dashed', color='magenta')
    ax[2].plot (t, (-monitors['bess1pq']['Q'] - monitors['pv1pq']['Q'])*0.001, label='$\Delta$Q (AARV)', color='red')
    ax[2].legend (loc='best')
  else:
    fig, ax = plt.subplots(3, 1, figsize=(pWidth, pHeight), constrained_layout=True)
    fig.suptitle ('Nantucket BESS $\Delta$P Steps with AARV', fontsize=10)

    ax[0].plot (t, monitors['pcc1vi']['V'], label='FL $V_T$', linestyle='-', color='red')
    ax[0].plot (t, monitors['pcc2vi']['V'], label='NL $V_T$', linestyle='--', color='blue')
    ax[0].plot (t, monitors['pv1st']['Vreg'], label='FL $V_{ref}$', linestyle='-.', color='magenta')
    ax[0].plot (t, monitors['pv2st']['Vreg'], label='NL $V_{ref}$', linestyle=':', color='green')
    ax[0].set_ylabel ('Voltage [pu]')
    ax[0].legend (loc='best')

    ax[1].set_ylabel ('Real Power [kW]')
    ax[1].plot (t, -monitors['bess1pq']['P'] - monitors['pv1pq']['P'], label='FL $\Delta$P', linestyle='-', color='red')
    ax[1].plot (t, -monitors['bess2pq']['P'] - monitors['pv2pq']['P'], label='NL $\Delta$P', linestyle='--', color='blue')
    ax[1].legend (loc='best')

    ax[2].set_ylabel ('Reactive Power [kvar]')
    ax[2].plot (t, -monitors['bess1pq']['Q'] - monitors['pv1pq']['Q'], label='FL $\Delta$Q', linestyle='-', color='red')
    ax[2].plot (t, -monitors['bess2pq']['Q'] - monitors['pv2pq']['Q'], label='NL $\Delta$Q', linestyle='--', color='blue')
    ax[2].legend (loc='best')

  xticks = [0, 1800, 3600, 5400, 7200, 9000]
  for i in range(3):
    ax[i].set_xticks (xticks)
    ax[i].set_xlim(xticks[0], xticks[-1])
    ax[i].grid()
  ax[2].set_xlabel ('Time [s]')

  if FullLoadOnly:
    plt.savefig(f'PosterBESS_{dss_suffix}.png', dpi=600)
  else:
    plt.savefig(f'Fig4_{dss_suffix}.png', dpi=300)
  plt.show()

