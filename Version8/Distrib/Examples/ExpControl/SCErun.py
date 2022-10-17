# Copyright (C) 2021-2022 Battelle Memorial Institute
#
# Simulates the secondary system example from 2023 PES GM submittal
#  invoke 'python SCErun.py no' to simulate without ExpControl
#  invoke 'python SCErun.py yes' to simulate with ExpControl

import win32com.client # pip install pywin32
import math
import numpy as np
import h5py
import sys
import os

prefix_template = """Clear
// from "Evaluation of the Effectiveness and Robustness of Residential-Scale Smart Photovoltaics"
// J. Schoene, M. Humayun, B. Poudel, V. Zheglov, A. Gebeyehu
New Circuit.Primary basekv=12.0 pu=1.00 r1=0 x1=0.001 r0=0 x0=0.001

// Definitions /////////////////////////////////////////////////////////////////////////////

New Loadshape.Vshape npts=1441 interval=0 hour=(file=Vshape_dss.csv)
New Loadshape.Cloud npts=86401 sinterval=1 csvfile=pcloud.csv action=normalize
New Loadshape.Clear npts=86401 sinterval=1 csvfile=pclear.csv action=normalize

// SCE used underground aluminum 350, 4/0, #4 and #2
New Linecode.750_Triplex  nphases=2 units=kft    ! ohms per 1000 ft
~ rmatrix=[  0.04974733   0.02342157 |  0.02342157   0.04974733 ]
~ xmatrix=[  0.02782436   0.00669472 |  0.00669472   0.02782436 ]
~ cmatrix=[  3.00000000  -2.40000000 | -2.40000000   3.00000000 ]
~ NormAmps=580 {580 1.25 *}  
New Linecode.4/0Triplex nphases=2 units=kft      !ohms per 1000 ft
~ rmatrix=[  0.40995115   0.11809509 |  0.11809509   0.40995115 ]
~ xmatrix=[  0.16681819   0.12759250 |  0.12759250   0.16681819 ]
~ cmatrix=[  3.00000000  -2.40000000 | -2.40000000   3.00000000 ]
~ Normamps=156  {156 1.25 *}

New XfmrCode.CT50  phases=1 windings=3 kvs=[6.9282 0.12 0.12] kVAs=[50.0 50.0 50.0] 
~ %imag=0.5 %Rs=[0.6 1.2 1.2] %noloadloss=.2 Xhl=2.04  Xht=2.04  Xlt=1.36

New LineCode.lat nphases=1 units=mi cmatrix=[0] rmatrix=[1.25953333] xmatrix=[1.66250000]
~ normamps=400 emergamps=600

// time-varying grid voltage to supply the primary //////////////////////////////////////////

New Vsource.Vth1 bus1=thev basekv=12.0 R1=0 X1=0.001 R0=0 X0=0.001 // daily=Vshape
new line.prim bus1=thev bus2=prim switch=yes

New Line.Tap linecode=lat bus1=Prim.1 bus2=Pole1Prim.1 units=ft  length=250

// PV system state variables: 1=irradiance
// 2 = panel kW, 3 = Power temperature factor, 4 = efficiency,
// 5 = Vreg from the parent ExpControl or InvControl

// lateral and secondaries follow //////////////////////////////////////////////////////////
"""

prim_template = """New Line.{tonode} linecode=lat bus1={fromnode}.1 bus2={tonode}.1 units=ft  length=950"""

polesec_template = """
New Transformer.{root}Service  XfmrCode=CT50  buses=[{root}Prim.1 {root}Sec.1.0 {root}Sec.0.2]

New Line.{root}Xsec1 Bus1={root}Sec.1.2   Bus2={root}Xsec1.1.2 linecode=750_Triplex length=190 units=ft 
New Line.{root}Xsec2 Bus1={root}Sec.1.2   Bus2={root}Xsec2.1.2 linecode=750_Triplex length= 55 units=ft 
New Line.{root}Xsec3 Bus1={root}Xsec2.1.2 Bus2={root}Xsec3.1.2 linecode=750_Triplex length=120 units=ft 
New Line.{root}Xsec4 Bus1={root}Xsec3.1.2 Bus2={root}Xsec4.1.2 linecode=750_Triplex length= 95 units=ft

New Line.{root}Drop01 Bus1={root}Sec.1.2    Bus2={root}Load01.1.2 linecode=4/0Triplex length= 80 units=ft 
New Line.{root}Drop02 Bus1={root}Sec.1.2    Bus2={root}Load02.1.2 linecode=4/0Triplex length=140 units=ft 
New Line.{root}Drop03 Bus1={root}XSec1.1.2  Bus2={root}Load03.1.2 linecode=4/0Triplex length= 80 units=ft 
New Line.{root}Drop04 Bus1={root}XSec1.1.2  Bus2={root}Load04.1.2 linecode=4/0Triplex length= 80 units=ft 
New Line.{root}Drop05 Bus1={root}XSec1.1.2  Bus2={root}Load05.1.2 linecode=4/0Triplex length=150 units=ft 
New Line.{root}Drop06 Bus1={root}XSec1.1.2  Bus2={root}Load06.1.2 linecode=4/0Triplex length=200 units=ft 
New Line.{root}Drop07 Bus1={root}XSec1.1.2  Bus2={root}Load07.1.2 linecode=4/0Triplex length=200 units=ft 
New Line.{root}Drop08 Bus1={root}XSec2.1.2  Bus2={root}Load08.1.2 linecode=4/0Triplex length=140 units=ft 
New Line.{root}Drop09 Bus1={root}XSec2.1.2  Bus2={root}Load09.1.2 linecode=4/0Triplex length=140 units=ft 
New Line.{root}Drop10 Bus1={root}XSec2.1.2  Bus2={root}Load10.1.2 linecode=4/0Triplex length= 80 units=ft 
New Line.{root}Drop11 Bus1={root}XSec3.1.2  Bus2={root}Load11.1.2 linecode=4/0Triplex length=160 units=ft 
New Line.{root}Drop12 Bus1={root}XSec3.1.2  Bus2={root}Load12.1.2 linecode=4/0Triplex length=160 units=ft 
New Line.{root}Drop13 Bus1={root}XSec3.1.2  Bus2={root}Load13.1.2 linecode=4/0Triplex length=140 units=ft 
New Line.{root}Drop14 Bus1={root}XSec3.1.2  Bus2={root}Load14.1.2 linecode=4/0Triplex length=100 units=ft 
New Line.{root}Drop15 Bus1={root}XSec4.1.2  Bus2={root}Load15.1.2 linecode=4/0Triplex length= 80 units=ft 
New Line.{root}Drop16 Bus1={root}XSec4.1.2  Bus2={root}Load16.1.2 linecode=4/0Triplex length= 80 units=ft 
New Line.{root}Drop17 Bus1={root}XSec4.1.2  Bus2={root}Load17.1.2 linecode=4/0Triplex length=140 units=ft 
New Line.{root}Drop18 Bus1={root}XSec4.1.2  Bus2={root}Load18.1.2 linecode=4/0Triplex length=140 units=ft

New Load.{root}01 phases=2 Bus1={root}Load01.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}02 phases=2 Bus1={root}Load02.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}03 phases=2 Bus1={root}Load03.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}04 phases=2 Bus1={root}Load04.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}05 phases=2 Bus1={root}Load05.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}06 phases=2 Bus1={root}Load06.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}07 phases=2 Bus1={root}Load07.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}08 phases=2 Bus1={root}Load08.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}09 phases=2 Bus1={root}Load09.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}10 phases=2 Bus1={root}Load10.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}11 phases=2 Bus1={root}Load11.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}12 phases=2 Bus1={root}Load12.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}13 phases=2 Bus1={root}Load13.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}14 phases=2 Bus1={root}Load14.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}15 phases=2 Bus1={root}Load15.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}16 phases=2 Bus1={root}Load16.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}17 phases=2 Bus1={root}Load17.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95
New Load.{root}18 phases=2 Bus1={root}Load18.1.2 kv=0.208 conn=wye kva={loadkva} pf=0.95

New PVsystem.{root}01 phases=2 Bus1={root}Load01.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}02 phases=2 Bus1={root}Load02.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}03 phases=2 Bus1={root}Load03.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}04 phases=2 Bus1={root}Load04.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}05 phases=2 Bus1={root}Load05.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}06 phases=2 Bus1={root}Load06.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}07 phases=2 Bus1={root}Load07.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}08 phases=2 Bus1={root}Load08.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}09 phases=2 Bus1={root}Load09.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}10 phases=2 Bus1={root}Load10.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}11 phases=2 Bus1={root}Load11.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}12 phases=2 Bus1={root}Load12.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}13 phases=2 Bus1={root}Load13.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}14 phases=2 Bus1={root}Load14.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}15 phases=2 Bus1={root}Load15.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}16 phases=2 Bus1={root}Load16.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}17 phases=2 Bus1={root}Load17.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263
New PVsystem.{root}18 phases=2 Bus1={root}Load18.1.2 kV=0.208 conn=wye pmpp=5.0 kva=5.263

new monitor.{root}xfv element=Transformer.{root}Service terminal=2 mode=96
new monitor.{root}xfq element=Transformer.{root}Service terminal=1 mode=65 PPolar=NO
new monitor.{root}pv01st element=PVSystem.{root}01 terminal=1 mode=3
new monitor.{root}pv02st element=PVSystem.{root}02 terminal=1 mode=3
new monitor.{root}pv03st element=PVSystem.{root}03 terminal=1 mode=3
new monitor.{root}pv04st element=PVSystem.{root}04 terminal=1 mode=3
new monitor.{root}pv05st element=PVSystem.{root}05 terminal=1 mode=3
new monitor.{root}pv06st element=PVSystem.{root}06 terminal=1 mode=3
new monitor.{root}pv07st element=PVSystem.{root}07 terminal=1 mode=3
new monitor.{root}pv08st element=PVSystem.{root}08 terminal=1 mode=3
new monitor.{root}pv09st element=PVSystem.{root}09 terminal=1 mode=3
new monitor.{root}pv10st element=PVSystem.{root}10 terminal=1 mode=3
new monitor.{root}pv11st element=PVSystem.{root}11 terminal=1 mode=3
new monitor.{root}pv12st element=PVSystem.{root}12 terminal=1 mode=3
new monitor.{root}pv13st element=PVSystem.{root}13 terminal=1 mode=3
new monitor.{root}pv14st element=PVSystem.{root}14 terminal=1 mode=3
new monitor.{root}pv15st element=PVSystem.{root}15 terminal=1 mode=3
new monitor.{root}pv16st element=PVSystem.{root}16 terminal=1 mode=3
new monitor.{root}pv17st element=PVSystem.{root}17 terminal=1 mode=3
new monitor.{root}pv18st element=PVSystem.{root}18 terminal=1 mode=3
new monitor.{root}pv01pq element=PVSystem.{root}01 terminal=1 mode=65 PPolar=no
new monitor.{root}pv02pq element=PVSystem.{root}02 terminal=1 mode=65 PPolar=no
new monitor.{root}pv03pq element=PVSystem.{root}03 terminal=1 mode=65 PPolar=no
new monitor.{root}pv04pq element=PVSystem.{root}04 terminal=1 mode=65 PPolar=no
new monitor.{root}pv05pq element=PVSystem.{root}05 terminal=1 mode=65 PPolar=no
new monitor.{root}pv06pq element=PVSystem.{root}06 terminal=1 mode=65 PPolar=no
new monitor.{root}pv07pq element=PVSystem.{root}07 terminal=1 mode=65 PPolar=no
new monitor.{root}pv08pq element=PVSystem.{root}08 terminal=1 mode=65 PPolar=no
new monitor.{root}pv09pq element=PVSystem.{root}09 terminal=1 mode=65 PPolar=no
new monitor.{root}pv10pq element=PVSystem.{root}10 terminal=1 mode=65 PPolar=no
new monitor.{root}pv11pq element=PVSystem.{root}11 terminal=1 mode=65 PPolar=no
new monitor.{root}pv12pq element=PVSystem.{root}12 terminal=1 mode=65 PPolar=no
new monitor.{root}pv13pq element=PVSystem.{root}13 terminal=1 mode=65 PPolar=no
new monitor.{root}pv14pq element=PVSystem.{root}14 terminal=1 mode=65 PPolar=no
new monitor.{root}pv15pq element=PVSystem.{root}15 terminal=1 mode=65 PPolar=no
new monitor.{root}pv16pq element=PVSystem.{root}16 terminal=1 mode=65 PPolar=no
new monitor.{root}pv17pq element=PVSystem.{root}17 terminal=1 mode=65 PPolar=no
new monitor.{root}pv18pq element=PVSystem.{root}18 terminal=1 mode=65 PPolar=no
new monitor.{root}pv01pvv element=PVSystem.{root}01 terminal=1 mode=96
new monitor.{root}pv02pvv element=PVSystem.{root}02 terminal=1 mode=96
new monitor.{root}pv03pvv element=PVSystem.{root}03 terminal=1 mode=96
new monitor.{root}pv04pvv element=PVSystem.{root}04 terminal=1 mode=96
new monitor.{root}pv05pvv element=PVSystem.{root}05 terminal=1 mode=96
new monitor.{root}pv06pvv element=PVSystem.{root}06 terminal=1 mode=96
new monitor.{root}pv07pvv element=PVSystem.{root}07 terminal=1 mode=96
new monitor.{root}pv08pvv element=PVSystem.{root}08 terminal=1 mode=96
new monitor.{root}pv09pvv element=PVSystem.{root}09 terminal=1 mode=96
new monitor.{root}pv10pvv element=PVSystem.{root}10 terminal=1 mode=96
new monitor.{root}pv11pvv element=PVSystem.{root}11 terminal=1 mode=96
new monitor.{root}pv12pvv element=PVSystem.{root}12 terminal=1 mode=96
new monitor.{root}pv13pvv element=PVSystem.{root}13 terminal=1 mode=96
new monitor.{root}pv14pvv element=PVSystem.{root}14 terminal=1 mode=96
new monitor.{root}pv15pvv element=PVSystem.{root}15 terminal=1 mode=96
new monitor.{root}pv16pvv element=PVSystem.{root}16 terminal=1 mode=96
new monitor.{root}pv17pvv element=PVSystem.{root}17 terminal=1 mode=96
new monitor.{root}pv18pvv element=PVSystem.{root}18 terminal=1 mode=96

"""

suffix_template = """
batchedit PVSystem..* irradiance=1 daily=Cloud %cutin=0.1 %cutout=0.1 varfollowinverter=true kvarmax=1.643
New ExpControl.pv1 deltaQ_factor=0.3 vreg=1.0 slope=22 vregtau=300 Tresponse=5 enabled={expon}
set loadmult=0.001

New Energymeter.tap Element=Line.prim Terminal=1

set controlmode=static
set maxcontroliter=1000
Set Maxiterations=30

Set voltagebases=[12.0, 0.208] 
Calcvoltagebases

//Solve
solve mode=daily number=86400 stepsize=1s // 86400
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
  EXPON = 'no'
  if len(sys.argv) > 1:
    EXPON = sys.argv[1]
  fp = open ('case_sce.dss', mode='w')
  print ('writing case_sce.dss with EXPON=', EXPON)
  print (prefix_template, file=fp)
  for i in range(9):
      fromnode = 'Pole{:d}Prim'.format(i+1)
      tonode = 'Pole{:d}Prim'.format(i+2)
      print (prim_template.format (fromnode=fromnode, tonode=tonode), file=fp)
  for i in range(10):
      root = 'Pole{:d}'.format(i+1)
      print (polesec_template.format (root=root, loadkva=3.32), file=fp)
  print (suffix_template.format(expon=EXPON), file=fp)
  fp.close ()

  # run the base case
  cwd = os.getcwd() # the DSS engine may change directories!
  d = DSS()
  d.text.command = 'cd {:s}'.format (cwd)
  d.text.command = 'redirect case_sce.dss'
  mon = d.circuit.monitors
  vreg = {}   # st, channel 5
  volts = {}  # want xfv and pvv
  xfp = {}
  xfq = {}
  pvp = {}
  pvq = {}
  npts = 0
  more = mon.first
  while more > 0:
    key = mon.Name
    npts = mon.SampleCount
#    if 'xfv' in key:
#      volts[key] = np.array (mon.Channel(1))
    if 'xfq' in key:
      xfp[key] = np.array (mon.Channel(1))
      xfq[key] = np.array (mon.Channel(2))
    elif 'st' in key:
      vreg[key] = np.array (mon.Channel(5))
    elif 'pq' in key:
      pvp[key] = np.array (mon.Channel(1))
      pvq[key] = np.array (mon.Channel(2))
    elif 'v' in key:
      volts[key] = np.array (mon.Channel(1)) / 120.0
    more = mon.next

  hrs = np.linspace (0.0, float(npts), num=npts, endpoint=False) / 3600.0

  print ('Found {:d} monitors with {:d} voltages, {:d} xfP, {:d} xfQ, {:d} pvQ, {:d} pvQ, {:d} Vreg'.format (mon.count,
    len(volts), len(xfp), len(xfq), len(pvp), len(pvq), len(vreg)))

  f = h5py.File ('sce_{:s}.hdf5'.format(EXPON), mode='w')
  grp = f.create_group ('hrs')
  grp.create_dataset ('hrs', data=hrs, compression='gzip')
  groups = {'volts':volts, 'vreg':vreg, 'xfp': xfp, 'xfq': xfq, 'pvp': pvp, 'pvq': pvq}
  for groupname, channels in groups.items():
    grp = f.create_group (groupname)
    for key, val in channels.items():
      if val is not None:
        grp.create_dataset (key, data=val, compression='gzip')
  f.close()

