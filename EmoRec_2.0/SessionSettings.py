# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

import tkinter as tk
from tkinter import filedialog
from tkinter import font
from HelperFunctions import HelperFunctions as help

class SessionSettings(object):
    def __init__(self, parent, master, deviceList):
        self.parent = parent
        self.master = master
        self.master.title('EmoRec 2.0 - Nová session')
        self.deviceList = deviceList
        self.frame = tk.Frame(self.master)
        self.frame.grid(column=0,row=0, sticky='nwes', padx=10,pady=10)

        #widgets initialization
        self.labelNewSession = tk.Label(self.frame,text='Nová session', font=('',15,'bold'))

        self.buttonConfirmSettings = tk.Button(self.frame, text='Začať session', state='disabled', command=self.sendPackedSettings)
        self.buttonConfirmSettings.config(width=20,height=2)

        self.labelDevice = tk.Label(self.frame,text='Výber vstupného zariadenia :')
        self.selectedDevice = tk.StringVar(self.master)
        self.selectedDevice.set('-------------------- žiadne --------------------')
        self.dropdownDeviceSelection = tk.OptionMenu(self.frame,self.selectedDevice,*self.deviceList.keys(), command=lambda widget : help.unlockWidget(self.buttonConfirmSettings))
        self.dropdownDeviceSelection.config(relief='sunken', borderwidth=0.5, background='white', activebackground='white', width=100)

        self.labelSampleRate = tk.Label(self.frame,text='Výber vzorkovacej frekvencie (Hz) :')
        self.selectedSampleRate = tk.StringVar(self.master)
        self.selectedSampleRate.set('48000')
        self.dropdownSampleRate = tk.OptionMenu(self.frame,self.selectedSampleRate,*('44100','48000','64000','88200','96000'))
        self.dropdownSampleRate.config(relief='sunken', borderwidth=0.5, background='white', activebackground='white', width=100)

        self.labelWindowLength = tk.Label(self.frame,text='Výber dĺžky vyhodnocovacieho okna (s) :')
        self.selectedWindowLength = tk.StringVar(self.master)
        self.selectedWindowLength.set('2')
        self.dropdownWindowLength = tk.OptionMenu(self.frame,self.selectedWindowLength,*('2','3','4','5','6','7','8','9','10'))
        self.dropdownWindowLength.config(relief='sunken', borderwidth=0.5, background='white', activebackground='white', width=100)

        self.labelLoadFile = tk.Label(self.frame,text='Načítať zo súboru', font=('',15,'bold'))
        self.entryFilePath = tk.Entry(self.frame, state='readonly')
        self.entryFilePath.config(readonlybackground='white')
        self.buttonFileDialog = tk.Button(self.frame,text="Nájsť súbor", command=self.openFileDialog)

        self.buttonConfirmFileSelection = tk.Button(self.frame,text='Analyzovať súbor', state='disabled', command=self.sendFilePath)
        self.buttonConfirmFileSelection.config(width=20,height=2)

        #grid placement
        self.labelNewSession.grid(row=0,column=0,columnspan=2,padx=10,pady=10,sticky='w')
        self.labelDevice.grid(row=1,column=0,padx=2,pady=5, sticky='e')
        self.dropdownDeviceSelection.grid(row=1, column=1, padx=5, pady=5)
        self.labelSampleRate.grid(row=2,column=0, padx=2, pady=5, sticky='e')
        self.dropdownSampleRate.grid(row=2, column=1, padx=5, pady=5)
        self.labelWindowLength.grid(row=3,column=0,padx=2,pady=5, sticky='e')
        self.dropdownWindowLength.grid(row=3, column=1, padx=5, pady=5)
        self.buttonConfirmSettings.grid(row=4,column=0, columnspan=2, padx=10, pady=5)
        self.labelLoadFile.grid(row=5,column=0,columnspan=2,padx=10,pady=10,sticky='w')
        self.buttonFileDialog.grid(row=6, column= 0, padx=10,pady=5)
        self.entryFilePath.grid(row=6,column=1,padx=5,pady=5,sticky='ew')
        self.buttonConfirmFileSelection.grid(row=7,column=0,columnspan=2,padx=10,pady=5)

    # zbalí nastavenia session a cez destroyItself funkciu ich odošle ako parameter do funkcie rodiča
    # packs session settings and sends them as parameter to parent function through destroyItself function
    def sendPackedSettings(self):
        packedVariables = dict()
        packedVariables['deviceID'] = help.getValueByKey(self.deviceList,self.selectedDevice.get())
        packedVariables['sampleRate'] = int(self.selectedSampleRate.get())
        packedVariables['windowLength'] = int(self.selectedWindowLength.get())
        self.destroyItself(None, packedVariables)

    # cez destroyItself funkciu odošle cestu k vybranému súboru do funkcie rodiča
    # send path to selected file as parameter to parent function through destroyItself function
    def sendFilePath(self):
        self.destroyItself(self.entryFilePath.get(),None)
  
    # funkcia, ktorá vymaže SessionSettings frame z hlavného okna a zavolá funkciu rodiča, ktorá vytvorí frame s ovládacím panelom session
    # function that deletes SessionSettings frame from main window and calls parent function, which creates frame with session control panel
    def destroyItself(self, filepath, packedVariables):
        self.frame.grid_forget()
        self.frame.destroy()
        self.parent.createSessionControls(self.master, filepath, packedVariables)

    # funkcia, ktorá otvára okno explorera pre vyhladávanie .wav súborov | function opening explorer window searching for .wav files
    def openFileDialog(self):
        filename = filedialog.askopenfilename(initialdir='/',filetypes=[('wav file', '*.wav')], title='Výber súboru')
        help.unlockWidget(self.entryFilePath)
        self.entryFilePath.delete(0,'end')
        self.entryFilePath.insert(0,filename)
        help.readonlyWidget(self.entryFilePath)
        if(len(self.entryFilePath.get())>0):
            help.unlockWidget(self.buttonConfirmFileSelection)
        else:
            help.lockWidget(self.buttonConfirmFileSelection)
