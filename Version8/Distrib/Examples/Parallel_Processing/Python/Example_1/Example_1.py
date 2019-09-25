
# coding: utf-8

# In[1]:


import win32com.client
from win32com.client import makepy
import sys
from tkinter import *
import gc
import numpy as np
from IPython.display import clear_output
import time
from os import system, name 
#import tkmessagebox

# Initialize OpenDSS (early binding)
sys.argv = ["makepy", "OpenDSSEngine.DSS"]
makepy.main()
DSSObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
DSSText = DSSObj.Text
DSSCircuit = DSSObj.ActiveCircuit
DSSSolution = DSSCircuit.Solution
DSSParallel = DSSCircuit.Parallel;
DSSBus=DSSCircuit.ActiveBus
DSSCtrlQueue=DSSCircuit.CtrlQueue
DSSObj.Start(0)

DNumActors = 6

DSSText.Command='ClearAll'
DSSText.Command='compile "C:/Temp/13Bus/IEEE13Nodeckt.dss"' 
DSSText.Command='set maxiterations=1000 maxcontroliter=1000' 
DSSSolution.Solve                       # Solves Actor 1
DSSText.Command =   'Clone ' + str(DNumActors - 1)

DSSText.Command =   'set ActiveActor=*'        
DSSText.Command =   'set mode=time controlmode=time number=525000 stepsize=1s hour=0 sec=0 miniterations=1 totalTime=0'
DSSText.Command =   'set ActiveActor=1'
DSSText.Command =   'Set Parallel=Yes'
DSSText.Command =   'SolveAll'


BoolStatus = 0;
while BoolStatus == 0:
    ActorStatus     =   DSSParallel.ActorStatus
    BoolStatus      =   all(Status == 1 for Status in ActorStatus) #Checks if everybody has ended
    ActorProgress   =   DSSParallel.ActorProgress
    system('cls') 
    for i in range(1, DNumActors):
        print('Actor ' + str(i) + ' Progress(' + str(ActorProgress[i-1]) + ') @ CPU ' + str(i - 1))
        
    time.sleep(0.5);  #  A little wait to not saturate the Processor  

print('Simulation finished by all the actors')

