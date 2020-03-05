
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
    column_names = ["Active Power (kW)", "Reactive Power (kvar)", "Power Factor", "Apparent Power (kVA)"]

    def __init__(self):

        start_time = timeit.default_timer()

        # dssFileName = r"C:\Users\ppra005\Box\Documents_PC\Projects\Inverter_watt_modes\dss\SnapShot_wattpf.dss"

        scenario_file = "C:\Users\ppra005\Box\Documents_PC\Projects\Inverter_watt_modes\Code\scenarios.csv"
        scenario_file = "C:\Users\ppra005\Box\Documents_PC\Projects\Inverter_watt_modes\Code\scenarios_watt-var_Stephen.csv"

        outputFolder = r"C:\Users\ppra005\Box\Documents_PC\Projects\Inverter_watt_modes\Results"
        outputFolder = r"C:\Users\ppra005\Box\Documents_PC\Projects\Inverter_watt_modes\Results_Stephen"

        irradiance_list = range(0, 1000, 1)

        # Read the scenarios file
        df_scenarios = pd.read_csv(scenario_file, engine="python")

        for index, row in df_scenarios.iterrows():
            print(u"Scenario ID " + str(row["Scenario ID"]))

            results_dic = {}

            dssFileName = row["OpenDSS file"]

            conditionObject = ControlOpenDSS.DSS(dssFileName, row)

            # Sets condition outputfolder
            self.scenario_outputFolder = outputFolder + "/scenario_test"
            if not os.path.exists(self.scenario_outputFolder):
                os.makedirs(self.scenario_outputFolder)

            for irradiance in irradiance_list:

                irradiance = irradiance / 1000.0
                conditionObject.process(irradiance)

                results_dic[irradiance] = [conditionObject.activePower * -3, conditionObject.reactivePower * -3, conditionObject.pf, conditionObject.apparentPower * 3]

            df_results = pd.DataFrame().from_dict(results_dic, orient="index", columns=["3ph Active Power (kW)", "3ph Reactive Power (kvar)", "Power Factor", "3ph Apparent Power (kVA)"]).sort_index()
            df_results["Irradiance"] = df_results.index


            title = "kVA is {} with Priority in (P: {}), (Q: {}), or (PF: {})".format(row["kVA"], row["P Priority"], row["Q Priority"], row["PF Priority"])
            data = df_results
            file_name = row["Scenario ID"]
            self.plot_powers(title, data, file_name)
            self.plot_pf(title, data, file_name)

            df_results.to_csv(self.scenario_outputFolder + "\\" + str(file_name) + r".csv")


        elapsed = timeit.default_timer() - start_time

        print "RunTime is: " + str(elapsed)

    def plot_powers(self, title, data, file_name):
        #plt.clf()
        # sns.set(style="ticks")
        # Reset default params
        sns.set()
        sns.set(rc={'figure.figsize': (28, 16)})
        sns.set_context("poster")

        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
        g1 = sns.lineplot(y="3ph Active Power (kW)", x="Irradiance", data=data, ax=ax1)
        ax1.set(xlabel="Irradiance", ylabel="kW", xlim=[0, 1])
        g2 = sns.lineplot(y="3ph Reactive Power (kvar)", x="Irradiance", data=data, ax=ax2)
        ax2.set(xlabel="Irradiance", ylabel="kvar", xlim=[0, 1])
        g3 = sns.lineplot(y="3ph Apparent Power (kVA)", x="Irradiance", data=data, ax=ax3)
        ax3.set(xlabel="Irradiance", ylabel="kVA", xlim=[0, 1])
        g4 = sns.lineplot(y="Power Factor", x="Irradiance", data=data, ax=ax4)
        ax4.set(xlabel="Irradiance", ylabel="PF", xlim=[0, 1])

        fig.suptitle(title)

        # plt.show()

        plt.savefig(
            self.scenario_outputFolder + "\\" + str(file_name) + ".png",
            dpi=None, facecolor='w', edgecolor='w',
            orientation='portrait', papertype=None, format=None,
            transparent=False, bbox_inches="tight", pad_inches=0.1,
            frameon=None)

    def plot_pf(self, title, data, file_name):
        #plt.clf()
        # sns.set(style="ticks")
        # Reset default params
        sns.set()
        sns.set(rc={'figure.figsize': (28, 16)})
        sns.set_context("poster")

        fig, ax1 = plt.subplots(1, 1)
        g1 = sns.lineplot(y="Power Factor", x="Irradiance", data=data, ax=ax1)
        ax1.set(xlabel="Irradiance", ylabel="PF", xlim=[0, 1])
        # g1.yticklabels = ['-1', '-0.95', '-0.9', '-0.85', '0', '0.85', '0.9', '0.95', '1']

        fig.suptitle(title)

        # plt.show()

        plt.savefig(
            self.scenario_outputFolder + "\\" + str(file_name) + "_PF.png",
            dpi=None, facecolor='w', edgecolor='w',
            orientation='portrait', papertype=None, format=None,
            transparent=False, bbox_inches="tight", pad_inches=0.1,
            frameon=None)

if __name__ == '__main__':
    Main()
