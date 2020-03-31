# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

import tkinter as tk # https://docs.python.org/3/library/tkinter.html
from tkinter import filedialog
from HelperFunctions import HelperFunctions as help

# trieda GUI - okno obsahujúce nastavenia a parametre
# GUI class - contains settings and parameters
class Settings(object):

    def __init__(self, parent, master, deviceList):
        self._parent = parent # umožňuje prístup do triedy z ktorej bolo toto okno vytvorené | allows access to class which created this window
        self._master = master
        self._master.title('EmoRec 2 - Settings')
        self._deviceList = deviceList
        self._frame = tk.Frame(self._master)
        self._frame.grid(column=0,row=0, sticky='nwes', padx=10,pady=10)

        # vytvára tkinter widgety | creates tkinter widgets
        labelNewSession = tk.Label(self._frame,text='New analysis', font=('',15,'bold'))

        labelDevice = tk.Label(self._frame,text='Input device :')
        self._selectedDevice = tk.StringVar(self._master)
        self._selectedDevice.set('-------------------- none --------------------')
        dropdownDeviceSelection = tk.OptionMenu(self._frame,self._selectedDevice,*self._deviceList.keys(), command=lambda widget : help.unlockWidget(self._buttonConfirmSettings))
        dropdownDeviceSelection.config(relief='sunken', borderwidth=0.5, background='white', activebackground='white', width=100)

        labelSampleRate = tk.Label(self._frame,text='Sample rate (Hz) :')
        self._selectedSampleRate = tk.StringVar(self._master)
        self._selectedSampleRate.set('48000')
        dropdownSampleRate = tk.OptionMenu(self._frame,self._selectedSampleRate,*('44100','48000','64000','88200','96000'))
        dropdownSampleRate.config(relief='sunken', borderwidth=0.5, background='white', activebackground='white', width=100)

        labelWindowLength = tk.Label(self._frame,text='Predictive window length (s) :')
        self._selectedWindowLength = tk.StringVar(self._master)
        self._selectedWindowLength.set('2')
        dropdownWindowLength = tk.OptionMenu(self._frame,self._selectedWindowLength,*('2','3','4','5','6','7','8','9','10'))
        dropdownWindowLength.config(relief='sunken', borderwidth=0.5, background='white', activebackground='white', width=100)

        labelBufferSize = tk.Label(self._frame,text='Buffer size (b) :')
        self._selectedBufferSize = tk.StringVar(self._master)
        self._selectedBufferSize.set('1024')
        dropdownBufferSize = tk.OptionMenu(self._frame,self._selectedBufferSize,*('8','16','32','64','128','256','512','1024','2048'))
        dropdownBufferSize.config(relief='sunken', borderwidth=0.5, background='white', activebackground='white', width=100)

        self._buttonConfirmSettings = tk.Button(self._frame, text='Start analysis', state='disabled', command=self._sendSettings)
        self._buttonConfirmSettings.config(width=20,height=2)

        labelLoadFile = tk.Label(self._frame,text='Load file', font=('',15,'bold'))
        self._entryFilePath = tk.Entry(self._frame, state='readonly')
        self._entryFilePath.config(readonlybackground='white')
        buttonFileDialog = tk.Button(self._frame,text="Browse", command=self._openFileDialog)

        self._buttonConfirmFileSelection = tk.Button(self._frame,text='Analyse file', state='disabled', command=self._sendFilePath)
        self._buttonConfirmFileSelection.config(width=20,height=2)

        # umiestnenie widgetov v gride | placing of widgets in grid
        labelNewSession.grid(row=0,column=0,columnspan=2,padx=10,pady=10,sticky='w')
        labelDevice.grid(row=1,column=0,padx=2,pady=5, sticky='e')
        dropdownDeviceSelection.grid(row=1, column=1, padx=5, pady=5)
        labelSampleRate.grid(row=2,column=0, padx=2, pady=5, sticky='e')
        dropdownSampleRate.grid(row=2, column=1, padx=5, pady=5)
        labelWindowLength.grid(row=3,column=0,padx=2,pady=5, sticky='e')
        dropdownWindowLength.grid(row=3, column=1, padx=5, pady=5)
        labelBufferSize.grid(row=4,column=0,padx=2,pady=5,sticky='e')
        dropdownBufferSize.grid(row=4, column=1, padx=5, pady=5)
        self._buttonConfirmSettings.grid(row=5,column=0, columnspan=2, padx=10, pady=5)
        labelLoadFile.grid(row=6,column=0,columnspan=2,padx=10,pady=10,sticky='w')
        buttonFileDialog.grid(row=7, column= 0, padx=10,pady=5)
        self._entryFilePath.grid(row=7,column=1,padx=5,pady=5,sticky='ew')
        self._buttonConfirmFileSelection.grid(row=8,column=0,columnspan=2,padx=10,pady=5)

    # funkcia, ktorá otvára okno explorera pre vyhladávanie .wav súborov | function opening explorer window searching for .wav files
    def _openFileDialog(self):
        filename = filedialog.askopenfilename(initialdir='/',filetypes=[('wav file', '*.wav')], title='Select file')
        help.unlockWidget(self._entryFilePath)
        self._entryFilePath.delete(0,'end')
        self._entryFilePath.insert(0,filename)
        help.readonlyWidget(self._entryFilePath)
        if(len(self._entryFilePath.get())>0):
            help.unlockWidget(self._buttonConfirmFileSelection)
        else:
            help.lockWidget(self._buttonConfirmFileSelection)

    # zbalí nastavenia session a cez destroyItself funkciu ich odošle ako parameter do funkcie rodiča
    # packs session settings and sends them as parameter to parent function through destroyItself function
    def _sendSettings(self):
        packedVariables = dict(filePath=None,deviceID=self._deviceList[self._selectedDevice.get()],sampleRate=int(self._selectedSampleRate.get()),windowLength=int(self._selectedWindowLength.get()),bufferSize=int(self._selectedBufferSize.get()),streamMode=None)
        self._destroyItself(packedVariables)

    # cez destroyItself funkciu odošle cestu k vybranému súboru do funkcie rodiča
    # send path to selected file as parameter to parent function through destroyItself function
    def _sendFilePath(self):
        packedVariables=dict(filePath=self._entryFilePath.get(),deviceID=None,sampleRate=None,windowLength=int(self._selectedWindowLength.get()),bufferSize=None,streamMode=False)
        self._destroyItself(packedVariables)

    # funkcia, ktorá vymaže SettingsGUI frame z hlavného okna a zavolá funkciu rodiča, ktorá vytvorí frame s ovládacím panelom session
    # function that deletes SettingsGUI frame from main window and calls parent function, which creates frame with session control panel
    def _destroyItself(self, packedVariables):
        self._frame.grid_forget()
        self._frame.destroy()
        self._parent.createSessionControls(self._master, packedVariables)