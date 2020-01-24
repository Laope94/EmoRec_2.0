class HelperFunctions(object):
#-----------------------------------------------------
#---GUI HELPERS---------------------------------------
#-----------------------------------------------------
    def lockWidget(widget):
        widget.config(stage='disabled')

    def unlockWidget(widget):
        widget.config(state='normal')

    def getValueByKey(dictionary, dictionary_key):
        return dictionary[dictionary_key]


#-----------------------------------------------------
#---LOGIC HELPERS-------------------------------------
#-----------------------------------------------------



