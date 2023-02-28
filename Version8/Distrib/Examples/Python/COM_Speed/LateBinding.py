
# coding: utf-8

# In[1]:


import win32com.client
from time import process_time

#import tkmessagebox

# Initialize OpenDSS (late binding)
DSSObj = win32com.client.dynamic.Dispatch("OpenDSSEngine.DSS")
DSSText = DSSObj.Text
DSSCircuit = DSSObj.ActiveCircuit
DSSSolution = DSSCircuit.Solution
DSSParallel = DSSCircuit.Parallel;
DSSBus=DSSCircuit.ActiveBus
DSSCtrlQueue=DSSCircuit.CtrlQueue
DSSObj.Start(0)

DNumActors = 6
print('Simulation started')
DSSText.Command='ClearAll'
DSSText.Command='compile "C:/Program Files/OpenDSS/IEEETestCases/8500-Node/master.dss"' 
DSSText.Command='set maxiterations=1000 maxcontroliter=1000' 
DSSSolution.Solve                       # Solves Actor 1
tic = process_time()  # Gets the initial time
for i in range(0,1000):
    j = DSSCircuit.Loads.First
    while j > 0:
        DSSCircuit.Loads.kW = 50
        DSSCircuit.Loads.kvar = 20
        j = DSSCircuit.Loads.Next

toc = process_time() # Gets the final time
# Publish results
print('Total time required (s): ')
print(toc-tic)

