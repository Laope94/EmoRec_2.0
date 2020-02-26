import os
import time
import pickle
import numpy as np
import librosa
import tensorflow as tf
from keras import backend
from keras.models import load_model, Sequential
from scipy.interpolate import interp1d

class PredictionController(object):
    def __init__(self):
        self.classifier = load_model(os.path.join('model', 'mfcc_1dconvolution_model.h5'))
        self.classifier._make_predict_function()
        self.session = backend.get_session()
        self.graph = tf.get_default_graph()
        self.graph.finalize()
        self.classifier.predict(np.zeros((1,256,15))) # fake prediction
        self.N_MFCC = 13
        self.N_FFT = 800
        self.HOP_LENGTH = 400
        self.a = librosa.db_to_amplitude(60, ref=0.00002)
        self.logger = self.Logger()
        with open(os.path.join('data', 'scaling_parameters.data'), 'rb') as f:
            self.min = pickle.load(f)
            self.max = pickle.load(f)

    def __predictEmotion(self,data,samplerate,windowLength):
        if(self.isSilence(data)):
            self.logger.logPrediction(7,windowLength)
        else:
            data = self.preprocessData(data,samplerate)
            with self.session.as_default():
                with self.graph.as_default():
                    prediction = self.classifier.predict(data)
                    self.logger.logPrediction(np.argmax(prediction,axis=1)[0],windowLength)

    def predictFromStream(self, data, samplerate, windowLength):
        data = np.array(data).ravel()     
        self.__predictEmotion(data,samplerate,windowLength)
        return self.logger.getLastEmotions()

    def predictFromFile(self,data,samplerate,windowLength):
        self.logger.clearLogger()
        data = self.splitData(data,samplerate,windowLength)
        for i in range(len(data)):
            self.__predictEmotion(data[i],samplerate,windowLength)
        return self.logger.getAllEmotions()

    def splitData(self,data,samplerate,windowLength):
        frameLength = windowLength*samplerate
        sampleCount = len(data)
        if(sampleCount<frameLength):
            data = np.append(data,np.zeros((frameLength-sampleCount)))
        else:
            data = np.append(data,np.zeros((frameLength-sampleCount%frameLength)))
        frames = int(len(data)/frameLength)
        splittedData = []
        for f in range(frames):
            splittedData.append(data[f*frameLength:((f+1)*frameLength)])
        return splittedData
        

    def preprocessData(self, data, samplerate):
        data = data * self.a / np.mean(librosa.feature.rms(y=data))
        data, index = librosa.effects.trim(y=data, top_db=28, frame_length=8, hop_length=2)
        data = data * self.a / np.mean(librosa.feature.rms(y=data))
        mfcc = librosa.feature.mfcc(data, samplerate, n_fft=self.N_FFT, hop_length=self.HOP_LENGTH, n_mfcc=self.N_MFCC)
        zerocrossing = librosa.feature.zero_crossing_rate(y=data, hop_length=self.HOP_LENGTH,frame_length=self.N_FFT)
        energy = librosa.feature.rms(y=data,hop_length=self.HOP_LENGTH,frame_length=self.N_FFT)
        interpolatedFeatures = []
        for n in range(self.N_MFCC):
            interpolatedFeatures.append(interp1d(np.arange(mfcc[n,:].size),mfcc[n,:], kind='cubic')(np.linspace(0,mfcc[n,:].size-1,256)))
        interpolatedFeatures.append(interp1d(np.arange(zerocrossing[0,:].size),zerocrossing[0,:], kind='cubic')(np.linspace(0,zerocrossing[0,:].size-1,256)))
        interpolatedFeatures.append(interp1d(np.arange(energy[0,:].size),energy[0,:], kind='cubic')(np.linspace(0,energy[0,:].size-1,256)))
        interpolatedFeatures = np.array(interpolatedFeatures)
        for n in range(self.N_MFCC+2):
            interpolatedFeatures[n,:] = (interpolatedFeatures[n,:]-self.min[n])/(self.max[n]-self.min[n])
        interpolatedFeatures = interpolatedFeatures.transpose()
        interpolatedFeatures = np.expand_dims(interpolatedFeatures,axis=0)
        return interpolatedFeatures

    def isSilence(self,data):
        if(np.max(librosa.amplitude_to_db(data))>=-20):
            return False
        else: 
            return True

    def clearLogger(self):
        self.logger.clearLogger()

    def getLog(self):
        return self.logger.getLog()

    class Logger(object):
        def __init__(self):
            self.sessionSeconds=0
            self.shortTermLog = []
            self.longTermLog = []

        def logPrediction(self,prediction,windowLength):
            self.shortTermLog.append(prediction)
            if(len(self.shortTermLog)>5):
                del self.shortTermLog[0]
            self.longTermLog.append(self.LogRecord(self.sessionSeconds,self.sessionSeconds+windowLength,prediction))
            self.sessionSeconds = self.sessionSeconds+windowLength

        def getAllEmotions(self):
            emotions = []
            for r in self.longTermLog:
                emotions.append(r.getEmotion())
            return emotions

        def getLastEmotions(self):
            emotions = np.array(self.shortTermLog)
            if(len(self.shortTermLog)<5):
                filler = np.empty((5-len(self.shortTermLog),))
                filler[:] = np.NaN
                emotions = np.concatenate((emotions,filler),axis=0)
            return np.expand_dims(emotions,axis=0)

        def getLog(self):
            log = ''
            for r in self.longTermLog:
                log = log + r.toString()
            return log

        def clearLogger(self):
            self.sessionSeconds=0
            self.shortTermLog = []
            self.longTermLog = []

        class LogRecord(object):
            def __init__(self,startTime,endTime,emotion):
                self.startTime = startTime
                self.endTime = endTime
                self.emotion = emotion

            def getEmotion(self):
                return self.emotion

            def toString(self):
                emotionList = ['hnev','znechutenie','strach','radosť','neutrál','smútok','prekvapenie','ticho']
                record = time.strftime('%H:%M:%S', time.gmtime(self.startTime)) + ' - ' + time.strftime('%H:%M:%S', time.gmtime(self.endTime))+ ' -- ' + emotionList[self.emotion]+'\n'
                return record