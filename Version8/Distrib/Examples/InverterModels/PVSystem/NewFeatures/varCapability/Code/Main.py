
import ControlOpenDSS # Class which creates the OpenDSS object
import string
import os
import csv
import timeit
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class Main(object):
    column_names = ["Voltage (pu)", "Active Power (kW)", "Reactive Power (kvar)"]

    def __init__(self):

        start_time = timeit.default_timer()

        type = "kvarNeg"
        #type = "kvar"
        #type = "VV"

        dssFileName = r"C:\OpenDSS_svn\Version8\Distrib\Examples\InverterModels\PVSystem2\NewFeatures\varCapability\PV_currentkvarLimit_" + type + ".dss"

        scenariosConfiguration_file = r"C:\OpenDSS_svn\Version8\Distrib\Examples\InverterModels\PVSystem2\NewFeatures\varCapability\scenarios_" + type + ".csv"

        outputFolder = r"C:\OpenDSS_svn\Version8\Distrib\Examples\InverterModels\PVSystem2\NewFeatures\varCapability\Results_" + type

        # Read the scenarios file
        df_scenarios = pd.read_csv(scenariosConfiguration_file, engine="python")

        irradiance_list = range(0, 1000, 1)

        results_dic = {}

        for index, row in df_scenarios.iterrows():
            print(u"Scenario ID " + str(row["Scenario ID"]))

            conditionObject = ControlOpenDSS.DSS(dssFileName, row)

            # Sets condition outputfolder
            scenario_outputFolder = outputFolder + "/scenario_" + str(row["Scenario ID"])
            if not os.path.exists(scenario_outputFolder):
                os.makedirs(scenario_outputFolder)

            for irradiance in irradiance_list:

                irradiance = irradiance / 1000.0
                conditionObject.process(irradiance)

                results_dic[irradiance] = [conditionObject.voltage, conditionObject.activePower * -3, conditionObject.reactivePower * -3]

            df_results = pd.DataFrame().from_dict(results_dic, orient="index", columns=["Voltage (pu)", "3ph Active Power (kW)", "3ph Reactive Power (kvar)"]).sort_index()
            df_results.to_csv(scenario_outputFolder + r"\p_q.csv")

            #sns.set(style="ticks")


            # Reset default params
            sns.set()

            # Set context to `"paper"`
            sns.set_context("paper")

            #ax = sns.scatterplot(x="3ph Active Power (kW)", y="3ph Reactive Power (kW)", data=df_results)
            df_results.plot(kind='scatter', x="3ph Active Power (kW)", y="3ph Reactive Power (kvar)", color='red')


            #plt.show()
            #ax.figure.savefig(scenario_outputFolder + r"\p_q.png")
            plt.savefig(scenario_outputFolder + r"\p_q.png")

        elapsed = timeit.default_timer() - start_time

        print "RunTime is: " + str(elapsed)


if __name__ == '__main__':
    Main()
