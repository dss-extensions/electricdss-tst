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

        # self.dssText.Command = "set casename=scenario_" + str(self.row["Scenario ID"])

        self.dssText.Command = "PVSystem.PV.irradiance=" + str(irradiance)
        self.dssText.Command = "PVSystem.PV.kVA=" + str(self.row["kVA"])
        self.dssText.Command = "PVSystem.PV.PFPriority=" + str(self.row["PF Priority"])
        self.dssText.Command = "PVSystem.PV.wattPriority=" + str(self.row["P Priority"])
        self.dssText.Command = "PVSystem.PV.%cutIn=" + str(self.row["cutIn"])
        self.dssText.Command = "PVSystem.PV.%cutOut=" + str(self.row["cutIn"])
        self.dssText.Command = "PVSystem.PV.%PminNoVars=" + str(self.row["PminNoVars"])
        self.dssText.Command = "PVSystem.PV.%PminkvarMax=" + str(self.row["PminkvarLimit"])
        self.dssText.Command = "PVSystem.PV.kvarmax=" + str(self.row["kvar Max"])
        self.dssText.Command = "PVSystem.PV.kvarmaxabs=" + str(self.row["kvar Max Abs"])
        self.dssObj.AllowForms = "false"
        self.dssText.Command = "Solve"

        self.dssCircuit.SetActiveElement("PVSystem.PV")

        # self.voltage = self.dssCktElement.VoltagesMagAng[0] / 7967.433715
        self.activePower = self.dssCktElement.Powers[0]
        self.reactivePower = self.dssCktElement.Powers[1]
        self.pf = abs(self.activePower) / sqrt(self.reactivePower**2 + self.activePower**2) * self.activePower * self.reactivePower / abs(self.activePower) / abs(self.reactivePower)
        self.apparentPower = sqrt(self.reactivePower**2 + self.activePower**2)