from tkinter import *

def createMainWindow():
    chooseDeviceWindow.destroy()
    window = Tk()

chooseDeviceWindow = Tk()
chooseDeviceWindow.title("EmoRec 2.0 - Výber vstupného zariadenia")
chooseDeviceWindow.minsize(400,300)

mainframe = Frame(chooseDeviceWindow)
mainframe.grid(column=0,row=0, sticky=(N,W,E,S) )
mainframe.columnconfigure(0, weight = 1)
mainframe.rowconfigure(0, weight = 1)
mainframe.pack(pady = 100, padx = 100)

deviceOption = StringVar(chooseDeviceWindow)
deviceOptionList = ("Mic1", "Mic2", "Microphone 3 holy shit long option... fuck my ex, fuck banks, fuck starbucks")
deviceOption.set("Mic1")
deviceMenu = OptionMenu(mainframe,deviceOption, *deviceOptionList)
deviceMenu.grid(row = 2, column =1)

buttonOk = Button(mainframe,text="Ok", command=createMainWindow)
buttonOk.grid(row=3,column=1)

chooseDeviceWindow.mainloop()

