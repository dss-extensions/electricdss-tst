'''
2019-02-28: Ported from CtrlQueueTest.bas by Paulo Meira (@pmeira)
'''
USE_COM = False # Change to True to test with the COM DLL

if not USE_COM:
    from dss import DSS as DSSobj
else:
    import os
    old_cd = os.getcwd()
    import win32com.client
    DSSobj = win32com.client.gencache.EnsureDispatch('OpenDSSengine.DSS')
    os.chdir(old_cd)

DSSText = DSSobj.Text
DSSCircuit = DSSobj.ActiveCircuit
DSSSolution = DSSCircuit.Solution
DSSControlQueue = DSSCircuit.CtrlQueue
DSSCktElement = DSSCircuit.ActiveCktElement
DSSPDElement = DSSCircuit.PDElements
DSSMeters = DSSCircuit.Meters
DSSBus = DSSCircuit.ActiveBus
DSSCmath = DSSobj.CmathLib
DSSParser = DSSobj.Parser
DSSIsources = DSSCircuit.ISources
DSSMonitors = DSSCircuit.Monitors
DSSCapacitors = DSSCircuit.Capacitors

def TestCtrlQueue():
    '''Example of implementing a simple voltage control for Capacitors via the COM interface'''

    # Run simple capacitor interface test and execute local cap control that emulates CapControl
    # with these settings:
    # PT=125.09 Type=voltage onsetting=118.8 offsetting=121.2
    
    # this test case has a four-step capacitor bank named "cap" and can be found in the Test Folder
    
    DSSText.Command = r"Compile Master_TestCapInterface.DSS"
    
    # Set all capacitor steps open for first capacitor
    iStates = [0] * 10
    iCap = DSSCapacitors.First   # should check iCap for >0
    
    for i in range(DSSCapacitors.NumSteps):
        iStates[i] = 0
    
    DSSCapacitors.States = iStates  # push over the interface to OpenDSS

    # check to make sure it worked
    DSSText.Command = "? Capacitor.Cap.States"
    strValue = "Starting Capacitor Step States=" + DSSText.Result  # should be [0 0 0 0]
    print(strValue)
    
    # Base solution
    DSSSolution.Solve()
    
    # Each message we push onto the queue will get a 5 s delay
    hour = 0
    secDelay = 5  # delay
    
    PTratio = 125.09   # for 26 kV system
    ONsetting = 118.8
    OFFsetting = 121.2
    ActionCodeAdd = 201  # just an arbitrary action code
    ActionCodeSub = 202  # just another arbitrary action code
    DeviceHandle = 123  # arbitrary handle that signifies this control
    
    # now, we'll crank the load up in 10% steps, checking the voltage at each step
    # until all cap steps are on (no more available)
    
    i = 0
    while DSSCapacitors.AvailableSteps > 0:
        print('DSSCapacitors.AvailableSteps', DSSCapacitors.AvailableSteps)
        i = i + 1
        DSSSolution.LoadMult = 1 + i * 0.1  # 10% more each time
        DSSSolution.InitSnap()
        DSSSolution.SolveNoControl()
        DSSSolution.SampleControlDevices() # sample all other controls
        
        # Emulate the cap control Sample Routine and get the bus voltage
        DSSCircuit.SetActiveBus("feedbus")
        V = DSSBus.VMagAngle
        
        # check the first phase magnitude
        Vreg = V[0] / PTratio
        print("Step", i, "Voltage=", Vreg, "LoadMult=", DSSSolution.LoadMult)
        if Vreg < ONsetting: # push a message to bump up the number of steps
            DSSControlQueue.Push(hour, secDelay, ActionCodeAdd, DeviceHandle)
        
        DSSSolution.DoControlActions()   # this sends actions to the local action list
        
        print('DSSControlQueue.NumActions', DSSControlQueue.NumActions)
        if DSSControlQueue.NumActions > 0:
            while DSSControlQueue.PopAction > 0:
                devHandle = DSSControlQueue.DeviceHandle
                if devHandle == DeviceHandle:
                    iCap = DSSCapacitors.First   # Sets designated capacitor active
               
                currentActionCode = DSSControlQueue.ActionCode 
               
                if currentActionCode == ActionCodeAdd:
                    DSSCapacitors.AddStep()
                elif currentActionCode == ActionCodeSub:
                    DSSCapacitors.SubtractStep()
               
                # Print result
                DSSText.Command = "? Capacitor." + DSSCapacitors.Name + ".States"
                print("Capacitor " + DSSCapacitors.Name + " States=" + DSSText.Result)

    
    # Now let's reverse Direction and start removing steps
    while DSSCapacitors.AvailableSteps < DSSCapacitors.NumSteps:
        i = i - 1
        DSSSolution.LoadMult = 1 + i * 0.1  # 10% more each time
        DSSSolution.InitSnap()
        DSSSolution.SolveNoControl()
        DSSSolution.SampleControlDevices() # sample all other controls
        
        # Emulate the cap control Sample Routine and get the bus voltage
        DSSCircuit.SetActiveBus("feedbus")
        V = DSSBus.VMagAngle
        
        # check the first phase magnitude
        Vreg = V[0] / PTratio
        print("Step", i, "Voltage=", Vreg, "LoadMult=", DSSSolution.LoadMult)
        if Vreg > OFFsetting: # push a message to bump down the number of steps
            DSSControlQueue.Push(hour, secDelay, ActionCodeSub, DeviceHandle)
        
        DSSSolution.DoControlActions()   # this send actions to the local action list
        
        if DSSControlQueue.NumActions > 0:
            while DSSControlQueue.PopAction > 0:
                devHandle = DSSControlQueue.DeviceHandle
                if devHandle == DeviceHandle:
                    iCap = DSSCapacitors.First   # Sets designated capacitor active
           
                currentActionCode = DSSControlQueue.ActionCode 
                if currentActionCode == ActionCodeAdd:
                    DSSCapacitors.AddStep()
                elif currentActionCode == ActionCodeSub:
                    DSSCapacitors.SubtractStep()
               
                # Print result
                DSSText.Command = "? Capacitor." + DSSCapacitors.Name + ".States"
                print("Capacitor " + DSSCapacitors.Name + " States=" + DSSText.Result)

if __name__ == '__main__':
    TestCtrlQueue()
