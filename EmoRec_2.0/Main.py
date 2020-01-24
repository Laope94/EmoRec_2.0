class Main(object):
    import tkinter as tk
    from InputController import InputController
    from HelperFunctions import HelperFunctions as help
    from SessionSettings import SessionSettings
    from SessionControls import SessionControls

    def main(self):
        self.masterWindow = self.tk.Tk()
        self.createSessionSettings(self.masterWindow)
        self.masterWindow.mainloop()

    def createSessionSettings(self,master):
        self.SessionSettings(self,master,self.InputController().getDeviceList())

    def createSessionControls(self,master):
        self.SessionControls(self,master)

if __name__ == '__main__':
    Main().main()



