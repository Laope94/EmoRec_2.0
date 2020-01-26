# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

class InputController(object):
    # táto trieda obsahuje funkcie, ktoré ovládajú vstupné zariadenia a prúd údajov z nich
    # this class containst functions controlling input devices and data streams

    import sounddevice as sd # https://python-sounddevice.readthedocs.io/en/0.3.14/
    import queue
    from threading import Thread

    # mechanizmus bufferovania - queue je FIFO štruktúra, ktorú tento program používa na krátkodobé uchovávanie malého množstva údajov zo streamu
    # dataBuffer je pole, do ktorého sa pridá blok údajov z queue ak je queue plná
    # mechanism of buffering - queue is FIFO structure, in this program it's used for short-therm saving of small amount of data from stream
    # dataBuffer is array, if queue is full, block of data is appended to array 
    q = queue.Queue(maxsize=2048)
    dataBuffer = []
   
    # funkcia vráti slovník obsahujúci údaje o vstupných zariadeniach a ich ID (ID je nutné pre otvorenie prúdu údajov)
    # function returns dictionary containing information about input devices and their ID's (ID is required for opening data stream)
    def getDeviceList(self):
        deviceQueryResult = self.sd.query_devices() # získa zoznam zariadení | get device list
        hostapiQueryResult = self.sd.query_hostapis() # získa zoznam hostapi | get hostapi list (WME, ASIO, WASAPI...)
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
        self.streamWorkerThread = self.Thread(target = self.__startStreamWorker, args=(deviceID,samplerate,dataGrabber))
        self.streamWorkerThread.start()
        #return self.streamWorkerThread
    
    # funkcia, ktorá otvára stream, nedoporučuje sa volať priamo, pretože blokuje mainloop, volá sa cez startStream()
    # function, opening data stream, not advised to call directly since it's blocking mainloop, call startStream() instead
    def __startStreamWorker(self, deviceID, samplerate, dataGrabber):
        # otvára prúd údajov zo zariadenia s daným ID a so zadanou vzorkovacou frekvenciou
        # zatial nie je možné používať viacero vstupných kanálov naraz (channels = 1)
        # opens data stream from device with given ID and with given sample rate
        # it's not possible to use multiple input channels at once (channels = 1)
        with self.sd.InputStream(samplerate=samplerate,channels=1,device=deviceID, callback=self.dataToQueue): 
            while True:
                self.dataBuffer.append(self.q.get()) # pridá dáta z queue do buffera | adds data from queue to buffer
                if(len(self.dataBuffer)==100): # ak sa buffer naplní do určitej veľkosti | if buffers fills with certain amount of data
                    self.sendDataThread = self.Thread(target = dataGrabber, args=(self.dataBuffer,)) # posiela dáta do dataGrabber funkcie | sends data to dataGrabber function
                    self.sendDataThread.start()
                    self.dataBuffer=[] # vyprázdni buffer | empties buffer

    # callback funkcia, ktorá priebežne ukladá dáta z prúdu do queue
    # callback function constantly saving data from stream to queue
    def dataToQueue(self,indata,frames,time,status):
        if(status):
            print(status)
        self.q.put(indata.copy())