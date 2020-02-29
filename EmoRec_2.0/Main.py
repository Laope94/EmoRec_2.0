# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

import tkinter as tk # https://docs.python.org/2/library/tkinter.html knižnica pre GUI | library for GUI
from IOController import IOController
from PredictionController import PredictionController
from SettingsGUI import Settings
from ControlPanelGUI import ControlPanel

# hlavná trieda, slúži ako vstupný bod programu, spravuje vytváranie GUI na hlavnom vlákne
# main class, serves as entry point, manages creation of GUI on mainloop
class Main(object):

    # hlavná funkcia programu, vytvára hlavné okno GUI | main function, creates main GUI window
    def main(self):
        self.ioController = IOController()
        self.predictionController = PredictionController()
        self.masterWindow = tk.Tk()
        self.masterWindow.resizable(False,False)
        self.createSettings(self.masterWindow)
        self.masterWindow.mainloop()

    # vytvára GUI s úvodnými nastaveniami session | creates GUI with session settings
    def createSettings(self,master):
        Settings(self,master,self.ioController.getDeviceList())

    # vytvára GUI s kontrolným panelom session - ovládanie vstupu, vyhodnocovanie emócií atď... 
    # creates GUI with session control panel - input controls, emotion categorization etc...
    def createSessionControls(self,master,packedVariables):
        ControlPanel(self,master,self.ioController, self.predictionController,**{k: v for k, v in packedVariables.items() if v is not None})

if __name__ == '__main__':
    Main().main()