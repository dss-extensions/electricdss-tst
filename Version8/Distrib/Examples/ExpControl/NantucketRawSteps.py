# Copyright (C) 2021-2022 Battelle Memorial Institute
# Adapted for DSS Extensions by Paulo Meira
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
new line.pcc1 bus1=sourcebus bus2=pcc1 r1={RFL} x1={XFL} r0=3.7061 x0=3.0256 c1=0.0 c0=0.0
new line.pcc2 bus1=sourcebus bus2=pcc2 r1={RNL} x1={XNL} r0=3.9612 x0=3.2135 c1=0.0 c0=0.0
//new load.pcc2 bus1=pcc2 phases=3 conn=2 kv=13.2 kw=7519.0 kvar=-6329.0 model=5
//new monitor.pcc1vi element=line.pcc1 terminal=2 mode=96
//new monitor.pcc2vi element=line.pcc2 terminal=2 mode=96

New Loadshape.cycle npts=10 interval=0 hour=[0.00,0.49,0.50,0.99,1.00,1.49, 1.50, 1.99,2.00,2.50] 
~                                      mult=[0.00,0.00,1.00,1.00,0.00,0.00,-1.00,-1.00,0.00,0.00]
~ action=normalize

// two similar battery systems, one for each PCC
new Storage.bess1 bus1=bess1 phases=3 kV=13.2 kWrated=6000 kva=7000 kWhrated=48000 kWhstored=24000 
~ dispmode=follow daily=cycle
new transformer.bess1 windings=2 buses=[pcc1 BESS1] conns=[w,w] kvas=[7500,7500] kvs=[13.2,13.2] xhl={XHL} %loadloss={XLL}
new Storage.BESS2 like=BESS1 bus1=BESS2
New Transformer.BESS2 like=BESS1 buses=[pcc2 BESS2]

new monitor.pcc1vi element=transformer.bess1 terminal=2 mode=96
new monitor.pcc2vi element=transformer.bess2 terminal=2 mode=96
New Monitor.bess1pq Element=Storage.BESS1 Terminal=1 mode=65 PPolar=No
New Monitor.bess2pq Element=Storage.BESS2 Terminal=1 mode=65 PPolar=No

set controlmode=static
set maxcontroliter=1000
set voltagebases=[13.2]

CalcV
solve
solve mode=daily number=9000 stepsize=1s
"""

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
  if len(sys.argv) > 1:
    if sys.argv[1] == 'xfmr':
      XHL=5.72
      XLL=0.55
  case_str = template.format(RFL=1.744, XFL=2.680, RNL=1.210, XNL=2.834, XHL=XHL, XLL=XLL)
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
    vchan = monitors[keyvi]['V']
    pchan = monitors[keypq]['P']
    qchan = monitors[keypq]['Q']
    print ('{:3d} {:8.4f} {:8.2f} {:8.2f} {:8.4f} {:8.2f} {:8.2f}'.format(pcc, 
      vchan[3550]-1.0, pchan[3550], qchan[3550], 
      vchan[7150]-1.0, pchan[7150], qchan[7150]))
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
  fig.suptitle ('Nantucket Steps at Unity Power Factor', fontsize=10)

  ax[0].plot (t, monitors['pcc1vi']['V'], label='PCC1(FL)', linestyle='-', color='red')
  ax[0].plot (t, monitors['pcc2vi']['V'], label='PCC2(NL)', linestyle='--', color='blue')
  ax[0].set_ylabel ('Voltage [pu]')

  ax[1].set_ylabel ('Real Power [kW]')
  ax[1].plot (t, -monitors['bess1pq']['P'], label='BESS1(FL)', linestyle='-', color='red')
  ax[1].plot (t, -monitors['bess2pq']['P'], label='BESS2(NL)', linestyle='--', color='blue')

  ax[2].set_ylabel ('Reactive Power [kvar]')
  ax[2].plot (t, -monitors['bess1pq']['Q'], label='BESS1(FL)', linestyle='-', color='red')
  ax[2].plot (t, -monitors['bess2pq']['Q'], label='BESS2(NL)', linestyle='--', color='blue')

  xticks = [0, 1800, 3600, 5400, 7200, 9000]
  for i in range(3):
    ax[i].set_xticks (xticks)
    ax[i].set_xlim(xticks[0], xticks[-1])
    ax[i].legend (loc='best')
    ax[i].grid()
  ax[2].set_xlabel ('Time [s]')
  plt.savefig(f'NantucketRawSteps_{dss_suffix}.png', dpi=300)
  plt.show()

