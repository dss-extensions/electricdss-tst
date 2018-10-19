import sys;
import re;
import csv;
import math;

# from opendss line constants calculation
# R1, X1, C1, R0, X0, C0 in ohms/kft or nF/kft
seqParms = {'Trans': [0.00997568, 0.140645, 2.8847, 0.0625438, 0.519912, 1.3964],
    'Pri': [0.0246567, 0.0126968, 107.24, 0.0246536, 0.0126035, 107.24],
    'Sec': [0.0385531, 0.0545944, 8.24795, 0.112396, 0.193039, 2.89204]}
# Z1, V1, Z0, V0 in ohms or %c
waveParms = {'Trans': [359.622, 98.0048, 993.789, 73.2639],
    'Pri': [17.7216, 53.4977, 17.6563, 53.6953],
    'Sec': [132.506, 93.0278, 420.78, 83.5478]}

def ATPBus(root, phs):
    val = root + phs
    return val.ljust(6)

def ATPWinding(bus, conn, seq): # TODO - this always makes the delta lead
    if conn.lower() == 'delta':
        if seq == 1:
            return ATPBus(bus, 'A') + ATPBus(bus, 'C')
        elif seq == 2:
            return ATPBus(bus, 'B') + ATPBus(bus, 'A')
        else:
            return ATPBus(bus, 'C') + ATPBus(bus, 'B')
    else:
        if seq == 1:
            return ATPBus(bus, 'A') + '      '
        elif seq == 2:
            return ATPBus(bus, 'B') + '      '
        else:
            return ATPBus(bus, 'C') + '      '
    

def ATP16ch(val):
    return '{:16.12f}'.format(val)

def ATP6ch(val):
    if val > 9999.9:
        return '{:6.0f}'.format(val)
    if val > 999.99:
        return '{:6.1f}'.format(val)
    if val > 99.999:
        return '{:6.2f}'.format(val)
    if val > 9.9999:
        return '{:6.3f}'.format(val)
    if val > 0.9999:
        return '{:6.4f}'.format(val)
    return '{:6.5f}'.format(val).lstrip('0')
    
def DSSkv(s, conn, phs):
    val = float(s)
    if conn.lower() == 'delta' or int(phs) > 1:
        val *= math.sqrt(3.0)
    return '{:.3f}'.format(0.001 * val)

def DSSConn(s):
    if s.lower() == 'wye':
        return 'w'
    if s.lower() == 'delta':
        return 'd'
    return '***' # don't want anything to fall through

def DSSPhases(s):
    if s== 'ABC':
        return '.1.2.3'
    if s== 'ABCN':
        return '.1.2.3'
    if s== 'AB':
        return '.1.2'
    if s== 'AC':
        return '.1.3'
    if s== 'BC':
        return '.2.3'
    if s== 'BA':
        return '.2.1'
    if s== 'CA':
        return '.3.1'
    if s== 'CB':
        return '.3.2'
    if s== 'A':
        return '.1'
    if s== 'B':
        return '.2'
    if s== 'C':
        return '.3'
    return '***' # don't want anything to fall through

lstLoads = []
with open('Loads.csv', newline='') as csvfile:
    rdr = csv.reader (csvfile, skipinitialspace=True)
    next(rdr)
    next(rdr)
    for row in rdr:
        lstLoads.append(row)
csvfile.close()

lstLines = []
with open('Lines.csv', newline='') as csvfile:
    rdr = csv.reader (csvfile, skipinitialspace=True)
    next(rdr)
    next(rdr)
    for row in rdr:
        lstLines.append(row)
csvfile.close()

lstXfmrs = []
with open('Transformers.csv', newline='') as csvfile:
    rdr = csv.reader (csvfile, skipinitialspace=True)
    next(rdr)
    next(rdr)
    for row in rdr:
        lstXfmrs.append(row)
csvfile.close()

op = open ('SecNet.dss', 'w')
print ('clear', file=op)
print (' ', file=op)
# near-infinite source impedance to match ATP's
print ('new circuit.ieee390 basekv=230 pu=1.05 bus1=P1 mvasc3=200000 mvasc1=2000000', file=op)

print (' ', file=op)
print ('new LineCode.Switch nphases=3 r1=1e-6 r0=1e-6 x1=1e-6 x0=1e-6 c1=0 c0=0', file=op)

print (' ', file=op)
print ('new LineSpacing.101 nconds=3 nphases=3 units=ft x=[0,10,20] h=[50,50,50]', file=op)
print ('new LineSpacing.102 nconds=3 nphases=3 units=in x=[0,3,6] h=[-48,-48,-48]', file=op)
print ('new LineSpacing.103 nconds=4 nphases=3 units=in x=[-2.1213,0,2.1213,0] h=[50.1213,48,50.1213,52.2426]', file=op)

print (' ', file=op)
print ('new WireData.397AA gmr=0.0277 rac=0.0477 diam=0.806 gmrunits=ft radunits=in runits=mi normamps=594', file=op)
print ('new CNData.1000AA gmrac=0.04683 rac=0.1214 diam=1.124 gmrunits=ft runits=mi radunits=in normamps=615', file=op)
print ('~ diacable=2.08 k=21 gmrstrand=0.00417 rstrand=0.1809 diastrand=0.1285', file=op)
print ('~ inslayer=0.25 diains=1.64', file=op)
print ('new WireData.UG500Cu gmr=0.026 rac=0.206 diam=0.814 gmrunits=ft radunits=in runits=mi normamps=430', file=op)

print (' ', file=op)
print ('new LineGeometry.Trans nconds=3 nphases=3 spacing=101 wires=[397AA 397AA 397AA]', file=op)
print ('new LineGeometry.Pri nconds=3 nphases=3 spacing=102 cncables=[1000AA 1000AA 1000AA]', file=op)
print ('new LineGeometry.Sec nconds=4 nphases=3 reduce=y spacing=103 wires=[UG500Cu UG500Cu UG500Cu UG500Cu]', file=op)

# Lines: Name, Bus1, Phases, Bus2, Phases, Length, Units, LineCode, Status ,Lines
print (' ', file=op)
for row in lstLines:
    if row[7] == 'Switch':
        print ('new Line.' + row[0] + ' bus1=' + row[1] + DSSPhases(row[2])
           + ' bus2=' + row[3] + DSSPhases(row[4]) + ' phases=3 switch=yes linecode=switch length=1', file=op)
        if row[8] == 'close':
            print ('  close Line.' + row[0] + ' 1', file=op)
        else:
            print ('  open  Line.' + row[0] + ' 1', file=op)
    else:
        print ('new Line.' + row[0] + ' bus1=' + row[1] + DSSPhases(row[2])
           + ' bus2=' + row[3] + DSSPhases(row[4]) + ' phases=3 length=' + row[5]
           + ' units=' + row[6] + ' geometry=' + row[7], file=op)
        for i in range (1, int(row[9])):
            print ('  new Line.' + row[0] + '_' + str(i+1) + ' bus1=' + row[1] + DSSPhases(row[2])
           + ' bus2=' + row[3] + DSSPhases(row[4]) + ' phases=3 length=' + row[5]
           + ' units=' + row[6] + ' geometry=' + row[7], file=op)
# Loads: Name, NumPhases, Bus, phases, Voltage, status, model, connection, kW, PF
print (' ', file=op)
for row in lstLoads:
    print ('new Load.' + row[0] + ' phases=' + row[1] + ' bus1=' + row[2] + DSSPhases(row[3])
           + ' conn=' + DSSConn(row[7]) + ' kv=' + DSSkv(row[4], row[7], row[1]) 
           + ' kw=' + row[8] + ' pf=' + row[9], file=op)
# HV/MV Substation connected Delta/grounded-wye,,,,,,,,,,
# Name, phases, bus1, bus2, V_pri, V_sec, kVA, Conn_pri, Conn_sec, %XHL, %RHL
print (' ', file=op)
for row in lstXfmrs:
    print ('new Transformer.' + row[0] + ' buses=[' + row[2] + ',' + row[3] + ']'
           + ' kvs=[' + DSSkv(row[4], row[7], 3) + ',' + DSSkv(row[5], row[8], 3) + ']'
           + ' kvas=[' + row[6] + ',' + row[6] + '] conns=[' + DSSConn(row[7]) + ',' + DSSConn(row[8]) + ']'
           + ' xhl=' + row[9] + ' %loadloss=' + row[10], file=op)


print (' ', file=op)
print ('Set Voltagebases=[230, 13.8, 0.48, 0.208]', file=op)
print ('calcv', file=op)
op.close()

# ATP output
#print(seqParms)
#print(waveParms)

op = open ('SecNet.atp', 'w')

print ('BEGIN NEW DATA CASE', file=op)
print ('C  dT  >< Tmax >< Xopt >< Copt ><Epsiln>', file=op)
print ('  50.E-6    .050     60.', file=op)                
print ('   99999       1       1       1       1       0       0       1       0', file=op)
print ('C        1         2         3         4         5         6         7         8', file=op)
print ('C 345678901234567890123456789012345678901234567890123456789012345678901234567890', file=op)

print ('/BRANCH', file=op)
print ('C < n1 >< n2 ><ref1><ref2>< R  >< L  >< C  >', file=op)
print ('C < n1 >< n2 ><ref1><ref2>< R  >< A  >< B  ><Leng><><>0', file=op)

print ('C ', file=op)
print ('C transformers follow', file=op)
print ('C ', file=op)
xnum = 1
for row in lstXfmrs: # we know these are all three-phase
    xnum += 1
    kv1 = 0.001 * float(row[4])
    if row[7].lower() == 'delta':
        kv1 *= math.sqrt(3.0)
    kv2 = 0.001 * float(row[5])
    if row[8].lower() == 'delta':
        kv2 *= math.sqrt(3.0)
    mva = 0.001 * float(row[6]) / 3.0 # per phase
    zbase1 = kv1 * kv1 / mva
    zbase2 = kv2 * kv2 / mva
    r1 = 0.01 * 0.5 * float(row[10]) * zbase1
    x1 = 0.01 * 0.5 * float(row[9]) * zbase1
    r2 = 0.01 * 0.5 * float(row[10]) * zbase2
    x2 = 0.01 * 0.5 * float(row[9]) * zbase2
    print ('  TRANSFORMER                         ' + ATPBus ('XF' + str(xnum), 'A') + '  1.E6', file=op)
    print ('            9999', file=op)
    print (' 1' + ATPWinding (row[2], row[7], 1) + '            ' + ATP6ch (r1) + ATP6ch (x1) + ATP6ch (kv1), file=op)
    print (' 2' + ATPWinding (row[3], row[8], 1) + '            ' + ATP6ch (r2) + ATP6ch (x2) + ATP6ch (kv2), file=op)
    print ('  TRANSFORMER ' + ATPBus ('XF' + str(xnum), 'A') + '                  ' + ATPBus ('XF' + str(xnum), 'B'), file=op)
    print (' 1' + ATPWinding (row[2], row[7], 2), file=op)
    print (' 2' + ATPWinding (row[3], row[8], 2), file=op)
    print ('  TRANSFORMER ' + ATPBus ('XF' + str(xnum), 'A') + '                  ' + ATPBus ('XF' + str(xnum), 'C'), file=op)
    print (' 1' + ATPWinding (row[2], row[7], 3), file=op)
    print (' 2' + ATPWinding (row[3], row[8], 3), file=op)

print ('C ', file=op)
print ('C fixed-impedance loads follow', file=op)
print ('C ', file=op)
for row in lstLoads:
    pf = float(row[9]) # fixed series impedance calculation, knowing they are all single-phase
    v = float(row[4])
    va = 1000.0 * float(row[8]) / pf
    z = v * v / va
    r = pf * z
    x = math.sqrt (z * z - r * r)
    if row[7].lower() == 'delta':
        r *= 3.0
        x *= 3.0
        bus1 = ATPBus (row[2], row[3][0])
        bus2 = ATPBus (row[2], row[3][1])
    else:
        bus1 = ATPBus (row[2], row[3])
        bus2 = '      '
    print ('  ' + bus1 + bus2 + '            ' + ATP6ch (r) + ATP6ch (x)
        + '                                         0', file=op)

print ('C ', file=op)
print ('C transmission, primary and secondary lines follow', file=op)
print ('C ', file=op)

print ('$VINTAGE,1', file=op)
for row in lstLines:
    if row[7] != 'Switch': # we know they are all three-phase and transposed
        key = row[7]
        bus1 = row[1]
        bus2 = row[3]
        npar = float(row[9])
        len = float(row[5]) # feet
        seq = seqParms[key] # ohm/kft and nF/kft
        r1 = seq[0] * len * 0.001 / npar
        x1 = seq[1] * len * 0.001 / npar
        c1 = seq[2] * len * 0.000001 * npar
        r0 = seq[3] * len * 0.001 / npar
        x0 = seq[4] * len * 0.001 / npar
        c0 = seq[5] * len * 0.000001 * npar
        rs = (r0 + 2.0 * r1) / 3.0
        rm = (r0 - r1) / 3.0
        xs = (x0 + 2.0 * x1) / 3.0
        xm = (x0 - x1) / 3.0
        cs = (c0 + 2.0 * c1) / 3.0
        cm = (c0 - c1) / 3.0
#        print (key, npar, len, r1, x1, c1, r0, x0, c0)
        print('1 ' + ATPBus(bus1, 'A') + ATPBus(bus2, 'A') + '            ' + ATP16ch(rs) + ATP16ch(xs) + ATP16ch(cs), file=op)
        print('2 ' + ATPBus(bus1, 'B') + ATPBus(bus2, 'B') + '            ' + ATP16ch(rm) + ATP16ch(xm) + ATP16ch(cm), file=op)
        print('  ' + '            '                        + '            ' + ATP16ch(rs) + ATP16ch(xs) + ATP16ch(cs), file=op)
        print('3 ' + ATPBus(bus1, 'C') + ATPBus(bus2, 'C') + '            ' + ATP16ch(rm) + ATP16ch(xm) + ATP16ch(cm), file=op)
        print('  ' + '            '                        + '            ' + ATP16ch(rm) + ATP16ch(xm) + ATP16ch(cm), file=op)
        print('  ' + '            '                        + '            ' + ATP16ch(rs) + ATP16ch(xs) + ATP16ch(cs), file=op)
print ('$VINTAGE,0', file=op)

print ('/SWITCH', file=op)
print ('C < n 1>< n 2>< Tclose ><Top/Tde ><   Ie   ><Vf/CLOP ><  type  >', file=op)
for row in lstLines:
    if row[7] == 'Switch': # we know they are all three-phase
        if row[8] == 'close':
            print ('  ' + ATPBus (row[1], 'A') + ATPBus (row[3], 'A') 
                + '      -1.0     100.0                                             0', file=op)
            print ('  ' + ATPBus (row[1], 'B') + ATPBus (row[3], 'B') 
                + '      -1.0     100.0                                             0', file=op)
            print ('  ' + ATPBus (row[1], 'C') + ATPBus (row[3], 'C') 
                + '      -1.0     100.0                                             0', file=op)
        else:
            print ('  ' + ATPBus (row[1], 'A') + ATPBus (row[3], 'A') 
                + '      -1.0     100.0                                             0', file=op)
            print ('  ' + ATPBus (row[1], 'B') + ATPBus (row[3], 'B') 
                + '      -1.0     100.0                                             0', file=op)
            print ('  ' + ATPBus (row[1], 'C') + ATPBus (row[3], 'C') 
                + '      -1.0     100.0                                             0', file=op)

print ('/SOURCE', file=op)
print ('C < n 1><>< Ampl.  >< Freq.  ><Phase/T0><   A1   ><   T1   >< TSTART >< TSTOP  >', file=op)
print ('14P1A     197183.924       60.        0.                           -1.      100.', file=op)
print ('14P1B     197183.924       60.     -120.                           -1.      100.', file=op)
print ('14P1C     197183.924       60.     -240.                           -1.      100.', file=op)

print ('C ', file=op)
print ('C this area for faults and other manual edits', file=op)
print ('C ', file=op)
print ('/BRANCH', file=op)
print ('C < n1 >< n2 ><ref1><ref2>< R  >< L  >< C  >', file=op)
print ('  S47A  FAULTA             0.001', file=op)
print ('  S47B  FAULTB             0.001', file=op)
print ('  S47C  FAULTC             0.001', file=op)
print ('/SWITCH', file=op)
print ('C < n 1>< n 2>< Tclose ><Top/Tde ><   Ie   ><Vf/CLOP ><  type  >', file=op)
print ('  FAULTA            10.0     100.0                                             1', file=op)
print ('  FAULTB            10.0     100.0                                             1', file=op)
print ('  FAULTC            10.0     100.0                                             1', file=op)

print ('/OUTPUT', file=op)
print ('  P82A  P82B  P82C  S47A  S47B  S47C  P1A   P1B   P1C', file=op)
print ('BLANK BRANCH', file=op)
print ('BLANK SWITCH', file=op)
print ('BLANK SOURCE', file=op)
print ('BLANK OUTPUT', file=op)
print ('BLANK PLOT', file=op)
print ('BEGIN NEW DATA CASE', file=op)
print ('BLANK', file=op)

op.close()

