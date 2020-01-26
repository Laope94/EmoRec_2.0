# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

class Main(object):
    # hlavná trieda, slúži ako vstupný bod programu, spravuje vytváranie GUI na hlavnom vlákne
    # main class, serves as entry point, manages creation of GUI on mainloop

    import tkinter as tk # https://docs.python.org/2/library/tkinter.html knižnica pre GUI | library for GUI
    from InputController import InputController
    from HelperFunctions import HelperFunctions as help
    from SessionSettings import SessionSettings
    from SessionControls import SessionControls

    # hlavná funkcia programu, vytvára hlavné okno GUI | main function, creates main GUI window
    def main(self):
        self.masterWindow = self.tk.Tk()
        self.masterWindow.resizable(False,False)
        self.createSessionSettings(self.masterWindow)
        self.masterWindow.mainloop()

    # vytvára GUI s úvodnými nastaveniami session | creates GUI with session settings
    def createSessionSettings(self,master):
        self.SessionSettings(self,master,self.InputController().getDeviceList())

    # vytvára GUI s kontrolným panelom session - ovládanie vstupu, vyhodnocovanie emócií atď... 
    # creates GUI with session control panel - input controls, emotion categorization etc...
    def createSessionControls(self,master,filepath,packedVariables):
        self.SessionControls(self,master,filepath,packedVariables, self.InputController())

if __name__ == '__main__':
    Main().main()