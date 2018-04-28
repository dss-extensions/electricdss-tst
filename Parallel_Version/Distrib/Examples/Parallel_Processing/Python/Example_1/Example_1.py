
# coding: utf-8

# In[ ]:


import win32com.client
from win32com.client import makepy
import sys
import gc
import numpy as np
import time

# Initialize OpenDSS (early binding)
sys.argv = ["makepy", "OpenDSSEngine.DSS"]
makepy.main()
DSSObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
DSSText = DSSObj.Text
DSSCircuit = DSSObj.ActiveCircuit
DSSSolution = DSSCircuit.Solution
DSSParallel = DSSCircuit.Parallel
DSSBus=DSSCircuit.ActiveBus
DSSCtrlQueue=DSSCircuit.CtrlQueue
DSSObj.Start(0)
#Requests the number of CPUs to create actors
NCPUs=DSSParallel.NumCPUs
DSSText.Command='ClearAll'
DSSText.Command='set parallel=No'
EndArray=[] # for checking when all the actors are done
for x in range(0, (NCPUs-1)):
    if x != 0:
        DSSParallel.CreateActor
    DSSText.Command='compile "C:\Program Files\OpenDSS\EPRITestCircuits\ckt24\master_ckt24.dss"'
    DSSSolution.Solve
    DSSText.Command='set mode=yearly number=2000'
    EndArray.append(1)
    
DSSText.Command='set parallel=Yes'
DSSSolution.SolveAll
BoolStatus      =   False;
while BoolStatus == False:
    ActorStatus     =   DSSParallel.ActorStatus;
    BoolStatus      =   ActorStatus == EndArray; #Checks if everybody has ended
    # Prints the current time on each simulation
    for i in range(1,(NCPUs-1)):
        DSSParallel.ActiveActor = i;
        CHour   =   DSSSolution.dblHour;
        print('Actor Time(hours)',CHour);
    end;
    time.sleep(0.5);  #  A little wait to not saturate the Processor  
end;

