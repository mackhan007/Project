from pynput.mouse import Listener
from time import time

class mouseListener:
    def __init__(self):
        self.file = open("am.txt", "a") # automate mouse - am
        with Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll) as listener:
            listener.join()
    
    def on_move(self, x, y):
        sec = time()
        self.file.write(f"mouse - time: {sec} x: {x} y: {y} - moved\n")
        print(x, y, " moved")
    
    def on_click(self, x, y, button, pressed):
        sec = time()
        
        self.file.write(f"mouse - time: {sec} x: {x} y: {y} button: {button} - {'pressed' if pressed else 'release'}\n")
        print(x, y, button)
    
    def on_scroll(self, x, y, dx, dy):
        sec = time()
        self.file.write(f"mouse - time: {sec} x: {x} y: {y} dx: {dx} dy: {dy} - scrolled\n")
        print(x, y, dx, dy)

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()

ml = mouseListener()


from time import sleep
from runAutomationSteps import RunSteps
from listeners import Listeners
from getAutomationSteps import AutomateSteps
from basicSteps.type import Type
from basicSteps.openApplication import openApp
import os


dir = 'tasks/'
# dir = 'sample/'

if not os.path.exists(os.path.join(os.getcwd(), dir)):
    os.makedirs(os.path.join(os.getcwd(), dir))

# fileName = dir + 'tell_me_time'

# l = Listeners(f"{fileName}.txt", f'{fileName}_reply.txt')

# ass = AutomateSteps(f'{fileName}.txt')

# ass.convertToStep()

# rs = RunSteps(f"{fileName}_steps.json")

# rs.performSteps()

# print(rs.getReply())



# l = Listeners()

# '''
#     testing code
# '''
# from threading import Thread


# def startMouse():
#     ml = mouseListener()

# def startKeyboard():
#     kl = keyboardListener()


# mouseThread = Thread(target=startMouse)
# keyboardThread = Thread(target=startKeyboard)


# mouseThread.start()
# keyboardThread.start()


'''
    working code
    l = Listeners()

'''
