class HelperFunctions(object):

    def lockWidget(widget):
        widget.config(state='disabled')

    def unlockWidget(widget):
        widget.config(state='normal')

    def readonlyWidget(widget):
        widget.config(state='readonly')

    def getValueByKey(dictionary, dictionary_key):
        return dictionary[dictionary_key]