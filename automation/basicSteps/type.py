from pynput import keyboard
from time import time, sleep

class Type:
    def __init__(self) -> None:
        self.keyboard = keyboard.Controller()
    
    def type(self, data):
        self.keyboard.tap(data)

        sleep(0.3)

    def typeWord(self, data):
        for i in data:
            self.type(i)

