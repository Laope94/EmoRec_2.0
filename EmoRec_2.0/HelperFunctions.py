# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

class HelperFunctions(object):
    # táto trieda obsahuje pomocné funkcie, ktoré využívajú viaceré triedy
    # this class contains helper functions commonly used by other classes

    # zamknúť prvok GUI | lock GUI element
    def lockWidget(widget):
        widget.config(state='disabled')

    # odomknúť prvok GUI | unlock GUI element
    def unlockWidget(widget):
        widget.config(state='normal')

    # nastaviť prvok GUI iba na čítanie | set GUI element as readonly
    # prvok znovu umožní zápis po použití funkcie unlockWidget() | element allows writing again after calling unlockWidget() function
    def readonlyWidget(widget):
        widget.config(state='readonly')

    # zo slovníka vráti hodnotu daného klúča | returns value of given key from dictionary
    def getValueByKey(dictionary, dictionary_key):
        return dictionary[dictionary_key]