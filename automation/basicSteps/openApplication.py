import os
from pynput import keyboard
from time import time, sleep
from .type import Type

from pyrsistent import thaw

class openApp:
    def __init__(self) -> None:
        self.keyboard = keyboard.Controller()
        self.isAppFilesLoaded = False
        self.type = Type()
  
    def getFiles(self):
        if not self.isAppFilesLoaded:
            appFileLocation = os.path.join('/Applications')
            files = os.listdir(appFileLocation)
            files = [f.lower() for f in files]

            self.isAppFilesLoaded = True
            self.appFiles = files
            return files
        else:
            return self.appFiles



    def isAppInstalled(self, appName) -> bool:
        files = self.getFiles()
        return appName+'.app' in files 


    def openApp(self, appName):

        if not self.isAppInstalled(appName):
            raise Exception(appName+" application not found")

        sleep(0.2)
        self.keyboard.press(keyboard.Key.cmd)
        self.keyboard.tap(keyboard.Key.space)
        self.keyboard.release(keyboard.Key.cmd)
        sleep(0.3)

        for letter in appName:
            self.type.type(letter)

        sleep(0.3)
        self.keyboard.tap(keyboard.Key.enter)