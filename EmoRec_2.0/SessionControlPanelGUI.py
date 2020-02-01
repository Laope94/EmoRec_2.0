# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

import tkinter as tk
from HelperFunctions import HelperFunctions as help
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

class SessionControlPanel(object):

    def __init__(self, parent, master, pathfile, packedVariables, inputController):
        self.inputController = inputController
        self.streamMode = self.isStreamMode(pathfile)

        if(self.streamMode):
            self.deviceID = help.getValueByKey(packedVariables,'deviceID')
            self.sampleRate = help.getValueByKey(packedVariables,'sampleRate')
            self.windowLength = help.getValueByKey(packedVariables,'windowLength')
            self.bufferSize = help.getValueByKey(packedVariables,'bufferSize')
        else:
            self.pathfile = pathfile

        self.master = master
        self.parent = parent
        self.master.title('EmoRec 2.0 - Session')
        self.frame = tk.Frame(self.master)
        self.frame.grid(column=0,row=0, sticky='nwes', padx=10,pady=10)

        #widgets initialization
        self.fig = Figure(figsize=(10,2))
        self.fig.set_facecolor('#F0F0F0')
        self.fig.subplots_adjust(left=0.05, bottom=0.15, right=0.99, top=0.95, wspace=0, hspace=0)
        self.graph = self.fig.add_subplot(111)
        self.graph.set_ylim(-1,1)
        self.graph.set_xlim(0,self.windowLength*self.sampleRate*5)
        self.plotCanvas = FigureCanvasTkAgg(self.fig,master=self.frame)
        self.plotCanvas.draw()

        self.buttonStartStream = tk.Button(self.frame, text='Štart', command= self.startStreamAndUpdateUI)
        self.buttonStartStream.config(width=20,height=2)

        self.buttonStopStream = tk.Button(self.frame, text='Stop', command = self.stopStreamAndUpdateUI)
        self.buttonStopStream.config(width=20,height=2)

        self.buttonStartPlayback = tk.Button(self.frame, text='Prehrať')
        self.buttonStartPlayback.config(width=20,height=2)

        self.buttonStopPlayback  = tk.Button(self.frame, text='Zastaviť prehrávanie')
        self.buttonStopPlayback.config(width=20,height=2)

        self.buttonShowLog  = tk.Button(self.frame, text='Zobraziť log')
        self.buttonShowLog.config(width=20,height=2)

        self.buttonSettings = tk.Button(self.frame, text='Nastavenia', command=self.destroyItself)
        self.buttonSettings.config(width=20,height=2)

        #grid placement
        self.plotCanvas.get_tk_widget().grid(row=0,column=0, rowspan = 3, padx=10, pady=10)
        self.buttonStartStream.grid(row=0,column=1, padx=10, pady=5)
        self.buttonStopStream.grid(row=1,column=1, padx=10, pady=5)
        self.buttonStartPlayback.grid(row=2,column=1, padx=10, pady=5)
        self.buttonStopPlayback.grid(row=3,column=1, padx=10, pady=5)
        self.buttonShowLog.grid(row=4,column=1, padx=10, pady=5)
        self.buttonSettings.grid(row=5, column=1, padx=10, pady=5)
        self.initialLock()

    def isStreamMode(self,filepath):
        if(filepath==None):
            return True
        else: 
            return False

    def initialLock(self):
        if(self.streamMode):
            help.lockWidget(*(self.buttonStopStream, self.buttonStartPlayback, self.buttonStopPlayback, self.buttonShowLog))
        else: 
            help.lockWidget(*(self.buttonStartStream, self.buttonStopStream, self.buttonStopPlayback))

    def destroyItself(self):
        self.frame.grid_forget()
        self.frame.destroy()
        self.parent.createSessionSettings(self.master)

    def dataGrabber(self,data):
        self.numpyData = data
        self.master.after(0, self.redrawGraph)

    def redrawGraph(self):
        self.graph.clear()
        self.graph.set_xlim(0,self.sampleRate*self.windowLength*5)
        self.graph.set_ylim(-1,1)
        self.graph.plot(self.numpyData)
        self.plotCanvas.draw()

    def startStreamAndUpdateUI(self):
        self.inputController.startStream(self.deviceID,self.sampleRate,self.windowLength,self.bufferSize,self.dataGrabber)
        help.lockWidget(*(self.buttonStartStream,self.buttonSettings))
        help.unlockWidget(self.buttonStopStream)

    def stopStreamAndUpdateUI(self):
        self.inputController.streamStop()
        help.lockWidget(self.buttonStopStream)
        help.unlockWidget(*(self.buttonStartStream, self.buttonSettings))