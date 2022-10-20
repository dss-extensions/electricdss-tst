# Copyright (C) 2021-2022 Battelle Memorial Institute
#
import win32com.client # pip install pywin32
import math
import numpy as np
import matplotlib.pyplot as plt
import os

LOAD_KW = 0.1
LOAD_PF = 0.85
PV_KW = 10.0
INV_KVA = PV_KW * 1.0328 # Category A
INV_KVA = PV_KW * 1.1135 # Category B (in the case_template, kvarMax and kvarMaxAbs are hard-coded for 10 kW Cat B)

case_template = """
clear
new circuit.secondary 
edit vsource.source bus1=pole phases=1 pu=1 basekv=7.2 Isc1=10000 Isc3=10000 x1r1=2 x0r0=2

new wiredata.#2 Runits=kft radunits=in GMRunits=in diam=0.292 GMRac=0.10594 Rac=0.2929 NormAmps=90.0
new linegeometry.#2_triplex_full nconds=3 nphases=2 reduce=yes normamps=90.00
~ cond=1 wire=#2 x=-0.20600 h=240.28543 units=in
~ cond=2 wire=#2 x=0.20600 h=240.28543 units=in
~ cond=3 wire=#2 x=0 h=240.00000 units=in
new xfmrcode.10kva phases=1 windings=3 conns=[w, w, w] kvs=[7.200 0.12 0.12]
~ kvas=[10.0 10.0 10.0] %noloadloss=0.318
~ Xhl=1.08 Xht=1.08 Xlt=0.72 %Rs=[0.58 1.15 1.15]

new transformer.poletop xfmrcode=10kva buses=[pole.1, sec.1.0, sec.0.2]
new line.drop geometry=#2_triplex_full bus1=sec bus2=house units=m length={meters}
new load.house phases=2 bus1=house conn=w kv=0.208 kW={loadkw} pf={loadpf} model=1

New PVSystem.der phases=2 bus1=house conn=w kV=0.208 irradiance=1.0 pmpp={pvkw} kVA={invkva} varfollowinverter=false kvarMax=4.9 kvarMaxAbs=4.9
{exp_comment}New PVSystem.expq phases=2 bus1=house conn=w kV=0.208 irradiance=0.5 pmpp=0.01 kVA={invkva} varfollowinverter=false kvarMax=4.9 kvarMaxAbs=4.9

// 1547-2018 default volt-var settings for category A, with sentinels (Yarray is based on kvarmax/kvarmaxabs, not invkva as in IEEE 1547)
New XYcurve.voltvar1547a npts=4 Yarray=[1.0,1.0,-1.0,-1.0] Xarray=[.5,0.9,1.1,1.5]
// 1547-2018 default volt-var settings for category B, with sentinels (Yarray is based on kvarmax/kvarmaxabs, not invkva as in IEEE 1547)
New XYcurve.voltvar1547b npts=6 Yarray=[1.0,1.0,0,0,-1.0,-1.0] Xarray=[.5,0.92,0.98,1.02,1.08,1.5]
// 1547-2018 default watt-var settings for category B, with sentinels; can only be implemented in Version 8 of OpenDSS, Y in pu of VARMAX
New XYcurve.wattvar1547b npts=8 Yarray=[1.0,1.0,0,0,0,0,1.0,-1.0] Xarray=[-2.0,-1.0,-0.5,-0.2,0.2,0.5,1.0,2.0]
// 1547-2018 default volt-watt settings for category B, with sentinel, not for storage
New XYcurve.voltwatt1547b npts=4 Yarray=[1.0,1.0,0.2,0.2] Xarray=[0.0,1.06,1.10,2.00]
New XYcurve.voltwatt1547bch npts=4 Yarray=[0.0,0.0,1.0,1.0] Xarray=[0.0,1.06,1.10,2.00]
// volt-watt settings to start limiting at 1.03 pu, with sentinel, can't absorb P 
//   note that minimum V1 is 1.05 and maximum V2 is 1.10 per IEEE 1547, so V1=1.03 below is outside the standard
//   OpenDSS will screen for V1 >= 1.00 and V2 <= 1.10
New XYcurve.voltwatt1547pv npts=4 Yarray=[1.0,1.0,0.0,0.0] Xarray=[0.0,1.03,1.06,2.00]

{exp_comment}New InvControl.vw derlist=[pvsystem.der] mode=VOLTWATT voltage_curvex_ref=rated voltwatt_curve=voltwatt1547b deltaP_factor=0.2
{exp_comment}New ExpControl.pv1 pvsystemlist=[expq] deltaQ_factor=0.3 vreg=0.0 slope=22 vregtau=0 vregmax=1.03 preferQ=yes

{vv_vw_comment}New InvControl.vv_vw derlist=[pvsystem.der] combimode=VV_VW voltage_curvex_ref=rated vvc_curve1=voltvar1547b 
{vv_vw_comment}~ voltwatt_curve=voltwatt1547b deltaQ_factor=0.4 deltaP_factor=0.2 RefReactivePower=VARMAX

{vv_comment}New InvControl.vv derlist=[pvsystem.der] mode=VOLTVAR voltage_curvex_ref=rated vvc_curve1=voltvar1547b deltaQ_factor=0.4 RefReactivePower=VARMAX

set tolerance=0.0000001
set controlmode=static
set maxcontroliter=9000

set voltagebases=(12.47, 0.208)
calcvoltagebases
solve
"""

def get_average_magnitude (ary):
  nvals = len(ary) // 2
  sum = 0.0
  for i in range(nvals):
    re = ary[2*i]
    im = ary[2*i+1]
    sum += math.sqrt (re*re + im*im)
  return sum/nvals

def get_pv_power (pv):
  p = 0.0
  q = 0.0
  for i in range(pv.count):
    pv.idx = i+1
    p += pv.kw
    q += pv.kvar
  return p, q

def format_case(meters, loadkw, loadpf, pvkw, invkva, vv_comment='//', vv_vw_comment='//', exp_comment='//'):
  case_str = case_template.format (meters=meters, loadkw=loadkw, loadpf=loadpf, pvkw=pvkw, invkva=invkva, 
                                   exp_comment=exp_comment, vv_comment=vv_comment, vv_vw_comment=vv_vw_comment)
  return case_str

class DSS:
  def __init__(self):
    self.engine = win32com.client.Dispatch("OpenDSSEngine.DSS")
    self.engine.Start("0")
    self.text = self.engine.Text
    self.text.Command = "clear"
    self.circuit = self.engine.ActiveCircuit
    print (self.engine.Version)

if __name__ == '__main__':
  case_str = format_case (meters=250.0, loadkw=LOAD_KW, loadpf=LOAD_PF, pvkw=PV_KW, invkva=INV_KVA)
  fp = open ('case.dss', mode='w')
  print (case_str, file=fp)
  fp.close ()

  cwd = os.getcwd() # the DSS engine may change directories!
  # run the base case
  d = DSS()
  d.text.command = 'cd {:s}'.format(cwd)
  d.text.command = 'redirect case.dss'
# nbus = d.circuit.numbuses
# for i in range (nbus):
#   bus = d.circuit.Buses(i)
#   print (bus.Name, bus.Voltages, bus.Nodes)
  i = d.circuit.SetActiveBus ('house')
  print ('House PU Voltage = {:.4f}'.format (get_average_magnitude (d.circuit.Buses(i).Voltages)/120.0))
  pv = d.circuit.pvsystems
  pv.idx = 1
  print ('PV output = {:.3f} kW + j {:.3f} kVAR'.format (pv.kw, pv.kvar))
  load = d.circuit.loads
  load.idx = 1
  print ('Load = {:.3f} kW + j {:.3f} kVAR'.format (load.kw, load.kvar))

  # now run a loop over length
  mtrs = np.linspace (1.0, 300.0)
  npts = len(mtrs)
  vunreg = np.zeros (npts)
  vvv = np.zeros (npts)
  pvv = np.zeros (npts)
  qvv = np.zeros (npts)
  v14h = np.zeros (npts)
  p14h = np.zeros (npts)
  q14h = np.zeros (npts)
  vavr = np.zeros (npts)
  pavr = np.zeros (npts)
  qavr = np.zeros (npts)
  for i in range(npts):
    case_str = format_case (meters=mtrs[i], loadkw=LOAD_KW, loadpf=LOAD_PF, pvkw=PV_KW, invkva=INV_KVA)
    fp = open ('case.dss', mode='w')
    print (case_str, file=fp)
    fp.close ()
    d.text.command = "redirect case.dss"
    ih = d.circuit.SetActiveBus ('house')
    vunreg[i] = get_average_magnitude (d.circuit.Buses(ih).Voltages)/120.0

  for i in range(npts):
    case_str = format_case (meters=mtrs[i], loadkw=LOAD_KW, loadpf=LOAD_PF, pvkw=PV_KW, invkva=INV_KVA, vv_comment='')
    fp = open ('case.dss', mode='w')
    print (case_str, file=fp)
    fp.close ()
    d.text.command = "redirect case.dss"
    ih = d.circuit.SetActiveBus ('house')
    vvv[i] = get_average_magnitude (d.circuit.Buses(ih).Voltages)/120.0
    pvv[i], qvv[i] = get_pv_power (d.circuit.pvsystems)

    case_str = format_case (meters=mtrs[i], loadkw=LOAD_KW, loadpf=LOAD_PF, pvkw=PV_KW, invkva=INV_KVA, vv_vw_comment='')
    fp = open ('case.dss', mode='w')
    print (case_str, file=fp)
    fp.close ()
    d.text.command = "redirect case.dss"
    ih = d.circuit.SetActiveBus ('house')
    v14h[i] = get_average_magnitude (d.circuit.Buses(ih).Voltages)/120.0
    p14h[i], q14h[i] = get_pv_power (d.circuit.pvsystems)

    case_str = format_case (meters=mtrs[i], loadkw=LOAD_KW, loadpf=LOAD_PF, pvkw=PV_KW, invkva=INV_KVA, exp_comment='')
    fp = open ('case.dss', mode='w')
    print (case_str, file=fp)
    fp.close ()
    d.text.command = "redirect case.dss"
    ih = d.circuit.SetActiveBus ('house')
    vavr[i] = get_average_magnitude (d.circuit.Buses(ih).Voltages)/120.0
    pavr[i], qavr[i] = get_pv_power (d.circuit.pvsystems)

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
  fig.suptitle ('{:.1f}-kW PV Output with {:.1f}-kW Load'.format(PV_KW, LOAD_KW), fontsize=10)

  ax[0].plot (mtrs, vavr, label='AVR', linestyle='-', color='red')
  ax[0].plot (mtrs, v14h, label='14H', linestyle='--', color='green')
  ax[0].plot (mtrs, vvv,  label='VVar', linestyle='-.', color='blue')
  ax[0].plot (mtrs, vunreg, label='pf=1', linestyle=':', color='black')
  ax[0].set_ylabel ('Voltage [pu]')

  ax[1].set_ylabel ('Real Power [kW]')
  ax[1].plot (mtrs, pavr, label='AVR', linestyle='-', color='red')
  ax[1].plot (mtrs, p14h, label='14H', linestyle='--', color='green')
  ax[1].plot (mtrs, pvv, label='VVar', linestyle='-.', color='blue')

  ax[2].set_ylabel ('Reactive Power [kvar]')
  ax[2].plot (mtrs, qavr, label='AVR', linestyle='-', color='red')
  ax[2].plot (mtrs, q14h, label='14H', linestyle='--', color='green')
  ax[2].plot (mtrs, qvv, label='VVar', linestyle='-.', color='blue')

  xticks = [0, 50, 100, 150, 200, 250, 300]
# pticks = [0, 3, 6, 9, 12]
# qticks = [-6, -3, 0]
# vticks = [1.00, 1.02, 1.04, 1.06, 1.08, 1.10]
# ax[0].set_yticks (vticks)
# ax[0].set_ylim(vticks[0], vticks[-1])
# ax[1].set_yticks (pticks)
# ax[1].set_ylim(pticks[0], pticks[-1])
# ax[2].set_yticks (qticks)
# ax[2].set_ylim(qticks[0], qticks[-1])
  for i in range(3):
    ax[i].set_xticks (xticks)
    ax[i].set_xlim(xticks[0], xticks[-1])
    ax[i].legend (loc='best')
    ax[i].grid()
  ax[2].set_xlabel ('Service Drop Length [m]')

# lns1 = ax.plot (mtrs, vavr, label='V: AVR', linestyle='-', color='red')
# lns2 = ax.plot (mtrs, v14h, label='V: 14H', linestyle='-.', color='red')
# lns3 = ax.plot (mtrs, vunreg, label='V: Unreg', linestyle=':', color='black')
# ax.grid()
# ax.set_ylabel ('Voltage [pu]')
# ax.set_xlabel ('Service Drop Length [m]')
#
# ax2 = ax.twinx()
# ax2.set_ylabel ('Power [kVA]')
# lns4 = ax2.plot (mtrs, pvp, label='PV P: AVR', linestyle='-', color='blue')
# lns5 = ax2.plot (mtrs, pvq, label='PV Q: AVR', linestyle='-', color='magenta')
# lns6 = ax2.plot (mtrs, p14h, label='PV P: 14H', linestyle='-.', color='blue')
# lns7 = ax2.plot (mtrs, q14h, label='PV Q: 14H', linestyle='-.', color='magenta')
#
# ax.set_xlim(0, 300)
# ax.set_xticks ([0, 50, 100, 150, 200, 250, 300])
# ax.set_ylim (0.98, 1.1)
# ax.set_yticks ([0.98, 1.00, 1.02, 1.04, 1.06, 1.08, 1.10])
# ax2.set_ylim (-6, 12)
# ax2.set_yticks ([-6, -3, 0, 3, 6, 9, 12])
#
# lns = lns1 + lns2 + lns3 + lns4 + lns5 + lns6 + lns7
# labs = [l.get_label() for l in lns]
# ax.legend (lns, labs, loc='right')

  plt.savefig('Fig5.png', dpi=300)
  plt.show()


    

