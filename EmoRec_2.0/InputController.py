class InputController(object):
    import sounddevice as sd
    import queue
    from threading import Thread

    q = queue.Queue(maxsize=2048)
    dataBuffer = []
   
    #returns dictionary of devices and their IDs
    def getDeviceList(self):
        deviceQueryResult = self.sd.query_devices()
        hostapiQueryResult = self.sd.query_hostapis()
        deviceList = dict()
        for i in range(len(deviceQueryResult)):
            if(deviceQueryResult[i]['max_input_channels']>0):
                deviceList["" + deviceQueryResult[i]["name"] + 
                           ", " + hostapiQueryResult[deviceQueryResult[i]["hostapi"]]["name"] + 
                           ", (in: " + str(deviceQueryResult[i]["max_input_channels"]) +
                           ", out: " + str(deviceQueryResult[i]["max_output_channels"]) + ")" +
                           ", " + str(deviceQueryResult[i]["default_samplerate"]) + " Khz"] = i
        return deviceList

    def callback(self,indata,frames,time,status):
        if(status):
            print(status)
        self.q.put(indata.copy())
    
    #not advised to call directly, call startStream() instead
    def __startStreamWorker(self, deviceID, samplerate, dataGrabber):
        with self.sd.InputStream(samplerate=samplerate,channels=1,device=deviceID, callback=self.callback): 
            while True:
                self.dataBuffer.append(self.q.get())
                if(len(self.dataBuffer)==100):
                    self.streamThread = self.Thread(target = dataGrabber, args=(self.dataBuffer,))
                    self.streamThread.start()
                    self.dataBuffer=[]

    def startStream(self, deviceID, samplerate, dataGrabber):
        self.streamWorkerThread = self.Thread(target = self.__startStreamWorker, args=(deviceID,samplerate,dataGrabber))
        self.streamWorkerThread.start()
        #return self.streamWorkerThread