# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

import sounddevice as sd # https://python-sounddevice.readthedocs.io/en/0.3.14/
import queue
from threading import Thread

# táto trieda obsahuje funkcie, ktoré ovládajú vstupné zariadenia a prúd údajov z nich
# this class contains functions controlling input devices and data streams
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
    def startStream(self, deviceID, samplerate, windowLength, bufferSize, dataGrabber):
        self.streamWorkerThread = Thread(target = self.__startStreamWorker, args=(deviceID,samplerate,windowLength,bufferSize,dataGrabber))
        self.streamWorkerThread.start()
        self.runningWorker = True
    
    # funkcia, ktorá otvára stream, nedoporučuje sa volať priamo, pretože blokuje mainloop, volá sa cez startStream()
    # function opening data stream, not advised to call directly since it's blocking mainloop, call startStream() instead
    def __startStreamWorker(self, deviceID, samplerate,windowLength,bufferSize,dataGrabber):
        self.streamWorker = self.StreamWorker(deviceID,samplerate,windowLength,bufferSize,dataGrabber)
        self.streamWorker.run()

    # funkcia, ktorá zastavuje workera a zároveň zastavuje vlákno na ktorom worker beží | function that that stops worker and thread that runs worker
    def streamStop(self):
        self.streamWorker.terminate()
        self.streamWorkerThread.join()
        
    # trieda StreamWorker je vnorená trieda InputController a stará sa o vytváranie a zatváranie prúdu údajov
    # class StreamWorker is nested class of InputController and it handles creating and closing data stream 
    class StreamWorker(object):

        def __init__(self, deviceID, samplerate, windowLength, bufferSize, dataGrabber):
            self.isRunning = True # flag, ktorý určuje či má worker stále bežať | flag that determines if is worker supposed to stay in running state
            self.deviceID = deviceID
            self.samplerate = samplerate # určuje počet vzoriek za sekundu | determines samples per second
            self.dataGrabber = dataGrabber  # funkcia definovaná v inej triede, slúži na pravidelné odosielanie dát zo streamu do GUI | function defined in some other class, generally serves for sending data from stream to GUI regulary
            self.windowLength = windowLength # dĺžka okna v sekundách
            self.bufferSize = bufferSize # veľkosť buffera ovládača zariadenia | size of device driver buffer
            self.dataBuffer = self.DataBuffer(self.samplerate,self.windowLength)

        # nastavuje isRunning flag na False a tým dôjde k zastaveniu workera | sets isRunning flag to False which stops the worker
        def terminate(self):
            self.isRunning = False

        def run(self):
            # otvára prúd údajov zo zariadenia s daným ID a so zadanou vzorkovacou frekvenciou, zatial nie je možné používať viacero vstupných kanálov naraz (channels = 1)
            # opens data stream from device with given ID and with given sample rate, it's not possible to use multiple input channels at once yet (channels = 1)
            with sd.InputStream(samplerate=self.samplerate,channels=1,device=self.deviceID, blocksize=self.bufferSize, callback=self.__dataToQueue): 
                while self.isRunning:
                    if(self.dataBuffer.pushToFrame()):
                        if(self.dataBuffer.isDataBufferFull()):
                            self.dataBuffer.removeFirstFrame()
                        self.sendDataThread = Thread(target = self.dataGrabber, args=(self.dataBuffer.getAllFrames(),)) # posiela dáta do dataGrabber funkcie | sends data to dataGrabber function
                        self.sendDataThread.start()
                        
        # callback funkcia, ktorá priebežne ukladá dáta z prúdu do queue | callback function constantly saving data from stream to queue
        def __dataToQueue(self,indata,frames,time,status):
            if(status):
                print(status)
            self.dataBuffer.pushToQueue(indata.copy())

        # vnorená trieda workera, ktorá sa stará o bufferovanie údajov, ktoré prichádzajú zo streamu s ohľadom na výkon
        # nested class of worker that takes care of buffering data incoming from stream and also takes concern of performance
        class DataBuffer(object):
            def __init__(self, sampleRate, windowLength):
                self.frameLength = sampleRate*windowLength
                self.q = queue.Queue()
                self.frame = []
                self.dataBuffer = []
                # vysvetlenie
                # Queue je velmi rýchla FIFO štruktúra, ale neumožňuje žiadne užitočné operácie s dátami, vhodná na pravidelné a rýchle získavanie údajov z buffera ovládača
                # vynechanie Queue z procesu bufferovania vedie k velkej vyťaženosti CPU
                # frame je krátky list do ktorého sa presúva Queue vždy keď sa naplní vzorkami z buffera ovládača, uchováva vzorky od 2 do 10 sekúnd podla nastavenia, potom sa presúva do ďalšieho buffera
                # dataBuffer je list uchovávajúci posledných 5 framov
                # explanation
                # Queue is very fast FIFO structure, but it doesn't allow any useful operations with data, it's suitable for regular and quick grabbing of data from driver buffer
                # leaving Queue out of buffering proces results in hughe CPU usage
                # frame is short list, which takes data from Queue everytime when Queue is fully filled with samples from driver buffer, it stores samples equal to 2 to 10 seconds deppending on setting, after filling is moved to next buffer
                # dataBuffer is list containing last 5 frames
            
            # vloží dáta do queue | inserts data to queue
            def pushToQueue(self,data):
                self.q.put(data)

            def pushToFrame(self):
                self.frame.extend(self.q.get()) # dáta z queue do framu | data from queue to frame
                if(len(self.frame)>self.frameLength): # ak frame prekročí velkosť | if frame overflows size limit
                    self.__pushToBuffer() # presúva sa do dataBuffera | moves to dataBuffer
                    del self.frame[0:self.frameLength] # maže sa počet vzoriek zodpovedajúci limitu, pretečený zvyšok sa stáva začiatkom nového framu | deletes number of samples equal to frame limit, the rest becomes beginning of new frame
                    return True # vracia True ak došlo k získaniu celého framu | returns True if whole new frame was gained
                else: 
                    return False # vracia False ak počet vzoriek nie je dostatočný na kompletný frame | returns False if number of samples are not enough for complete frame

            def __pushToBuffer(self):
                self.dataBuffer.extend(self.frame[0:self.frameLength])

            # odstraňuje prvý frame z buffera | removes first frame from buffer
            def removeFirstFrame(self):
                del self.dataBuffer[0:self.frameLength]
            
            # vráti posledný frame z buffera | returns last frame of buffer
            def getLastFrame(self):
                return self.dataBuffer[-self.frameLength]

            # vráti celý buffer | returns whole buffer
            def getAllFrames(self):
                return self.dataBuffer

            # vracia True ak buffer prekročil počet maximálny počet framov | returns True if buffer exceeds maximum number of frames
            def isDataBufferFull(self):
                if(len(self.dataBuffer)>5*self.frameLength):
                    return True
                else:
                    return False
