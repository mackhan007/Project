import json
import clipboard
from pynput import keyboard, mouse
from time import time, sleep
from .basicSteps.main import Type


class RunSteps:
    def __init__(self, fileName) -> None:
        self.replySet = set()
        self.replyData = []
        self.replyFileIndex = 1

        self.fileName = fileName
        self.file = open(fileName, "r")
        self.jsonData = json.load(self.file)

        self.clearOldClipboardData()

        self.keyboard = keyboard.Controller()
        self.keyboardKeysStr = [str(i) for i in keyboard.Key]
        self.keyboardKeys = list(keyboard.Key)

        self.type = Type()

        self.mouse = mouse.Controller()
    
    def keyboardStep(self, data, variables):
        function = data['function'] 

        def getKey(rawData):
            if 'Key.' in rawData:
                index = self.keyboardKeysStr.index(rawData)

                # out of range 
                if index == -1 or index > len(self.keyboardKeys): return ''

                return self.keyboardKeys[index]
    
            return rawData

        if function == 'type':
            if data['key'] in variables:
                self.type.typeWord(variables[data['key']]) 
            else:
                self.type.typeWord(data['key'])

        if function == 'pressed':
            self.keyboard.press(getKey(data['key']))

        elif function == 'released':
            self.keyboard.release(getKey(data['key']))

        sleep(data['time'])
    
    def mouseStep(self, data):
        function = data['function']

        if function == 'moved':
            self.mouse.position = (data['x'], data['y'])

        elif function == 'pressed':
            self.mouse.position = (data['x'], data['y'])

            if 'Button.left' in data['button']:
                self.mouse.press(mouse.Button.left)
            elif 'Button.right' in data['button']:
                self.mouse.press(mouse.Button.right)

        elif function == 'released':
            self.mouse.position = (data['x'], data['y'])

            if 'Button.left' in data['button']:
                self.mouse.release(mouse.Button.left)
            elif 'Button.right' in data['button']:
                self.mouse.release(mouse.Button.right) 

        elif function == 'scrolled':
            self.mouse.scroll(data['dx'], data['dy'])

        sleep(data['time'])
    
    def clearOldClipboardData(self):
        clipboard.copy('')

    def checkForReplyAndAppend(self):
        reply = clipboard.paste() 

        if reply and reply != '' and reply not in self.replySet:
            self.replySet.add(reply)
            self.replyData.append(reply)
            self.replyFileIndex += 1

    def performSteps(self, variables):
        for stepIndex in range(1, len(self.jsonData)+1):
            try:
                data = self.jsonData[f'step {stepIndex}']

                print(data)
                
                if data['inputType'] == 'keyboard':
                    self.keyboardStep(data, variables)
                elif data['inputType'] == 'mouse':
                    self.mouseStep(data)
                
                self.checkForReplyAndAppend()
            
            except Exception as e:
                print(e)

    def getReply(self):
        replyfileName = self.fileName.replace('steps', 'reply').replace('json', 'txt')
        file = open(replyfileName, 'r') 
        replyIndexes = set()
        reply = []
        
        for line in file.readlines():
            index = line.split()
            if index:
                index = index[0][:-1]
                replyIndexes.add(int(index))
        i = 1
        for data in self.replyData:
            if i in replyIndexes:
                reply.append(data)
                
            i += 1
        
        return reply
        


# rs = RunSteps("automate_step.json")

# rs.performSteps()