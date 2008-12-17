import os

from menclave.aenclave.control import Controller

def announce(string):
    pid = os.fork()
    if not pid:
        controller = Controller()
        controller.pause()
        os.system('echo "'+string+'" | festival --tts')
        controller.unpause()
    return
    
