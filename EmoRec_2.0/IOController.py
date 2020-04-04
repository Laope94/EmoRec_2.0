# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

import sounddevice as sd # https://python-sounddevice.readthedocs.io/en/0.3.14/
import soundfile as sf # https://pysoundfile.readthedocs.io/en/latest/
import numpy as np
import queue
from threading import Thread

# táto trieda obsahuje funkcie, ktoré ovládajú vstupné a výstupné zariadenia a prúd údajov z nich
# this class contains functions controlling input and output devices and data streams
class IOController(object):
    
    # funkcia vráti slovník obsahujúci údaje o vstupných zariadeniach a ich ID (ID je nutné pre otvorenie prúdu údajov)
    # function returns dictionary containing information about input devices and their ID's (ID is required for opening data stream)
    def getDeviceList(self):
        deviceQueryResult = sd.query_devices() # získa zoznam zariadení | get device list
        hostapiQueryResult = sd.query_hostapis() # získa zoznam hostapi | get hostapi list (WME, ASIO, WASAPI...)
        deviceList = dict() 
        for i in range(len(deviceQueryResult)):
            if(deviceQueryResult[i]['max_input_channels']>0): # zariadenia bez vstupných kanálov sú ignorované | devices without input channels are ignored
                # klúč: (názov zariadenia, hostapi, počet vstupných a výstupných kanálov, predvolená vzorkovacia frekvencia) ; hodnota: ID zariadenia
                # key: (name of device, hostapi, number of input and output channels, default sample rate) ; value: device ID
                deviceList["" + deviceQueryResult[i]["name"] + 
                           ", " + hostapiQueryResult[deviceQueryResult[i]["hostapi"]]["name"] + 
                           ", (in: " + str(deviceQueryResult[i]["max_input_channels"]) +
                           ", out: " + str(deviceQueryResult[i]["max_output_channels"]) + ")" +
                           ", " + str(deviceQueryResult[i]["default_samplerate"]) + " Hz"] = i
        return deviceList

    # funkcia vytvárajúca vlákno pre funkciu, ktorá otvára stream - zabraňuje zamrznutiu GUI
    # poznámka k argumentu dataGrabber - mal by obsahovať referenciu na funkciu, ktorá by sa mala nachádzať v triede vytvárajúcej GUI, v prípade, že GUI sa bude updatovať na základe dát zo streamu
    # poznámka k argumentu predictEmotion - mal by obsahovať referenciu na funkciu, ktorá sa v PredictControlleri stará o predikciu emócie
    # function creates thread for function that opens stream - prevents GUI from freezing
    # note to dataGrabber argument - argument should contain reference to function, which should be defined in GUI creating class in case that GUI needs to be regulary updated with data from stream
    # note to predictEmotion argument - argument should contain reference to function, which is defined in PredictionController and takes care of emotion prediction 
    def startStream(self, deviceID, samplerate, windowLength, bufferSize, dataGrabber, predictEmotion):
        self._streamWorkerThread = Thread(target = self._startStreamWorker, args=(deviceID,samplerate,windowLength,bufferSize,dataGrabber,predictEmotion))
        self._streamWorkerThread.start()
    
    # funkcia, ktorá otvára stream, nedoporučuje sa volať priamo, pretože blokuje mainloop, volá sa cez startStream()
    # function opening data stream, not advised to call directly since it's blocking mainloop, call startStream() instead
    def _startStreamWorker(self, deviceID, samplerate,windowLength,bufferSize,dataGrabber,predictEmotion):
        self._streamWorker = self.StreamWorker(deviceID,samplerate,windowLength,bufferSize,dataGrabber,predictEmotion)
        self._streamWorker.run()

    # funkcia, ktorá zastavuje workera a zároveň zastavuje vlákno na ktorom worker beží | function that that stops worker and thread that runs worker
    def streamStop(self):
        self._streamWorker.terminate()
        self._streamWorkerThread.join()

    # funkcia vytvára prehrávač pre súbor so zadanou cestou | function creates player for file with given path
    def createPlayer(self,filePath,windowLength):
        self._player = self.Player(filePath,windowLength)

    # wrapper pre funkciu, ktorá spúšťa prehrávanie | wrapper for function which starts playback
    def startPlayback(self):
        self._player.play()

    # wrapper pre funkciu, ktorá zastavuje prehrávanie | wrapper for function which stops playback
    def stopPlayback(self):
        self._player.stop()

    # wrapper pre funkciu, ktorá z prehrávača vracia vzorkovaciu frekvenciu | wrapper for function which gets sample rate from player
    def getPlayerSampleRate(self):
        return self._player.getSampleRate()

    # wrapper pre funkciu, ktorá z prehrávača vracia načítaný súbor v podobe numpy pola | wrapper for function which gets loaded file from player in form of numpy array
    def getPlayerSamples(self):
        return self._player.getSamples()

    # trieda StreamWorker je vnorená trieda IOController a stará sa o vytváranie a zatváranie prúdu údajov
    # class StreamWorker is nested class of IOController and it handles creating and closing data stream 
    class StreamWorker(object):

        def __init__(self, deviceID, samplerate, windowLength, bufferSize, dataGrabber, predictEmotion):
            self._isRunning = True # flag, ktorý určuje či má worker stále bežať | flag that determines if is worker supposed to stay in running state
            self._deviceID = deviceID
            self._samplerate = samplerate # určuje počet vzoriek za sekundu | determines samples per second
            self._dataGrabber = dataGrabber  # funkcia definovaná v inej triede, slúži na pravidelné odosielanie dát zo streamu do GUI | function defined in some other class, generaly serves for sending data from stream to GUI regulary
            self._predictEmotion = predictEmotion # funkcia definovaná v inej triede, slúži na predikciu emócií | function defined in another class, generaly serves for prediction of emotions
            self._windowLength = windowLength # dĺžka okna v sekundách
            self._bufferSize = bufferSize # veľkosť buffera ovládača zariadenia | size of device driver buffer
            self._dataBuffer = self.DataBuffer(self._samplerate,self._windowLength)

        def run(self):
            # otvára prúd údajov zo zariadenia s daným ID a so zadanou vzorkovacou frekvenciou, zatial nie je možné používať viacero vstupných kanálov naraz (channels = 1)
            # opens data stream from device with given ID and with given sample rate, it's not possible to use multiple input channels at once yet (channels = 1)
            with sd.InputStream(samplerate=self._samplerate,channels=1,device=self._deviceID, blocksize=self._bufferSize, callback=self._dataToQueue): 
                while self._isRunning:
                    if(self._dataBuffer.pushToFrame()):
                        sendDataThread = Thread(target=self._sendData)
                        sendDataThread.start()
                        #sendDataThread.join() # v prípade problémov a mrznutia programu odkomentovať | uncomment if you experience problems and application freezing

        # nastavuje isRunning flag na False a tým dôjde k zastaveniu workera | sets isRunning flag to False which stops the worker
        def terminate(self):
            self._isRunning = False

        # callback funkcia, ktorá priebežne ukladá dáta z prúdu do queue | callback function constantly saving data from stream to queue
        def _dataToQueue(self,indata,frames,time,status):
            if(status):
                print(status)
            self._dataBuffer.pushToQueue(indata.copy())

        # odošle dáta na predikciu a do GUI | sends data to prediction and to GUI
        def _sendData(self):
            predictions = self._predictEmotion(self._dataBuffer.getLastFrame(),self._samplerate,self._windowLength)
            self._dataGrabber(self._dataBuffer.getAllFrames(),predictions)

        # vnorená trieda workera, ktorá sa stará o bufferovanie údajov, ktoré prichádzajú zo streamu s ohľadom na výkon
        # nested class of worker that takes care of buffering data incoming from stream and also takes concern of performance
        class DataBuffer(object):
            def __init__(self, sampleRate, windowLength):
                self._frameLength = sampleRate*windowLength
                self._q = queue.Queue()
                self._frame = []
                self._frameBuffer = []
                # vysvetlenie
                # Queue je velmi rýchla FIFO štruktúra, ale neumožňuje žiadne užitočné operácie s dátami, vhodná na pravidelné a rýchle získavanie údajov z buffera ovládača
                # vynechanie Queue z procesu bufferovania vedie k velkej vyťaženosti CPU
                # frame je krátky list do ktorého sa presúva Queue vždy keď sa naplní vzorkami z buffera ovládača, uchováva vzorky od 2 do 10 sekúnd podla nastavenia, potom sa presúva do ďalšieho buffera
                # frameBuffer je list uchovávajúci posledných 5 framov
                # explanation
                # Queue is very fast FIFO structure, but it doesn't allow any useful operations with data, it's suitable for regular and quick grabbing of data from driver buffer
                # leaving Queue out of buffering proces results in huge CPU usage
                # frame is short list, which takes data from Queue everytime when Queue is fully filled with samples from driver buffer, it stores samples equal to 2 to 10 seconds deppending on setting, after filling is moved to next buffer
                # frameBuffer is list containing last 5 frames
            
            # vloží dáta do queue | inserts data to queue
            def pushToQueue(self,data):
                self._q.put(data)

            # presunie dáta z queue do framu | moves data from queue to frame
            def pushToFrame(self):
                self._frame.extend(self._q.get()) # dáta z queue do framu | data from queue to frame
                if(len(self._frame)>self._frameLength): # ak frame prekročí velkosť | if frame overflows size limit
                    self._pushToBuffer() # presúva sa do dataBuffera | moves to dataBuffer
                    del self._frame[0:self._frameLength] # maže sa počet vzoriek zodpovedajúci limitu, pretečený zvyšok sa stáva začiatkom nového framu | deletes number of samples equal to frame limit, the rest becomes beginning of new frame
                    return True # vracia True ak došlo k získaniu celého framu | returns True if whole new frame was gained
                else: 
                    return False # vracia False ak počet vzoriek nie je dostatočný na kompletný frame | returns False if number of samples are not enough for complete frame

            # vloží frame do buffra | puts frame to buffer
            def _pushToBuffer(self):
                self._frameBuffer.append(self._frame[0:self._frameLength])
                if(self._isDataBufferFull()):
                    self._removeFirstFrame()
            
            # vráti posledný frame z buffera | returns last frame of buffer
            def getLastFrame(self):
                return self._frameBuffer[-1]

            # vráti celý buffer | returns whole buffer
            def getAllFrames(self):
                return np.asarray(self._frameBuffer).ravel()

            # vracia True ak buffer prekročil počet maximálny počet framov | returns True if buffer exceeds maximum number of frames
            def _isDataBufferFull(self):
                if(len(self._frameBuffer)>5):
                    return True
                else:
                    return False

            # odstraňuje prvý frame z buffera | removes first frame from buffer
            def _removeFirstFrame(self):
                del self._frameBuffer[0]

    # trieda Player je vnorená trieda IOControllera, stará sa o spracovanie a prehrávanie načítaného súboru
    # class Player is nested class of IOController and takes care of processing and playback of loaded file
    class Player(object):
        
        # načítanie súboru - ak posledný frame súboru nie je kompletný tak sa k nemu doplnia nuly
        # file load - if last frame of file is not complete it's filled with zeros
        def __init__(self, filePath, windowLength):
            self._data, self._samplerate = sf.read(filePath)
            frameLength = windowLength*self._samplerate
            sampleCount = len(self._data)
            if(sampleCount<frameLength):
                self._data = np.append(self._data,np.zeros((frameLength-sampleCount)))
            if(sampleCount>frameLength):
                self._data = np.append(self._data,np.zeros((frameLength-sampleCount%frameLength)))

        # prehrá súbor, ako výstupné zariadenie je použité defaultné (výber výstupného zariadenia nie je implementovaný)
        # plays file, default output device is used (selection of output device is not implemented)
        def play(self):
            sd.play(self._data,self._samplerate)

        # zastaví prehrávanie | stops playback
        def stop(self):
            sd.stop()

        # vráti vzorkovaciu frekvenciu, ktorá bola automaticky získaná pri načítaní | returns sample rate which was automatically obtained on load
        def getSampleRate(self):
            return self._samplerate

        # vráti načítaný súbor vo forme numpy pola | returns loaded file in form of numpy array
        def getSamples(self):
            return self._data