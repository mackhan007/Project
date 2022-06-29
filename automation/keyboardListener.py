from pynput.keyboard import Key, Listener
from time import time


class keyboardListener:
    def __init__(self):
        self.file = open("ak.txt", "a") # automate keyboard - ak
        self.pressedKeys = {}
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
    
    def on_press(self, key):
        self.pressedKeys[key] += 1
        print('{0} release'.format(key))
        sec = time()
        self.file.write(f"keyboard - time: {sec} key: {key} - pressed\n")

    def on_release(self, key):
        self.pressedKeys[key] -= 1
        sec = time()
        self.file.write(f"keyboard - time: {sec} key: {key} - released\n")
        # if key == Key.esc:
        #     return False
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()

a = [str(i) for i in Key]
for i in a:
    print(i)