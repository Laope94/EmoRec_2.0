class SessionSettings(object):
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import font
    from HelperFunctions import HelperFunctions as help

    def __init__(self, parent, master, deviceList):
        self.parent = parent
        self.master = master
        self.master.title('EmoRec 2.0 - Nová session')
        self.deviceList = deviceList
        self.frame = self.tk.Frame(self.master)
        self.frame.grid(column=0,row=0, sticky='nwes', padx=10,pady=10)

        #widgets initialization
        self.labelNewSession = self.tk.Label(self.frame,text='Nová session', font=('',15,'bold'))

        self.buttonConfirmSettings = self.tk.Button(self.frame, text='Začať session', state='disabled', command=self.sendPackedSettings)
        self.buttonConfirmSettings.config(width=20,height=2)

        self.labelDevice = self.tk.Label(self.frame,text='Výber vstupného zariadenia :')
        self.selectedDevice = self.tk.StringVar(self.master)
        self.selectedDevice.set('-------------------- žiadne --------------------')
        self.dropdownDeviceSelection = self.tk.OptionMenu(self.frame,self.selectedDevice,*self.deviceList.keys(), command=lambda widget : self.help.unlockWidget(self.buttonConfirmSettings))
        self.dropdownDeviceSelection.config(relief='sunken', borderwidth=0.5, background='white', activebackground='white', width=100)

        self.labelSampleRate = self.tk.Label(self.frame,text='Výber vzorkovacej frekvencie (Hz) :')
        self.selectedSampleRate = self.tk.StringVar(self.master)
        self.selectedSampleRate.set('48000')
        self.dropdownSampleRate = self.tk.OptionMenu(self.frame,self.selectedSampleRate,*('44100','48000','64000','88200','96000'))
        self.dropdownSampleRate.config(relief='sunken', borderwidth=0.5, background='white', activebackground='white', width=100)

        self.labelWindowLength = self.tk.Label(self.frame,text='Výber dĺžky vyhodnocovacieho okna (s) :')
        self.selectedWindowLength = self.tk.StringVar(self.master)
        self.selectedWindowLength.set('2')
        self.dropdownWindowLength = self.tk.OptionMenu(self.frame,self.selectedWindowLength,*('2','3','4','5','6','7','8','9','10'))
        self.dropdownWindowLength.config(relief='sunken', borderwidth=0.5, background='white', activebackground='white', width=100)

        self.labelLoadFile = self.tk.Label(self.frame,text='Načítať zo súboru', font=('',15,'bold'))
        self.entryFilePath = self.tk.Entry(self.frame, state='readonly')
        self.entryFilePath.config(readonlybackground='white')
        self.buttonFileDialog = self.tk.Button(self.frame,text="Nájsť súbor", command=self.openFileDialog)

        self.buttonConfirmFileSelection = self.tk.Button(self.frame,text='Analyzovať súbor', state='disabled', command=self.sendFilePath)
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

    def sendPackedSettings(self):
        self.packedVariables = dict()
        self.packedVariables['deviceID'] = self.help.getValueByKey(self.deviceList,self.selectedDevice.get())
        self.packedVariables['sampleRate'] = int(self.selectedSampleRate.get())
        self.packedVariables['windowLength'] = int(self.selectedWindowLength.get())
        self.destroyItself(None, self.packedVariables)

    def sendFilePath(self):
        self.destroyItself(self.entryFilePath.get(),None)
  
    def destroyItself(self, filepath, packedVariables):
        self.frame.grid_forget()
        self.frame.destroy()
        self.parent.createSessionControls(self.master, filepath, packedVariables)

    def openFileDialog(self):
        filename = self.filedialog.askopenfilename(initialdir='/',filetypes=[('Wav file', '*.wav')], title='Výber súboru')
        self.help.unlockWidget(self.entryFilePath)
        self.entryFilePath.delete(0,'end')
        self.entryFilePath.insert(0,filename)
        self.help.readonlyWidget(self.entryFilePath)
        if(len(self.entryFilePath.get())>0):
            self.help.unlockWidget(self.buttonConfirmFileSelection)
        else:
            self.help.lockWidget(self.buttonConfirmFileSelection)
