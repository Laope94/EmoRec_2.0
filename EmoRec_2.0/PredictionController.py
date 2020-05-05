# Real Time klasifikácia emocionálneho stavu z reči | Real Time Classification of Emotional States from Speech
# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Autor | Author : Bc. Timotej Sulka
# Školitel | Supervisor: PaedDr. Martin Magdin Ph.D.

import os
import csv
import time
import pickle
import numpy as np
import librosa # https://librosa.github.io/librosa/index.html
import tensorflow as tf # https://www.tensorflow.org
from keras import backend # https://keras.io/applications/
from keras.models import load_model, Sequential
from scipy.interpolate import interp1d # https://docs.scipy.org/doc/scipy/reference/

# táto trieda obsahuje funkcie pre spracovanie údajov, neurónovú sieť a uchovávanie histórie predikcií
# this class contains functions for data processing, neural network and logging prediction history
class PredictionController(object):
    
    def __init__(self):
        self._classifier = load_model(os.path.join('model', 'mfcc_1dconvolution_model.h5')) # načítanie modelu | model load
        self._classifier._make_predict_function() # 
        self._session = backend.get_session()     # táto časť finalizuje model, model sa stane readonly a threadsafe (predikcia môže byť volaná zo samostatného vlákna)
        self._graph = tf.get_default_graph()      # this part finalizes model, model becomes readonly and threadsafe (prediction can be called from separate thread)
        self._graph.finalize()                    # 
        
        # prvá predikcia trvá vždy velmi dlho, preto sa nevykoná na reálnych dátach ale pri štarte programu naprázdno na matici so samými nulami
        # first prediction always takes too long, it's not good to run first prediction on real data, therefore it first run is done at program start with all zero matrix
        self._classifier.predict(np.zeros((1,256,15)))
        self._n_mfcc = 13 # počet mfcc charakteristík | number of mfcc characteristics
        self._n_fft = 800 #  dĺžka FFT okna | length of FFT window
        self._hop_length = 400 # počet vzoriek medzi za sebou idúcimi rámcami | number of samples between successive frames
        self._a = librosa.db_to_amplitude(60, ref=0.00002) # parameter pre normalizáciu hlasitosti | parameter for volume normalization
        self._logger = self.Logger()
        with open(os.path.join('data', 'scaling_parameters.data'), 'rb') as f:
            self._min = pickle.load(f) # načítanie parametrov na škálovanie mfcc medzi 0 a 1, parametre boli určené v predspracovaní RAVDESS datasetu
            self._max = pickle.load(f) # parameters required for scaling mfcc between 0 and 1, paramteres were determined during RAVDESS dataset preprocess

    # funkcia sa použije na predikciu ak je otvorený prúd údajov zo vstupného zariadenia, wrapper pre _predictEmotion() funkciu
    # function is used for prediction if data stream from input device is opened, wrapper for _predictEmotion() function
    def predictFromStream(self,data,samplerate,windowLength): 
        self._predictEmotion(np.array(data).ravel(),samplerate,windowLength)
        return self._logger.getLastEmotions()

    # funkcia sa použije na predikciu ak je vstupom .wav súbor, wrapper pre _predictEmotion() funkciu
    # function is used for prediction if .wav file is input, wrapper for _predictEmotion() function
    def predictFromFile(self,data,samplerate,windowLength):
        self._logger.clearLogger()
        for d in self._splitData(data,samplerate,windowLength):
            self._predictEmotion(d,samplerate,windowLength)
        return self._logger.getAllEmotions()

    # funkcia, ktorá vykonáva predikciu, nemala by sa volať priamo, iba cez jeden z wrapperov vyššie
    # function making predictions, it should not be called directly, use above wrappers instead
    def _predictEmotion(self,data,samplerate,windowLength):
        if(self._isSilence(data)):
            self._logger.logPrediction(7,windowLength)
        else:
            with self._session.as_default():
                with self._graph.as_default():
                    prediction = self._classifier.predict(self._preprocessData(data,samplerate))
                    self._logger.logPrediction(np.argmax(prediction,axis=1)[0],windowLength) # predikcia sa zaloguje | prediction is logged

    # funkcia, ktorá rozdeluje vstupné údaje na jednotlivé framy ak je vstupom .wav súbor
    # function splits input data to frames if .wav file is input
    def _splitData(self,data,samplerate,windowLength):
        frameLength = windowLength*samplerate
        _data = []
        for f in range(int(len(data)/frameLength)):
            _data.append(data[f*frameLength:((f+1)*frameLength)])
        return _data

    # funkcia pripravuje dáta do formy, ktorú potrebuje model na predikciu
    # function prepares data to form required for prediction by model
    def _preprocessData(self,data,samplerate):
        _data,index = librosa.effects.trim(y=data, top_db=28, frame_length=8, hop_length=2) # orezanie ticha | silence trimming
        _data = _data*(self._a / np.mean(librosa.feature.rms(y=_data))) # normalizácia na hlasitosť 60 db | normalization to volume 60 db
        mfcc = librosa.feature.mfcc(_data, samplerate, n_fft=self._n_fft, hop_length=self._hop_length, n_mfcc=self._n_mfcc) # výpočet 13 mfcc charakteristík | 13 mfcc calculation
        zerocrossing = librosa.feature.zero_crossing_rate(y=_data, hop_length=self._hop_length,frame_length=self._n_fft) # k 13 mfcc charakteristikám sa pridáva zerocrossing a energia ako 14 a 15 charakteristika
        energy = librosa.feature.rms(y=_data,hop_length=self._hop_length,frame_length=self._n_fft)                       # zerocrossing and energy is added to 13 mfcc as 14th and 15th characteristic
        
        # interpolácia - matica s charakteristikami môže mať rozmer 15 x N kde N závisí od dĺžky vstupu, interpolácia charakteristík upravuje maticu na fixnú velkosť 15 x 256 
        # interpolation - matrix with characteristics can have shape of 15 X N where N is determined by length of ipnut, interpolation of characteristics adjusts matrix to fixed length 15 x 256
        interpolatedFeatures = []
        for n in range(self._n_mfcc):
            interpolatedFeatures.append(interp1d(np.arange(mfcc[n,:].size),mfcc[n,:], kind='cubic')(np.linspace(0,mfcc[n,:].size-1,256)))
        interpolatedFeatures.append(interp1d(np.arange(zerocrossing[0,:].size),zerocrossing[0,:], kind='cubic')(np.linspace(0,zerocrossing[0,:].size-1,256)))
        interpolatedFeatures.append(interp1d(np.arange(energy[0,:].size),energy[0,:], kind='cubic')(np.linspace(0,energy[0,:].size-1,256)))
        interpolatedFeatures = np.array(interpolatedFeatures)
        
        # škálovanie charakteristík medzi 0 a 1
        # scaling characteristics between 0 a 1
        for n in range(self._n_mfcc+2):
            interpolatedFeatures[n,:] = (interpolatedFeatures[n,:]-self._min[n])/(self._max[n]-self._min[n])
        
        # transponovanie - model vyžaduje vstup v opačnom tvare ako je výstup z librosy
        # transposition - model requires input to be in opposite shape as output provided by librosa
        interpolatedFeatures = interpolatedFeatures.transpose()
        interpolatedFeatures = np.expand_dims(interpolatedFeatures,axis=0)
        return interpolatedFeatures

    # ak vstup nedosiahol úroveň aspoň -20dB je považovaný za ticho
    # input is considered silence if it hasn't reached volume level at least -20dB
    def _isSilence(self,data):
        if(np.max(librosa.amplitude_to_db(data))>=-20):
            return False
        else: 
            return True

    # wrapper pre funkciu, ktorá resetuje logger
    # wrapper for function reseting looger
    def clearLogger(self):
        self._logger.clearLogger()

    # wrapper pre funckiu, ktorá vráti všetky záznamy v loggeri
    # wrapper for function returning all logger records
    def getLog(self):
        return self._logger.getLog()

    # wrapper pre funkciu, ktorá uloží log do csv
    # wrapper for function saving log to csv
    def saveCSV(self,path):
        return self._logger.saveCSV(path)

    # vnorená trieda PredictionControllera, uchováva históriu predikcií a časovú informáciu
    # nested class of PredictionController, it stores history of predictions and information about time
    class Logger(object):
        def __init__(self):
            self._sessionSeconds=0 # sekundy, ktoré uplynuli od začiatku určovania | seconds from beginning of predictions
            self._shortTermLog = [] # uchováva iba posledných 5 predikcií v jednoduchej forme | stores only last 5 predictions in simple form
            self._longTermLog = [] # uchováva všetky predikcie a k nim informáciu o čase, pozri vnorenú triedu LogRecord | stores all predictions and time informations, see nested class LogRecord
            # poznámka: funkcie logPrediction() a getLastEmotions() je možné zjednodušiť tak aby shortTermLog nebol potrebný
            # shortTermLog existuje, pretože LogRecord pôvodne nemal mať funkciu getEmotion()
            # note: it's possible to simplify functions logPrediction() and getLastEmotions() in way that shortTermLog is not needed at all
            # shortTermLog only exists because LogRecord originally wasn't supposed to have getEmotion() function

        # uloží predikciu do logu v jednoduchej aj zložitej forme | stores prediction into log in simple and also complex form
        def logPrediction(self,prediction,windowLength):
            self._shortTermLog.append(prediction)
            if(len(self._shortTermLog)>5):
                del self._shortTermLog[0]
            self._longTermLog.append(self.LogRecord(self._sessionSeconds,self._sessionSeconds+windowLength,prediction))
            self._sessionSeconds = self._sessionSeconds+windowLength

        # vráti krátkodobý log, ak je v logu menej ako 5 záznamov tak sa doplní nulami (ticho) 
        # returns short term log, if log contains less than 5 records rest is filled with zeroes (silence)
        def getLastEmotions(self):
            emotions = np.array(self._shortTermLog)
            if(len(self._shortTermLog)<5):
                filler = np.empty((5-len(self._shortTermLog),))
                filler[:] = np.NaN
                emotions = np.concatenate((emotions,filler),axis=0)
            return np.expand_dims(emotions,axis=0)

        # vráti jednoduchú formu všetkých záznamov v logu | returns simple form of all records in log
        def getAllEmotions(self):
            emotions = []
            for r in self._longTermLog:
                emotions.append(r.getEmotion())
            return emotions

        # vráti komplexnú formu všetkých záznamov v logu | returns complex form of all log records
        def getLog(self):
            log = ''
            for r in self._longTermLog:
                log = log + r.toString()
            return log

        # uloží log do CSV | saves log to CSV file
        def saveCSV(self,path):
            with open(path,'w',newline='') as logFile:
                csvWriter = csv.writer(logFile,delimiter=';')
                csvWriter.writerow(['start','end','emotion'])
                for r in self._longTermLog:
                    csvWriter.writerow(r.toCSV())

        # resetuje čas a vymaže záznamy loggera | resets time and deletes records in logger
        def clearLogger(self):
            self._sessionSeconds=0
            self._shortTermLog = []
            self._longTermLog = []

        # vnorená trieda Loggera, poskytuje štruktúru pre komplexný záznam v logu
        # nested class of Logger, it provides structure for complex record in log
        class LogRecord(object):
            def __init__(self,startTime,endTime,emotion):
                self._startTime = startTime
                self._endTime = endTime
                self._emotion = emotion
            
            # vráti predikovanú emóciu bez časového údaja | returns predicted emotion without time information
            def getEmotion(self):
                return self._emotion

            # vráti kompletný záznam vo forme reťazca s informáciou o určenej emócií a trvaní v čase | returns complete record in form of string with information about predicted emotion and time duration
            def toString(self):
                emotionList = ['anger','disgust','fear','happiness','neutral','sadness','surprise','silence']
                record = time.strftime('%H:%M:%S', time.gmtime(self._startTime)) + ' - ' + time.strftime('%H:%M:%S', time.gmtime(self._endTime))+ ' -- ' + emotionList[self._emotion]+'\n'
                return record

            # vráti záznam vo forme pola | returns record in form of array
            def toCSV(self):
                record = []
                emotionList = ['anger','disgust','fear','happiness','neutral','sadness','surprise','silence']
                record.append(time.strftime('%H:%M:%S', time.gmtime(self._startTime)))
                record.append(time.strftime('%H:%M:%S', time.gmtime(self._endTime)))
                record.append(emotionList[self._emotion])
                return record