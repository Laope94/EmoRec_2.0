class SessionControls(object):
    import tkinter as tk

    def __init__(self, parent, master):
        self.master = master
        self.parent = parent
        self.master.title('EmoRec 2.0 - Session')
        self.frame = self.tk.Frame(self.master)
        self.frame.grid(column=0,row=0, sticky='nwes', padx=10,pady=10)

        #widgets initialization
        self.buttonSettings = self.tk.Button(self.frame, text='Nastavenia', command=self.packAndDestroy)
        self.buttonSettings.config(width=20,height=2)

        #grid placement
        self.buttonSettings.grid(row=0, column=0, padx=10, pady=5)

    def packAndDestroy(self):
        self.frame.grid_forget()
        self.frame.destroy()
        self.parent.createSessionSettings(self.master)

