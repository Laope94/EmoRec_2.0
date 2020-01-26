# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

class SessionControls(object):
    import tkinter as tk
    from HelperFunctions import HelperFunctions as help
    import numpy as np

    def __init__(self, parent, master, pathfile, packedVariables, inputController):
        self.inputController = inputController
        self.pathfile = pathfile
        self.deviceID = None
        self.sampleRate = None
        self.windowLength = None
        if(packedVariables != None):
            self.deviceID = self.help.getValueByKey(packedVariables,'deviceID')
            self.sampleRate = self.help.getValueByKey(packedVariables,'sampleRate')
            self.windowLength = self.help.getValueByKey(packedVariables,'windowLength')

        self.master = master
        self.parent = parent
        self.master.title('EmoRec 2.0 - Session')
        self.frame = self.tk.Frame(self.master)
        self.frame.grid(column=0,row=0, sticky='nwes', padx=10,pady=10)

        #widgets initialization
        self.buttonStartSession = self.tk.Button(self.frame, text='Štart', command= lambda : self.inputController.startStream(self.deviceID,self.sampleRate,self.dataGrabber))
        self.buttonStartSession.config(width=20,height=2)

        self.buttonStopSession = self.tk.Button(self.frame, text='Stop', command = self.stopButtonAction)
        self.buttonStopSession.config(width=20,height=2)

        self.buttonStartPlayback = self.tk.Button(self.frame, text='Prehrať')
        self.buttonStartPlayback.config(width=20,height=2)

        self.buttonStopPlayback  = self.tk.Button(self.frame, text='Zastaviť prehrávanie')
        self.buttonStopPlayback.config(width=20,height=2)

        self.buttonShowLog  = self.tk.Button(self.frame, text='Zobraziť log')
        self.buttonShowLog.config(width=20,height=2)

        self.buttonSettings = self.tk.Button(self.frame, text='Nastavenia', command=self.destroyItself)
        self.buttonSettings.config(width=20,height=2)

        #grid placement
        self.buttonStartSession.grid(row=0,column=1, padx=10, pady=5)
        self.buttonStopSession.grid(row=1,column=1, padx=10, pady=5)
        self.buttonStartPlayback.grid(row=2,column=1, padx=10, pady=5)
        self.buttonStopPlayback.grid(row=3,column=1, padx=10, pady=5)
        self.buttonShowLog.grid(row=4,column=1, padx=10, pady=5)
        self.buttonSettings.grid(row=5, column=1, padx=10, pady=5)

    def destroyItself(self):
        self.frame.grid_forget()
        self.frame.destroy()
        self.parent.createSessionSettings(self.master)

    def dataGrabber(self,data):
        self.numpyData = self.np.array(data)
        print(self.numpyData.shape)

    def stopButtonAction(self):
        self.inputController.streamStop()