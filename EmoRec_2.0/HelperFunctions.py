# Univerzita Konštantína Filozofa v Nitre | Constantine the Philosopher University in Nitra
# Fakulta Prírodných Vied | Faculty of Natural Sciences
# Katedra informatiky | Department of informatics
# Diplomová práca | Diploma thesis
# Bc. Timotej Sulka

# táto trieda obsahuje pomocné funkcie, ktoré využívajú viaceré triedy
# this class contains helper functions commonly used by other classes
class HelperFunctions(object):

    # zamkne jeden alebo viac GUI prvkov | locks one or more GUI elements
    def lockWidget(*widget):
        for w in widget:
            w.config(state='disabled')

    # odomkne jeden alebo viac GUI prvkov | unlocks one or more GUI elements
    def unlockWidget(*widget):
        for w in widget:
            w.config(state='normal')

    # nastaví jeden alebo viac GUI prvkov iba na čítanie | sets one or more GUI elements as readonly
    # prvok znovu umožní zápis po použití funkcie unlockWidget() | element allows writing again after calling unlockWidget() function
    def readonlyWidget(*widget):
        for w in widget:
            w.config(state='readonly')