class SessionSettings(object):
    import tkinter as tk
    from HelperFunctions import HelperFunctions as help

    def __init__(self, parent, master, deviceList):
        self.parent = parent
        self.master = master
        self.master.title('EmoRec 2.0 - Nová session')
        self.deviceList = deviceList
        self.frame = self.tk.Frame(self.master)
        self.frame.grid(column=0,row=0, sticky='nwes', padx=10,pady=10)

        #widgets initialization
        self.buttonConfirmSettings = self.tk.Button(self.frame, text='OK', state='disabled', command=self.packAndDestroy)
        self.buttonConfirmSettings.config(width=20,height=2)

        self.labelDevice = self.tk.Label(self.frame,text="Výber vstupného zariadenia :")
        self.selectedDevice = self.tk.StringVar(self.master)
        self.selectedDevice.set('-----žiadne-----')
        self.dropdownDeviceSelection = self.tk.OptionMenu(self.frame,self.selectedDevice,*self.deviceList.keys(), command=lambda widget : self.help.unlockWidget(self.buttonConfirmSettings))
        self.dropdownDeviceSelection.config(relief='sunken', borderwidth=0.5, background='white', width=100)

        self.labelSampleRate = self.tk.Label(self.frame,text="Výber vzorkovacej frekvencie (Khz) :")
        self.selectedSampleRate = self.tk.StringVar(self.master)
        self.selectedSampleRate.set('48000')
        self.dropdownSampleRate = self.tk.OptionMenu(self.frame,self.selectedSampleRate,*('44100','48000','96000'))
        self.dropdownSampleRate.config(relief='sunken', borderwidth=0.5, background='white', width=100)

        self.labelWindowLength = self.tk.Label(self.frame,text="Výber dĺžky vyhodnocovacieho okna (s) :")
        self.selectedWindowLength = self.tk.StringVar(self.master)
        self.selectedWindowLength.set('2')
        self.dropdownWindowLength = self.tk.OptionMenu(self.frame,self.selectedWindowLength,*('2','3','4','5','6','7','8'))
        self.dropdownWindowLength.config(relief='sunken', borderwidth=0.5, background='white', width=100)

        #grid placement
        self.labelDevice.grid(row=0,column=0,padx=2,pady=5)
        self.dropdownDeviceSelection.grid(row=0, column=1, padx=5, pady=5)
        self.labelSampleRate.grid(row=1,column=0,padx=2,pady=5)
        self.dropdownSampleRate.grid(row=1, column=1, padx=5, pady=5)
        self.labelWindowLength.grid(row=2,column=0,padx=2,pady=5)
        self.dropdownWindowLength.grid(row=2, column=1, padx=5, pady=5)
        self.buttonConfirmSettings.grid(row=3,column=0, columnspan=2, padx=10, pady=5)

    def packAndDestroy(self):
        print(self.help.getValueByKey(self.deviceList,self.selectedDevice.get()))
        self.frame.grid_forget()
        self.frame.destroy()
        self.parent.createSessionControls(self.master)


