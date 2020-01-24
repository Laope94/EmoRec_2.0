class InputController(object):
    import sounddevice as sd
   
    #returns dictionary of devices and their IDs
    def getDeviceList(self):
        deviceQueryResult = self.sd.query_devices()
        hostapiQueryResult = self.sd.query_hostapis()
        deviceList = dict()
        for i in range(len(deviceQueryResult)):
            if(deviceQueryResult[i]['max_input_channels']>0):
                #deviceList.append({"id" : i,
                #                   "name" : deviceQueryResult[i]["name"],
                #                   "hostapi" : hostapiQueryResult[deviceQueryResult[i]["hostapi"]]["name"],
                #                   "in" : deviceQueryResult[i]["max_input_channels"],
                #                   "out" : deviceQueryResult[i]["max_output_channels"],
                #                   "default_samplerate" : deviceQueryResult[i]["default_samplerate"]})
                deviceList["" + deviceQueryResult[i]["name"] + 
                           ", " + hostapiQueryResult[deviceQueryResult[i]["hostapi"]]["name"] + 
                           ", (in: " + str(deviceQueryResult[i]["max_input_channels"]) +
                           ", out: " + str(deviceQueryResult[i]["max_output_channels"]) + ")" +
                           ", " + str(deviceQueryResult[i]["default_samplerate"]) + " Khz"] = i
        return deviceList


