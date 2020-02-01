# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

import sounddevice as sd # https://python-sounddevice.readthedocs.io/en/0.3.14/
import queue
import numpy as np
from threading import Thread

# táto trieda obsahuje funkcie, ktoré ovládajú vstupné zariadenia a prúd údajov z nich
# this class containst functions controlling input devices and data streams
class InputController(object):
    
    # funkcia vráti slovník obsahujúci údaje o vstupných zariadeniach a ich ID (ID je nutné pre otvorenie prúdu údajov)
    # function returns dictionary containing information about input devices and their ID's (ID is required for opening data stream)
    def getDeviceList(self):
        deviceQueryResult = sd.query_devices() # získa zoznam zariadení | get device list
        hostapiQueryResult = sd.query_hostapis() # získa zoznam hostapi | get hostapi list (WME, ASIO, WASAPI...)
        deviceList = dict() 
        for i in range(len(deviceQueryResult)):
            if(deviceQueryResult[i]['max_input_channels']>0): # zariadenia bez vstupných kanálov sú ignorované | devices without input channels are ignored
                deviceList["" + deviceQueryResult[i]["name"] + 
                           ", " + hostapiQueryResult[deviceQueryResult[i]["hostapi"]]["name"] + 
                           ", (in: " + str(deviceQueryResult[i]["max_input_channels"]) +
                           ", out: " + str(deviceQueryResult[i]["max_output_channels"]) + ")" +
                           ", " + str(deviceQueryResult[i]["default_samplerate"]) + " Khz"] = i
        # klúč: (názov zariadenia, hostapi, počet vstupných a výstupných kanálov, predvolená vzorkovacia frekvencia) ; hodnota: ID zariadenia
        # key: (name of device, hostapi, number of input and output channels, default sample rate) ; value: device ID
        return deviceList

    # funkcia vytvárajúca vlákno pre funkciu, ktorá otvára stream - zabraňuje zamrznutiu GUI
    # poznámka k parametru dataGrabber - parameter obsahuje referenciu na dataGrabber funkciu, ktorá by sa mala nachádzať v triede vytvárajúcej GUI, v prípade, že GUI sa bude updatovať na základe dát zo streamu
    # function creates thread for function that opens stream - prevents GUI from freezing
    # note to dataGrabber parameter - parameter should contain reference to dataGrabber function, which should be defined in GUI creating class in case that GUI needs to be regulary updated with data from stream
    def startStream(self, deviceID, samplerate, dataGrabber):
        self.streamWorkerThread = Thread(target = self.__startStreamWorker, args=(deviceID,samplerate,dataGrabber))
        self.streamWorkerThread.start()
        self.runningWorker = True
    
    # funkcia, ktorá otvára stream, nedoporučuje sa volať priamo, pretože blokuje mainloop, volá sa cez startStream()
    # function opening data stream, not advised to call directly since it's blocking mainloop, call startStream() instead
    def __startStreamWorker(self, deviceID, samplerate, dataGrabber):
        self.streamWorker = self.StreamWorker(deviceID,samplerate,dataGrabber)
        self.streamWorker.run()

    # funkcia, ktorá zastavuje workera a zároveň zastavuje vlákno na ktorom worker beží
    # function that that stops worker and thread that runs worker
    def streamStop(self):
        self.streamWorker.terminate()
        self.streamWorkerThread.join()
        
    # trieda StreamWorker je vnorená trieda InputController a stará sa o vytváranie a zatváranie prúdu údajov
    # # class StreamWorker is nested class of InputController and it handles creating and closing data stream 
    class StreamWorker(object):

        def __init__(self, deviceID, samplerate, dataGrabber):
            self.isRunning = True
            self.deviceID = deviceID
            self.samplerate = samplerate
            self.dataGrabber = dataGrabber

            # mechanizmus bufferovania - queue je FIFO štruktúra, ktorú tento program používa na krátkodobé uchovávanie malého množstva údajov zo streamu
            # dataBuffer je pole, do ktorého sa pridá blok údajov z queue ak je queue plná
            # mechanism of buffering - queue is FIFO structure, in this program it's used for short-therm saving of small amount of data from stream
            # dataBuffer is array, if queue is full, block of data is appended to array 
            #self.q = queue.Queue()
            self.dataBuffer = self.DataBuffer(self.samplerate,2)

        def terminate(self):
            self.isRunning = False

        def run(self):
            # otvára prúd údajov zo zariadenia s daným ID a so zadanou vzorkovacou frekvenciou
            # zatial nie je možné používať viacero vstupných kanálov naraz (channels = 1)
            # opens data stream from device with given ID and with given sample rate
            # it's not possible to use multiple input channels at once (channels = 1)
            with sd.InputStream(samplerate=self.samplerate,channels=1,device=self.deviceID, blocksize=1024, callback=self.__dataToQueue): 
                while self.isRunning:
                    if(self.dataBuffer.pushToFrame()): # ak sa buffer naplní do určitej veľkosti | if buffers fills with certain amount of data
                        if(self.dataBuffer.isDataBufferFull()):
                            self.dataBuffer.removeFirstFrame()
                        self.sendDataThread = Thread(target = self.dataGrabber, args=(self.dataBuffer.getAllFrames(),)) # posiela dáta do dataGrabber funkcie | sends data to dataGrabber function
                        self.sendDataThread.start()
                        

        # callback funkcia, ktorá priebežne ukladá dáta z prúdu do queue
        # callback function constantly saving data from stream to queue
        def __dataToQueue(self,indata,frames,time,status):
            if(status):
                print(status)
            self.dataBuffer.pushToQueue(indata.copy())

        class DataBuffer(object):
            def __init__(self, sampleRate, windowLength):
                self.frameLength = sampleRate*windowLength
                self.q = queue.Queue()
                self.frame = []
                self.dataBuffer = []
                
            def pushToQueue(self,data):
                self.q.put(data)

            def pushToFrame(self):
                self.frame.extend(self.q.get())
                if(len(self.frame)>self.frameLength):
                    self.__pushToBuffer()
                    del self.frame[0:self.frameLength]
                    return True
                else: 
                    return False

            def __pushToBuffer(self):
                self.dataBuffer.extend(self.frame[0:self.frameLength])

            def removeFirstFrame(self):
                del self.dataBuffer[0:self.frameLength]

            def getLastFrame(self):
                return self.dataBuffer[-self.frameLength]

            def getAllFrames(self):
                return self.dataBuffer

            def clearBuffer(self):
                self.dataBuffer = []

            def isDataBufferFull(self):
                if(len(self.dataBuffer)>5*self.frameLength):
                    return True
                else:
                    return False
