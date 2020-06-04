import win32com.client
from win32com.client import makepy
from numpy import *
from pylab import *
import os               # for path manipulation and directory operations

class DSS(object):

    #------------------------------------------------------------------------------------------------------------------#
    def __init__(self, dssFileName, row):
        """ Compile OpenDSS model and initialize variables."""

        # These variables provide direct interface into OpenDSS
        sys.argv = ["makepy", r"OpenDSSEngine.DSS"]
        makepy.main()  # ensures early binding and improves speed

        # Create a new instance of the DSS
        self.dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")

        # Start the DSS
        if self.dssObj.Start(0) == False:
            print "DSS Failed to Start"
        else:
            #Assign a variable to each of the interfaces for easier access
            self.dssText = self.dssObj.Text
            self.dssCircuit = self.dssObj.ActiveCircuit # Maybe this one can help
            self.dssSolution = self.dssCircuit.Solution
            self.dssCktElement = self.dssCircuit.ActiveCktElement
            self.dssBus = self.dssCircuit.ActiveBus
            self.dssMeters = self.dssCircuit.Meters
            self.dssPDElement = self.dssCircuit.PDElements

        # Always a good idea to clear the DSS when loading a new circuit
        self.dssObj.ClearAll()

        # Load the given circuit master file into OpenDSS
        self.dssText.Command = "compile [" + dssFileName + "]"

        self.row = row

    def process(self, irradiance):

        self.dssText.Command = "Vsource.Source.pu=" + str(self.row["Vsource (pu)"])
        self.dssText.Command = "set casename=scenario_" + str(self.row["Scenario ID"])
        self.dssText.Command = "PVSystem2.PV.%cutIn=" + str(self.row["%cutIn"])
        self.dssText.Command = "PVSystem2.PV.pctPminNoVars=" + str(self.row["pctPminNoVars"])
        self.dssText.Command = "PVSystem2.PV.pctPminkvarLimit=" + str(self.row["pctPminkvarLimit"])

        self.dssText.Command = "PVSystem2.PV.irradiance=" + str(irradiance)
        self.dssObj.AllowForms = "false"
        self.dssText.Command = "Solve"

        self.dssCircuit.SetActiveElement("PVSystem2.PV")

        self.voltage = self.dssCktElement.VoltagesMagAng[0] / 7967.433715
        self.activePower = self.dssCktElement.Powers[0]
        self.reactivePower = self.dssCktElement.Powers[1]

