import os
import json
from time import sleep
from .listeners import Listeners
from .runAutomationSteps import RunSteps
from .getAutomationSteps import AutomateSteps

class Automater:
    def __init__(self) -> None:
        self.projectDir = os.getcwd()
        self.dir = 'tasks'
        
        self.listener = None
    
    def techBot(self, name: str, tag: str, patterns: list[str]):
        fileName = f'{self.projectDir}/data/{name.lower()}/{self.dir}/{tag}'
        
        print('listening') 
        self.listener = Listeners(f"{fileName}.txt", f'{fileName}_reply.txt')
        self.listener.start()
        print('done listening') 
        
        automateSteps = AutomateSteps(f'{fileName}.txt')
        variables = automateSteps.convertToStep()
        print('created steps', variables)
        if ' ' in variables:
            variables.remove(' ')
        if '' in variables:
            variables.remove('')
       

        variableDict = {}
        for pattern in patterns:
            newPattern = pattern
            for var in variables:
                if var in pattern:
                    newPattern = newPattern.replace(var.lower(), '$variable')
             
            variableDict[pattern] = newPattern
        
        file = open(f'{fileName}_variables.json', 'w')
        file.write(json.dumps(variableDict, indent=4))
        file.close()
        
        
        
        
        

    def stopListening(self):
        print('stopping to listen', self.listener)
        if not self.listener:
            self.listener.stop()
            self.listener = None
        
    def performTask(self, name, tag, variablePattern, variable):
        fileName = f'{self.projectDir}/data/{name.lower()}/{self.dir}/{tag}_steps.json'

        if not os.path.exists(fileName):
            raise Exception('Unable to find the task')
        
        runSteps = RunSteps(fileName)
        runSteps.performSteps(variable)
        
        replies = runSteps.getReply()
        
        return replies