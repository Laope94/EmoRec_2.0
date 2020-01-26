# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

import tkinter as tk # https://docs.python.org/2/library/tkinter.html knižnica pre GUI | library for GUI
from InputController import InputController
from SessionSettings import SessionSettings
from SessionControls import SessionControls

class Main(object):
    # hlavná trieda, slúži ako vstupný bod programu, spravuje vytváranie GUI na hlavnom vlákne
    # main class, serves as entry point, manages creation of GUI on mainloop

    # hlavná funkcia programu, vytvára hlavné okno GUI | main function, creates main GUI window
    def main(self):
        self.masterWindow = tk.Tk()
        self.masterWindow.resizable(False,False)
        self.createSessionSettings(self.masterWindow)
        self.masterWindow.mainloop()

    # vytvára GUI s úvodnými nastaveniami session | creates GUI with session settings
    def createSessionSettings(self,master):
        SessionSettings(self,master,InputController().getDeviceList())

    # vytvára GUI s kontrolným panelom session - ovládanie vstupu, vyhodnocovanie emócií atď... 
    # creates GUI with session control panel - input controls, emotion categorization etc...
    def createSessionControls(self,master,filepath,packedVariables):
        SessionControls(self,master,filepath,packedVariables, InputController())

if __name__ == '__main__':
    Main().main()