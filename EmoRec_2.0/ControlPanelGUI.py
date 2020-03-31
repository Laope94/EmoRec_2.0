# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

import tkinter as tk # https://docs.python.org/3/library/tkinter.html
from tkinter import scrolledtext
from tkinter import filedialog
from HelperFunctions import HelperFunctions as help
import matplotlib.pyplot as plt # https://matplotlib.org/contents.html
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib import colors, patches

# trieda GUI obsahujúca prvky ovládajúce vstup z mikrofónu a analýzy súboru
# GUI class containing widgets controlling input from microphone and file analysis
class ControlPanel(object):

    def __init__(self, parent, master, ioController, predictionController, filePath=None, deviceID=None, sampleRate=None, windowLength=2, bufferSize=None, streamMode=True):
        self._ioController = ioController # referencia na controller ovládajúci stream | reference to controller of stream
        self._predictionController = predictionController # referencia na controller, ktorý riadi predikciu emócií | reference to controllerec that handles emotion prediction
        self._deviceID = deviceID
        self._sampleRate = sampleRate
        self._windowLength = windowLength
        self._bufferSize = bufferSize

        if(streamMode):
            self._maxDataSize = self._sampleRate*self._windowLength*5 # určuje maximálny počet vzoriek, ktoré budú vykreslené na grafe - 5 okien | determines maximum samples that will be plotted - 5 windows
            self._indices = list(range(self._maxDataSize)) # časť optimalizácie vykreslovania, pozri funkciu redrawWaveform() | part of plotting optimization, see redrawWaveform() function
            self._extendX = True # rovnako ako predchádzajúca premenná | same as variable above
        else:
            self._ioController.createPlayer(filePath,self._windowLength) # vytvorí sa prehrávač pre súbor so zadanou cestou | player is created for file with given path
            self._sampleRate = self._ioController.getPlayerSampleRate()
            playerSamples = self._ioController.getPlayerSamples()
            predictedEmotions = self._predictionController.predictFromFile(playerSamples,self._sampleRate,self._windowLength) # predikcia emócií na načítanom súbore | prediction of emotions of loaded file

        self._master = master
        self._parent = parent
        self._master.title('EmoRec 2 - Analysis')
        self._frame = tk.Frame(self._master)
        self._frame.grid(column=0,row=0, sticky='nwes', padx=10,pady=10)

        # vytvára tkinter widgety | creates tkinter widgets
        
        # vytvorí graf | creates graph
        fig = Figure(figsize=(10,4))
        fig.set_facecolor('#F0F0F0')
        fig.subplots_adjust(left=0.05, bottom=0.15, right=0.99, top=0.95, wspace=0, hspace=0.2)
        
        # graf audio súboru | plot of audio file
        waveformPlot = fig.add_subplot(211)     
        if(streamMode):
            waveformPlot.set_xlim(0,self._windowLength*self._sampleRate*5)
        else:
            waveformPlot.set_xlim(0,len(playerSamples))
        waveformPlot.set_ylim(-1,1)
        waveformPlot.axes.get_xaxis().set_visible(False)
        if(streamMode):
            self._waveform, = waveformPlot.plot([],[])
        else:
            self._waveform, = waveformPlot.plot(range(len(playerSamples)),playerSamples)
        
        # graf emócié | plot of emotions
        emotionPlot = fig.add_subplot(212)
        if(streamMode):     
            emotionPlot.set_xlim(0,5)
        else:
            emotionPlot.set_xlim(0,len(predictedEmotions))
            emotionPlot.set_xticks(range(len(predictedEmotions)))
        emotionPlot.set_ylim(0,1)
        emotionPlot.axes.get_yaxis().set_visible(False)
        cmap = colors.ListedColormap(['red','orange','purple','green','gray','blue','pink','white'])
        bounds = [0,0.9,1.9,2.9,3.9,4.9,5.9,6.9,8]
        norm = colors.BoundaryNorm(bounds,cmap.N)
        if(streamMode):
            self._emotions = emotionPlot.imshow([[]], aspect='auto',extent=(0,5,0,1),cmap=cmap,norm=norm)
        else:
            self._emotions = emotionPlot.imshow([predictedEmotions], aspect='auto',extent=(0,len(predictedEmotions),0,1),cmap=cmap,norm=norm)
        handles = [ patches.Patch(color=[ cmap(norm(i)) for i in range(8)][i], label=['anger','disgust','fear','happiness','neutral','sadness','surprise','silence'][i]) for i in range(8) ]
        legend = emotionPlot.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5,-0.2),fancybox=False, shadow=False, ncol=8)
        legend.get_frame().set_facecolor('#F0F0F0')
        legend.get_frame().set_linewidth(0)
        
        # vykreslenie grafov na plátno | drawing of plots on canvas
        self._canvas = FigureCanvasTkAgg(fig,master=self._frame)
        self._canvas.draw()

        self._buttonStartStream = tk.Button(self._frame, text='Start stream', command= self._startStreamAndUpdateUI)
        self._buttonStartStream.config(width=20,height=2)

        self._buttonStopStream = tk.Button(self._frame, text='Stop stream', command = self._stopStreamAndUpdateUI)
        self._buttonStopStream.config(width=20,height=2)

        self._buttonStartPlayback = tk.Button(self._frame, text='Play', command= self._startPlayback)
        self._buttonStartPlayback.config(width=20,height=2)

        self._buttonStopPlayback  = tk.Button(self._frame, text='Stop', command= self._stopPlayback)
        self._buttonStopPlayback.config(width=20,height=2)

        self._buttonShowLog  = tk.Button(self._frame, text='Show log', command=self._readLog)
        self._buttonShowLog.config(width=20,height=2)

        self._buttonSettings = tk.Button(self._frame, text='Settings', command=self._destroyItself)
        self._buttonSettings.config(width=20,height=2)

        # umiestnenie widgetov v gride | placing of widgets in grid
        self._canvas.get_tk_widget().grid(row=0,column=0, rowspan = 6, padx=10, pady=10)
        self._buttonStartStream.grid(row=0,column=1, padx=10, pady=5)
        self._buttonStopStream.grid(row=1,column=1, padx=10, pady=5)
        self._buttonStartPlayback.grid(row=2,column=1, padx=10, pady=5)
        self._buttonStopPlayback.grid(row=3,column=1, padx=10, pady=5)
        self._buttonShowLog.grid(row=4,column=1, padx=10, pady=5)
        self._buttonSettings.grid(row=5, column=1, padx=10, pady=5)
        
        # zamkne niektoré prvky GUI podla módu | locks some GUI widgets, mode dependent
        if(streamMode):
            help.lockWidget(*(self._buttonStopStream, self._buttonStartPlayback, self._buttonStopPlayback, self._buttonShowLog))
        else: 
            help.lockWidget(*(self._buttonStartStream, self._buttonStopStream))
        
    # začne stream v IOControlleri a upraví GUI | starts stream in IOController and updates GUI
    def _startStreamAndUpdateUI(self):
        self._ioController.startStream(self._deviceID,self._sampleRate,self._windowLength,self._bufferSize,self._dataGrabber,self._predictionController.predictFromStream)
        self._predictionController.clearLogger()
        help.lockWidget(*(self._buttonStartStream,self._buttonSettings, self._buttonShowLog))
        help.unlockWidget(self._buttonStopStream)

    # zastaví stream v IOControlleri a upraví GUI | stops stream in IOController and updates GUI
    def _stopStreamAndUpdateUI(self):
        self._ioController.streamStop()
        help.lockWidget(self._buttonStopStream)
        help.unlockWidget(*(self._buttonStartStream, self._buttonSettings, self._buttonShowLog))
        self._extendX = True

    # spustí prehrávanie súboru | starts playback of file
    def _startPlayback(self):
        self._ioController.startPlayback()

    # zastaví prehrávanie súboru | stops playback of file
    def _stopPlayback(self):
        self._ioController.stopPlayback()

    # táto funkcia slúži na získavanie údajov z IOControllera | this function gets data from IOController
    def _dataGrabber(self,data,predictions):
        self._master.after(0, lambda : self._redrawWaveform(data,predictions)) # funkcia dataGrabber je volaná z iného vlákna, ale prekreslenie tkinter môže byť volané iba z mainloop vlákna, inak spadne | dataGrabber is called from another thread, but tkinter draw can be called only from mainloop, crashes otherwise

    # prekreslí graf
    def _redrawWaveform(self, data, predictions):
        if(self._extendX):                                           # 
            self._waveform.set_xdata(self._indices[0:len(data)])     # pozri nižšie pre vysvetlenie tejto časti
            if(len(data)==self._maxDataSize):                        # see below for explanation of this part
                self._extendX = False                                #
        self._waveform.set_ydata(data) # update dát | updates data
        self._emotions.set_data(predictions) # update emócií | update of emotions
        self._canvas.draw() # prekreslenie | redraw of plot
        self._canvas.flush_events()
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
        # this slightly improves CPU performance
        # note - one more method of redrawing exists - clear the plot, then add new data and redraw, it doesn't require knowing indexes to data, but it's much slower and more CPU demanding

    # zobrazí okno s históriou predikcie | shows window with history of prediction
    def _readLog(self): 
        self._logWindow = tk.Toplevel(self._master)
        self._logWindow.resizable(False,False)
        self._logWindow.title('Log')
        frame = tk.Frame(self._logWindow)
        logText = scrolledtext.ScrolledText(master=frame, width=40, height=20)
        logText.insert('1.0',self._predictionController.getLog())
        help.lockWidget(logText)
        buttonSaveLog = tk.Button(frame, text='Save log', command=self._saveLog)
        buttonSaveLog.config(width=10,height=2)
        frame.grid(column=0,row=0, sticky='nwes', padx=5,pady=5)
        logText.grid(row=0,column=0, columnspan=3, sticky='nwes', padx=5,pady=5)
        buttonSaveLog.grid(row=1,column=1,sticky='news', padx=5,pady=5)
        self._logWindow.focus_force()

    # otvára okno explorera a na zadanú cestu uloží csv súbor | opens explorer window and saves csv file to selected path
    def _saveLog(self):
        savePath = filedialog.asksaveasfilename(initialdir = "/",title = "Save log",filetypes = (("csv","*.csv"),))
        if(len(savePath)>0):
            savePath = savePath+'.csv'
            self._predictionController.saveCSV(savePath)
        self._logWindow.focus_force()

    # vymaže ControlPanelGUI frame z hlavného okna | removes ControlPanelGUI frame from main window
    def _destroyItself(self):
        self._frame.grid_forget()
        self._frame.destroy()
        self._parent.createSettings(self._master) # návrat na SettingsGUI