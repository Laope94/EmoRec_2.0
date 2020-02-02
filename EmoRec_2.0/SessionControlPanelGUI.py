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

# trieda GUI obsahujúca prvky ovládajúce vstup z mikrofónu a analýzy súboru
# GUI class containing widgets controlling input from microphone and file analysis
class SessionControlPanel(object):

    def __init__(self, parent, master, pathfile, packedVariables, inputController):
        self.inputController = inputController # referencia na controller ovládajúci stream | reference to controller of stream
        self.streamMode = self.isStreamMode(pathfile) # True/False premenná, ktorá určuje či sa má GUI prispôsobiť vstupu zo streamu alebo analýze hotového súboru | True/False variable that determines if GUI is supposed to customise to stream input or file analysis

        if(self.streamMode): # v móde vstupu zo streamu sa rozbalia premenné | in stream mode variables are unpacked
            self.deviceID = help.getValueByKey(packedVariables,'deviceID')
            self.sampleRate = help.getValueByKey(packedVariables,'sampleRate')
            self.windowLength = help.getValueByKey(packedVariables,'windowLength')
            self.bufferSize = help.getValueByKey(packedVariables,'bufferSize')
            self.maxDataSize = self.sampleRate*self.windowLength*5 # určuje maximálny počet vzoriek, ktoré budú vykreslené na grafe - 5 okien | determines maximum samples that will be plotted - 5 windows
            self.indices = list(range(self.maxDataSize)) # časť optimalizácie vykreslovania, pozri funkciu redrawWaveform() | part of plotting optimization, see redrawWaveform() function
            self.extendX = True # rovnako ako predchádzajúca premenná | same as variable above
        else: # v móde analýzy súboru sa uloží cesta k súboru | in file analysis mode path to file is saved
            self.pathfile = pathfile

        self.master = master
        self.parent = parent
        self.master.title('EmoRec 2.0 - Session')
        self.frame = tk.Frame(self.master)
        self.frame.grid(column=0,row=0, sticky='nwes', padx=10,pady=10)

        # vytvára tkinter widgety | creates tkinter widgets
        self.fig = Figure(figsize=(10,2))
        self.fig.set_facecolor('#F0F0F0')
        self.fig.subplots_adjust(left=0.05, bottom=0.15, right=0.99, top=0.95, wspace=0, hspace=0)
        self.waveformPlot = self.fig.add_subplot(111)
        self.waveformPlot.set_ylim(-1,1)
        self.waveformPlot.set_xlim(0,self.windowLength*self.sampleRate*5)
        self.waveform, = self.waveformPlot.plot([],[])
        self.canvas = FigureCanvasTkAgg(self.fig,master=self.frame)
        self.canvas.draw()

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

        # umiestnenie widgetov v gride | placing of widgets in grid
        self.canvas.get_tk_widget().grid(row=0,column=0, rowspan = 3, padx=10, pady=10)
        self.buttonStartStream.grid(row=0,column=1, padx=10, pady=5)
        self.buttonStopStream.grid(row=1,column=1, padx=10, pady=5)
        self.buttonStartPlayback.grid(row=2,column=1, padx=10, pady=5)
        self.buttonStopPlayback.grid(row=3,column=1, padx=10, pady=5)
        self.buttonShowLog.grid(row=4,column=1, padx=10, pady=5)
        self.buttonSettings.grid(row=5, column=1, padx=10, pady=5)
        self.__initialLock()

    # určí v akom móde má GUI pracovať podla toho či existuje cesta k súboru alebo nie | determines in which mode is GUI supposed to work by existence of path to file (if path to file doesn't exists, packedVariables should exist and vice versa)
    def isStreamMode(self,filepath):
        if(filepath==None):
            return True
        else: 
            return False

    # zamkne niektoré prvky GUI podla módu | locks some GUI widgets, mode dependent
    def __initialLock(self):
        if(self.streamMode):
            help.lockWidget(*(self.buttonStopStream, self.buttonStartPlayback, self.buttonStopPlayback, self.buttonShowLog))
        else: 
            help.lockWidget(*(self.buttonStartStream, self.buttonStopStream, self.buttonStopPlayback))
    
    # vymaže SessionControlPanelGUI frame z hlavného okna | removes SessionControlPanelGUI frame from main window
    def destroyItself(self):
        self.frame.grid_forget()
        self.frame.destroy()
        self.parent.createSessionSettings(self.master) # návrat na SessionSettingsGUI

    # táto funkcia slúži na získavanie údajov z InputControllera | this function gets data from InputController
    def dataGrabber(self,data):
        self.master.after(0, lambda : self.redrawWaveform(data)) # funkcia dataGrabber je volaná z iného vlákna, ale prekreslenie tkinter môže byť volané iba z mainloop vlákna, inak spadne | dataGrabber is called from another thread, but tkinter draw can be called only from mainloop, crashes otherwise

    # prekreslí graf
    def redrawWaveform(self, data):
        if(self.extendX):                                           # 
            self.waveform.set_xdata(self.indices[0:len(data)])      # pozri nižšie pre vysvetlenie tejto časti
            if(len(data)==self.maxDataSize):                        # see below for explanation of this part
                self.extendX = False                                #
        self.waveform.set_ydata(data) # update dát | updates data
        self.canvas.draw() # prekreslenie | redraw of plot
        self.canvas.flush_events()
        # vysvetlenie
        # optimalizácia vykreslovania grafu - indexy vzoriek buffera sa zobrazujú na X os a hodnoty vzoriek sa zobrazujú na Y os
        # počet prvkov X osi musí vždy sedieť s počtom prvkov, ktoré budú zobrazené na Y osi, ale na začiatku streamu ich počet nie je pevný - počet framov sa zvyšuje až kým ich nie je 5
        # nie je možné priamo zobrať indexy v poli vzoriek, ktoré prišli z buffera, ale je možné vytvoriť pole obsahujúce celé čísla od 0 až do konečného počtu vzoriek
        # aby sa takéto pole nevytváralo vždy znova pri prekreslení tak bolo vytvorené iba raz v __init__ metóde a iba sa z neho berie taká časť, ktorá zodpovedá súčasnému počtu vzoriek
        # ak sa buffer naplní na 5 framov tak už viac nie je nutné updatovať aký je počet vzoriek, pretože od tohto momentu už bude ich počet pevný - premenná extendX
        # takýmto spôsobom je možné mierne zmenšiť nároky na CPU
        # poznámka - existuje ešte jedna metóda prekreslenia - graf vymazať, vložiť nové dáta a prekresliť, pri tejto metóde nie je nutné poznať indexy dát, ale je pomalšia a náročnejšia na CPU
        # explanation
        # optimization of plot drawing - indexes of samples from buffer are displayed on X axis and values of samples are displayed on Y axis
        # number of X axis elements must be the same as number of Y axis elements, but on beggining of stream their number is not firm - number of frames is increasing until there are 5
        # it's not possible to take indexes of samples directly, but list containing numbers from 0 to number of samples can be made
        # to prevent creating this list everytime during redraw, list is created in __init__ function and is only sliced as required to match number of samples
        # if buffer contains 5 frames then it's not necessary to update number of samples anymore, because their number will be firm from this moment - variable extendX
        # this was slightly improves CPU performance
        # note - one more method of redrawing exists - clear the plot, then add new data and redraw, it doesn't require knowing indexes to data, but it's much slower and more CPU demanding
        
    # začne stream v InputControlleri a upraví GUI | starts stream in InputController and updates GUI
    def startStreamAndUpdateUI(self):
        self.inputController.startStream(self.deviceID,self.sampleRate,self.windowLength,self.bufferSize,self.dataGrabber)
        help.lockWidget(*(self.buttonStartStream,self.buttonSettings))
        help.unlockWidget(self.buttonStopStream)

    # zastaví stream v InputControlleri a upraví GUI | stops stream in InputController and updates GUI
    def stopStreamAndUpdateUI(self):
        self.inputController.streamStop()
        help.lockWidget(self.buttonStopStream)
        help.unlockWidget(*(self.buttonStartStream, self.buttonSettings))
        self.extendX = True