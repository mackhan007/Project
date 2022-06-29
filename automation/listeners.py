import clipboard
from time import time
from pynput import mouse, keyboard
from collections import defaultdict

class Listeners:
    def __init__(self, fileName, replyFileName) -> None:
        self.pressedKeys = defaultdict(int)
        self.replySet = set()
        self.replyFileIndex = 1

        self.fileName = fileName
        self.replyFileName = replyFileName
        self.file = open(fileName, "a")
        self.replyFile = open(replyFileName, "a")

        self.clearOldClipboardData()

    def start(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as self.kl, \
            mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll) as self.ml:

            self.kl.join()
            self.ml.join()
        
    def clearOldClipboardData(self):
        clipboard.copy('')

    def checkForReplyAndAppend(self):
        reply = clipboard.paste() 

        if reply and reply != '' and reply not in self.replySet:
            self.replySet.add(reply)
            reply = reply.replace("\n", " ")
            self.replyFile.write(f'{self.replyFileIndex}. {reply}\n')
            self.replyFileIndex += 1


        
    def on_move(self, x, y):
        sec = time()
        # self.file.write(f"mouse - time: {sec} x: {x} y: {y} - moved\n")
        # print(x, y, " moved")
        self.checkForReplyAndAppend()
    
    def on_click(self, x, y, button, pressed):
        sec = time()
        self.file.write(f"mouse - time: {sec} x: {x} y: {y} button: {button} - {'pressed' if pressed else 'released'}\n")
        # print(x, y, button)
        self.checkForReplyAndAppend()
    
    def on_scroll(self, x, y, dx, dy):
        sec = time()
        self.file.write(f"mouse - time: {sec} x: {x} y: {y} dx: {dx} dy: {dy} - scrolled\n")
        # print(x, y, dx, dy)
        self.checkForReplyAndAppend()
    
    def on_press(self, key):
        self.pressedKeys[key] += 1
        # print('{0} release'.format(key))
        sec = time()
        self.file.write(f"keyboard - time: {sec} key: {key} - pressed\n")
        self.checkForReplyAndAppend()

    def on_release(self, key):
        self.pressedKeys[key] -= 1
        sec = time()
        self.file.write(f"keyboard - time: {sec} key: {key} - released\n")
        self.checkForReplyAndAppend()
        if key == keyboard.Key.esc:
            self.stop()
    
    def stop(self):
        self.file.close()
        self.replyFile.close()
        self.kl.stop()
        self.ml.stop()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()