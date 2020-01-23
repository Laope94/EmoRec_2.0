from tkinter import *
from InputController import InputController
from HelperFunctions import HelperFunctions as help

def createMainWindow():
    print(deviceList[deviceOption.get()])
    chooseDeviceWindow.destroy()
    window = Tk()

chooseDeviceWindow = Tk()
chooseDeviceWindow.title('EmoRec 2.0 - Výber vstupného zariadenia')
chooseDeviceWindow.minsize(400,300)

mainframe = Frame(chooseDeviceWindow)
mainframe.grid(column=0,row=0, sticky=(N,W,E,S) )
mainframe.columnconfigure(0, weight = 1)
mainframe.rowconfigure(0, weight = 1)
mainframe.pack(pady = 100, padx = 100)

#-----------------------------------------------------
#---WIDGETS-------------------------------------------
#-----------------------------------------------------
buttonOk = Button(mainframe,text="Ok", state=DISABLED, command=createMainWindow)


deviceOption = StringVar(chooseDeviceWindow)
deviceOption.set('-----žiadne-----')
deviceList = InputController().getDeviceList()
deviceMenu = OptionMenu(mainframe,deviceOption, *deviceList.keys(), command=lambda widget : help.unlockWidget(buttonOk))

#----------------------------------------------------
#---GRID-PLACEMENT-----------------------------------
#----------------------------------------------------
deviceMenu.grid(row = 2, column =1)
buttonOk.grid(row=3,column=1)

chooseDeviceWindow.mainloop()

