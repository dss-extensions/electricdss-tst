
# coding: utf-8

# In[1]:


#import win32com.client
#from win32com.client import makepy
import sys
import gc
import numpy as np
import time
from os import system, name 

#sys.argv = ["makepy", "OpenDSSEngine.DSS"]
#makepy.main()
#DSSObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
from dss import dss as DSSObj
DSSText = DSSObj.Text
DSSCircuit = DSSObj.ActiveCircuit
DSSSolution = DSSCircuit.Solution
DSSParallel = DSSCircuit.Parallel
DSSBus=DSSCircuit.ActiveBus
DSSCtrlQueue=DSSCircuit.CtrlQueue
DSSObj.Start(0)
NCPUs=DSSParallel.NumCPUs
print(' total number of NCPUs', NCPUs )

DSSText.Command='ClearAll'
DSSText.Command='set parallel=No'

EndArray=[] # for checking when all the actors are done
yDelta=8760/(NCPUs-1)
ActorCPU =[]

for x in range(0, (NCPUs-1)):
    print('Core Number',x)
    if x != 0:
        DSSParallel.CreateActor()
    DSSText.Command='redirect ../../../../EPRITestCircuits/ckt5/Master_ckt5.dss'
    DSSText.Command='Solve'
    if x==NCPUs-1:
        yDelta=8760-(NCPUs-2)*yDelta
    DSSText.Command='set mode=yearly totaltime=0 number=' + str(yDelta) + ' hour=' + str(x*yDelta)
    EndArray.append(1)
            
DSSText.Command='set parallel=Yes'
DSSText.Command='SolveAll'
BoolStatus = False
time.sleep(1);
while BoolStatus == False:
    ActorStatus = list(DSSParallel.ActorStatus);
    BoolStatus = ActorStatus == EndArray
    ActorProgress=DSSParallel.ActorProgress
#    system('cls') 
    print('BoolStatus = ',BoolStatus,' ActorStatus = ',ActorStatus,' ActorProgress = ', ActorProgress)
    for i in range(1,(NCPUs-1)):
        DSSParallel.ActiveActor = i;
        CHour = DSSSolution.dblHour;
        print('Actor Time(hours)',CHour);
    time.sleep(0.5)
    
print('Simulation finished');

