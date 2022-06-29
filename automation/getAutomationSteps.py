import os
import json
from collections import defaultdict


class AutomateSteps:
    def __init__(self, fileName) -> None:
        self.fileName = fileName
        self.file = open(fileName, "r")

        self.pressedKeys = defaultdict(bool) 

        self.ignoreKeys = {"Key.space", 'Key.backspace', 'Key.delete', 'Key.caps_lock', 'Key.shift', 'Key.shift_r', '.'}
    
    def pretty(self, d, indent=2):
        print (json.dumps(d, indent=indent))
    
    def convertToStep(self):
        stepIndex = 0    
        stepsDict = {}    
        possibleVariables = set()

        time = None

        word = ''
        startIndex = -1

        for line in self.file.readlines():
            stepIndex += 1
            splits = line.split()

            if len(splits) < 1 and not (splits[0] == 'keyboard' or splits[0] == 'mouse'):
                continue

            stepsDict[f'step {stepIndex}'] = {
                'inputType': splits[0],
                'function': splits[-1]
            }

            splitsIndex = 2

            while splitsIndex < len(splits):
                if splits[splitsIndex] == '-': break

                stepsDict[f'step {stepIndex}'][splits[splitsIndex][0:-1]] = splits[splitsIndex+1]

                splitsIndex += 2
            
            newTime = float(stepsDict[f'step {stepIndex}']['time'])

            if time:
                stepsDict[f'step {stepIndex-1}']['time'] = newTime - time 

            time = newTime 

            # get only the key not the quotes
            if "key" in stepsDict[f'step {stepIndex}'] and stepsDict[f'step {stepIndex}']["key"][0] == "'" \
                and stepsDict[f'step {stepIndex}']["key"][-1] == "'":

                stepsDict[f'step {stepIndex}']["key"] = stepsDict[f'step {stepIndex}']["key"][1:-1] 
            
            # convert to int or float
            if 'x' in stepsDict[f'step {stepIndex}']:
                stepsDict[f'step {stepIndex}']['x'] = float(stepsDict[f'step {stepIndex}']['x']) 
            
            if 'y' in stepsDict[f'step {stepIndex}']:
                stepsDict[f'step {stepIndex}']['y'] = float(stepsDict[f'step {stepIndex}']['y'])
            
            if 'dx' in stepsDict[f'step {stepIndex}']:
                stepsDict[f'step {stepIndex}']['dx'] = float(stepsDict[f'step {stepIndex}']['dx'])
            
            if 'dy' in stepsDict[f'step {stepIndex}']:
                stepsDict[f'step {stepIndex}']['dy'] = float(stepsDict[f'step {stepIndex}']['dy'])
            
            # end converting 

            '''
                pressed keys
            '''
            if stepsDict[f'step {stepIndex}']['inputType'] == 'keyboard' and \
                (stepsDict[f'step {stepIndex}']['function'] == 'pressed' or \
                stepsDict[f'step {stepIndex}']['function'] == 'released') \
                and 'Key' in stepsDict[f'step {stepIndex}']['key']:
                
                if stepsDict[f'step {stepIndex}']['function'] == 'pressed': 
                    self.pressedKeys[stepsDict[f'step {stepIndex}']['key']] = True
                else:
                    del self.pressedKeys[stepsDict[f'step {stepIndex}']['key']]

            '''
                converting data into variables
            '''

            if stepsDict[f'step {stepIndex}']['inputType'] == 'keyboard' and \
                    (stepsDict[f'step {stepIndex}']['key'].isalnum() or \
                    stepsDict[f'step {stepIndex}']['key'] in self.ignoreKeys):
                if len(self.pressedKeys) > 0: continue
                
                if startIndex == -1:
                    if stepsDict[f'step {stepIndex}']['key'] == "Key.space":
                        continue 
                    startIndex = stepIndex
                
                if stepsDict[f'step {stepIndex}']['key'] in {'Key.caps_lock', 'Key.shift', 'Key.shift_r'}:
                    continue 

                if stepsDict[f'step {stepIndex}']['key'] == "Key.space":
                    word += ' ' 
                elif (stepsDict[f'step {stepIndex}']['key'] == "Key.backspace" \
                    or stepsDict[f'step {stepIndex}']['key'] == "Key.delete") \
                    and word:
                    word = word[:-2]
                else:
                    word += stepsDict[f'step {stepIndex}']['key']
            else:
                '''
                    do something with the word
                '''
                if startIndex != -1: 
                    word = word[::2]
                    print(word, startIndex, stepIndex)
                    possibleVariables.add(word.strip())
                    
                    if len(word) > 1:
                        for deleteStep in range(startIndex, stepIndex):
                            del stepsDict[f'step {deleteStep}']                            


                        stepsDict[f'step {startIndex}'] = {
                            'inputType': 'keyboard',
                            'function': 'type',
                            'key': word,
                            'time': 2
                        } 

                        stepsDict[f'step {startIndex + 1}'] = stepsDict[f'step {stepIndex}']

                        del stepsDict[f'step {stepIndex}'] 

                        stepIndex = startIndex + 1 


                    word = ''
                    startIndex = -1


        stepsDict[f'step {stepIndex}']['time'] = 0

        self.dumpStep(stepsDict)

        # self.deleteFile()

        return possibleVariables
    
    def dumpStep(self, dict):
        stepsFile = open(self.fileName.replace(".txt", "")  +'_steps.json', "w")
        stepsFile.write(json.dumps(dict, indent=4))
        stepsFile.close()


    def deleteFile(self):
        self.file.close()
        os.unlink(self.fileName)

        print("File deleted!!")

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
        