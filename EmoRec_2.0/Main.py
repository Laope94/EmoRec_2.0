class Main(object):
    import tkinter as tk
    from InputController import InputController
    from HelperFunctions import HelperFunctions as help
    from SessionSettings import SessionSettings
    from SessionControls import SessionControls

    def main(self):
        self.masterWindow = self.tk.Tk()
        self.masterWindow.resizable(False,False)
        self.createSessionSettings(self.masterWindow)
        self.masterWindow.mainloop()

    def createSessionSettings(self,master):
        self.SessionSettings(self,master,self.InputController().getDeviceList())

    def createSessionControls(self,master,filepath,packedVariables):
        self.SessionControls(self,master,filepath,packedVariables, self.InputController())

if __name__ == '__main__':
    Main().main()