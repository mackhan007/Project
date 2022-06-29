import os
import json
from time import sleep, time
from threading import Thread, Event
from tts_and_stt.main import TTS, STT
from faceRec.main import FaceRecognizer
from chatbotV2.main import Chatbot
from automation.main import Automater


class Main:
    '''
        init all the engines
        tts = Text to speech engine
        stt = Speech to text engine
        faceRec = FaceRecognition engine
    '''
    def __init__(self) -> None:
        self.projectDir = os.getcwd()
        self.dir = 'tasks'
        
        self.dataDir = f'{self.projectDir}/data'
        self.mainChatbotDataFile = f'{self.projectDir}/chatbotV2/data.json'
        
        self.tts = TTS()
        self.stt = STT()
        self.faceRec = FaceRecognizer()
        self.commandReplyClassifier = Chatbot()
        self.replyClassifier = Chatbot(self.dataDir + '/unknown/reply.json')
        self.commandClassifier = Chatbot(self.dataDir + '/unknown/command.json')
        self.automater = Automater() 

        self.faceRecStartRecognizingFaceThread: Thread = None
        self.sttRunEngineThread: Thread = None
        self.speaking = False
        self.teaching = False
        
        self.automationRunning = False
        
        self.voiceCallbackFunctionText = None
    
    def awaitFunction(self, awaitVariable=None):
        """awaiting function 
        can be used as a await for asycn data

        Args:
            awaitVariable (any, optional): variable for await. Defaults to None.
        """
        if awaitVariable:
            while not awaitVariable:
               sleep(0.5) 
        else:
            while not self.voiceCallbackFunctionText:
                sleep(0.5)
            
    def getText(self) -> str:
        """get text from stt

        Returns:
            str: return text
        """
        self.awaitFunction()
        
        text = self.voiceCallbackFunctionText
        self.voiceCallbackFunctionText = None 
        return text 
    
    def addDataToTag(self, fileLocation: str, pattern: str, tag: str) -> None:
        """used to add tag to file

        Args:
            fileLocation (str): file location where it is suppose to be added
            text (str): pattern to be added 
            tag (str): tag to which pattern to be added
        """
        file = open(fileLocation, 'r')
        dataList: dict = json.load(file)
        file.close()
        
        for data in dataList['data']:
            if data['tag'] == tag:
                data['patterns'].append(pattern)
                break
                
        
        file = open(fileLocation, 'w')
        json.dump(dataList, file, indent=4, sort_keys=True)
        file.close()
        
        self.resetClassifiers()
    
    def putDataInFile(self, fileLocation, data):
        file = open(fileLocation, 'r')
        dataList: dict = json.load(file)
        file.close()
        
        dataList['data'].append(data) 
        
        file = open(fileLocation, 'w')
        json.dump(dataList, file, indent=4, sort_keys=True)
        file.close() 
        
    def teachBot(self, text):
        self.speak('Unable to find a command, would you like to teach this command?')

        isPositiveOrNegative = self.getText() 
        self.awaitFunction(self.commandReplyClassifier)
            
        isPositiveOrNegativeResponse = self.commandReplyClassifier.getresponse(isPositiveOrNegative)
        print(isPositiveOrNegativeResponse)
        
        if isPositiveOrNegativeResponse['prediction'] == 'positive':    
            command = {
                'tag': f'{text.lower().replace(" ", "_")}',
                'patterns': set()
            }
            
            command['patterns'].add(text)
            
            
            self.speak('Please provide all possible patterns by which the command can be triggered, and say done when you are done.')
            
            text = self.getText()
            
            while text.lower() != 'done':
                command['patterns'].add(text)
                
                text = self.getText()

            self.speak(f'starting to record the process, please press escape button when you have completed your task')

            if 'don' in command:
                command['patterns'].remove('don')            
            
            command['patterns'] = list(command['patterns'])
            
            print(command)
            self.automationRunning = True
            self.automater.techBot(self.faceRec.lastUser.lower(), command['tag'], command['patterns'])
            self.automationRunning = False

            name = self.faceRec.lastUser if self.faceRec.lastUser and self.faceRec.lastUser.lower() != 'unknown' else ''
             
            self.speak(f"Thank you for teaching me a new command, {name}")

            commandFileLocation = self.dataDir + f'/{self.faceRec.lastUser.lower()}/command.json'

            command['patterns'] = list(command['patterns'])
            
            self.putDataInFile(commandFileLocation, command)
            
            for pattern in command['patterns']:
                self.addDataToTag(self.mainChatbotDataFile, pattern, 'command')
                
            self.resetClassifiers() 

            
            '''
                TODO: WORK ON REPLIES MANAGEMENT
            '''
            
            
            
            # repliesFileLocation = f'{self.projectDir}/data/{self.faceRec.lastUser.lower()}/{self.dir}/{command["tag"]}_reply.txt'

            # if os.path.exists(repliesFileLocation):
            #     repliesFile = open(repliesFileLocation, 'r')
            #     line = repliesFile.readline()
                
            #     if line.strip() != '':
            #         self.speak('These are the replies, please confirm')                                                                                                                                                                                                                                                        
    
    def teachChatBot(self, text):
        self.speak('Unable to find a reply, would you like to teach a reply for it?')

        isPositiveOrNegative = self.getText() 
        self.awaitFunction(self.commandReplyClassifier)
            
        isPositiveOrNegativeResponse = self.commandReplyClassifier.getresponse(isPositiveOrNegative)
        
        if isPositiveOrNegativeResponse['prediction'] == 'positive':    
            reply = {
                'tag': f'{text.lower().replace(" ", "_")}',
                'patterns': set(),
                'responses': set()
            }

            reply['patterns'].add(text)
            
            self.speak('Please provide all possible patterns by which the reply can be triggered, and say done when you are done.')
            
            text = self.getText()
            
            while text.lower() != 'done':
                reply['patterns'].add(text)
                
                text = self.getText()

            if 'don' in reply['patterns']: 
                reply['patterns'].remove('don')            
            
            self.speak('Please provide all possible response for reply, and say done when you are done.')
            
            text = self.getText()
            
            while text.lower() != 'done':
                reply['responses'].add(text)
                
                text = self.getText()
            
            if 'don' in reply['responses']:
                reply['responses'].remove('don')     
            
            name = self.faceRec.lastUser if self.faceRec.lastUser and self.faceRec.lastUser.lower() != 'unknown' else ''
             
            self.speak(f"Thank you for teaching me a new response, {name}")

            replyFileLocation = self.dataDir + f'/{self.faceRec.lastUser.lower()}/reply.json'

            reply['patterns'] = list(reply['patterns'])
            reply['responses'] = list(reply['responses'])
            
            self.putDataInFile(replyFileLocation, reply)
            
            for pattern in reply['patterns']:
                self.addDataToTag(self.mainChatbotDataFile, pattern, 'reply')
                
            self.resetClassifiers() 
                
    
    def resetClassifiers(self):
        replyFileLocation = self.dataDir + f'/{self.faceRec.lastUser.lower()}/reply.json'
        commandFileLocation = self.dataDir + f'/{self.faceRec.lastUser.lower()}/command.json'

        self.commandReplyClassifier = None
        self.replyClassifier = None
        self.commandClassifier = None

        commandReplyClassifier = Chatbot()
        replyClassifier = Chatbot(replyFileLocation)
        commandClassifier = Chatbot(commandFileLocation)     
        
            
        self.commandReplyClassifier = commandReplyClassifier
        self.replyClassifier = replyClassifier
        self.commandClassifier = commandClassifier 
        
    def teachNewCommandOrReply(self, text):
        self.speak('unable to recognize, would you like to teach me?')

        isPositiveOrNegative = self.getText()

        isPositiveOrNegativeResponse = self.commandReplyClassifier.getresponse(isPositiveOrNegative)
        print(isPositiveOrNegativeResponse)
        
        if isPositiveOrNegativeResponse['prediction'] == 'positive':
            self.speak('Is it a command or an reply') 
            
            commandOrReply = self.getText()
            
            if 'command' in commandOrReply or 'reply' in commandOrReply:
                if 'command' in commandOrReply:
                    self.teachBot(text)
                elif 'reply' in commandOrReply:
                    self.teachChatBot(text)
    
    def getVariables(self, p1: str, p2: str) -> dict:
        """_summary_
        not yet a perfect algo

        Args:
            p1 (str): _description_
            p2 (str): _description_

        Returns:
            dictionary: provides back a diction for variables matched
        """
        
        s1 = p1.split()
        s2 = p2.split()
        
        indexes = []
        
        for i in range(len(s2)):
            if s2[i] == '$variable':
                indexes.append(i)
                
        di1 = 0
        di2 = 0 
        
        variables = {}
        
        for i in indexes:
            if i == 0 and i+1 not in indexes:
                word = ''
                lastWord = s2[i+1]
                di1 = i
                print(lastWord)
                
                while di1 < len(s1) and s1[di1] != lastWord:
                    word += s1[di1]
                    word += ' '
                    di1 += 1 
                    
                variables[i] = word
            
            elif i == len(s2) - 1 and i-1 not in indexes:
                word = []
                lastWord = s2[i-1]
                
                di1 = len(s1) - 1

                while di1 > 0 and s1[di1] != lastWord:
                    word.append(s1[di1])
                    di1 -= 1 
                    
                variables[i] = ' '.join(word[::-1])
                
            elif i+1 not in indexes and i-1 not in indexes:
                word = []
                prefix = s2[i-1]
                suffix = s2[i+1]
                
                lastData3Pos = di1
                
                while di1 < len(s1) and s1[di1] != prefix:
                    di1 += 1 
                
                di1 += 1
                    
                while di1 < len(s1) and s1[di1] != suffix:
                    word.append(s1[di1])
                    di1 += 1
                    
                variables[i] = ' '.join(word)
                
        return variables     
        
    def processText(self):
        sleep(2)
        if self.voiceCallbackFunctionText:
            text = self.getText()

            # if self.automationRunning and text == 'done':
            #     self.speak(f'Is your task completed?')       
            #     isPositiveOrNegative = self.getText()

            #     isPositiveOrNegativeResponse = self.commandReplyClassifier.getresponse(isPositiveOrNegative)
            #     print(isPositiveOrNegativeResponse)

            #     if isPositiveOrNegativeResponse['prediction'] == 'positive':
            #         self.automater.stopListening()
            #         print('stopped listening')
            #         return
            
            self.awaitFunction(self.commandReplyClassifier)
            
            response = self.commandReplyClassifier.getresponse(text)
            print(response)
            
            if float(response['accuracy']) < 0.8: 

                if float(response['accuracy']) > 0.45:
                    self.speak(f'Unable to recognize, Is it a {response["prediction"]}')                     
                    isPositiveOrNegative = self.getText()

                    isPositiveOrNegativeResponse = self.commandReplyClassifier.getresponse(isPositiveOrNegative)
                    
                    if isPositiveOrNegativeResponse['prediction'] != 'positive':
                        self.teachNewCommandOrReply(text)
                        return
                else:
                    self.teachNewCommandOrReply(text)
                    return
            
            
            if response['prediction'] == 'start':
                if self.faceRec.lastUser and self.faceRec.lastUser.lower() != 'unknown':
                    self.speak(f'Hello {self.faceRec.lastUser}')
                else:
                    self.speak('Hello, I am Samantha') 
                    
            elif response['prediction'] == 'stop':
                self.speak(f'Are you sure, you want to exit?', 4)
                
                isPositiveOrNegative = self.getText()

                self.awaitFunction(self.commandReplyClassifier)
                isPositiveOrNegativeResponse = self.commandReplyClassifier.getresponse(isPositiveOrNegative)
                print(isPositiveOrNegativeResponse)
                
                if float(isPositiveOrNegativeResponse['accuracy']) < 0.8: return
                
                if isPositiveOrNegativeResponse['prediction'] == 'positive':
                    if self.faceRec.lastUser and self.faceRec.lastUser.lower() != 'unknown':
                        self.speak(f'Good Bye, {self.faceRec.lastUser}')
                    else:
                        self.speak('Good Bye')

                    sleep(2)

                    self.stt.stopEngine()
                    self.faceRec.stopRecognition()
                    
            elif response['prediction'] == 'command':
                self.awaitFunction(self.commandClassifier)
                
                response = self.commandClassifier.getresponse(text) 
                print(response)
                
                maxBow = 0 
                pattern = None
                variableDict = {}
                variables = {}
                variablePattern = None
                
                variableDictLocation = f'{self.projectDir}/data/{self.faceRec.lastUser.lower()}/{self.dir}/{response["prediction"]}_variables.json'
                if os.path.exists(variableDictLocation):      
                    variableDictFile = open(variableDictLocation, 'r') 
                    variableDict = json.load(variableDictFile)
                
                for pd in response['responses']:
                    if response['bow'][pd] >= maxBow:
                        maxBow = response['bow'][pd] 
                        pattern = pd
                        
                variablePattern = pattern
                 
                if pattern and pattern in variableDict and '$variable' in variableDict[pattern]:
                    variablePattern = variableDict[pattern]
                    
                    v1 = self.getVariables(pattern, variablePattern)
                    v2 = self.getVariables(text, variablePattern)

                    if len(v1) == len(v2):
                        for i in v1:
                            variables[v1[i]] = v2[i]
                
                print(variables)
                    
                if float(response['accuracy']) > 0.8 and maxBow >= 0.5 and pattern:
                    self.speak(f'Are you shown you want to perform task, {text}')
                    
                    isPositiveOrNegative = self.getText()

                    self.awaitFunction(self.commandReplyClassifier)
                    isPositiveOrNegativeResponse = self.commandReplyClassifier.getresponse(isPositiveOrNegative)
                    
                    if isPositiveOrNegativeResponse['prediction'] == 'positive':
                        print(f'starting task {text}')
                        self.speak(f'starting task {text}')
                        try:
                            replies = self.automater.performTask(self.faceRec.lastUser.lower(), response['prediction'], variablePattern, variables)
                            
                            print('task completed') 
                            for reply in replies:
                                self.speak(reply)
                        except:
                            self.speak('Unable to find the task')
                else:
                    if float(response['accuracy']) < 0.5 and pattern:
                        self.speak(f'just want to make sure, what i understood, {pattern}, is it correct?') 
                        isPositiveOrNegative = self.getText()

                        self.awaitFunction(self.commandReplyClassifier)
                        isPositiveOrNegativeResponse = self.commandReplyClassifier.getresponse(isPositiveOrNegative)
                        commandFileLocation = self.dataDir + f'/{self.faceRec.lastUser.lower()}/command.json'

                        if isPositiveOrNegativeResponse['prediction'] == 'positive':
                            print(f'starting task {text}')
                            
                            self.addDataToTag(self.mainChatbotDataFile, text, 'command')
                            self.addDataToTag(commandFileLocation, text, response['prediction'])
                            
                            self.resetClassifiers() 
                           
                            print(f'starting task {text}')
                            self.speak(f'starting task {text}')
                            try:
                                replies = self.automater.performTask(self.faceRec.lastUser.lower(), response['prediction'],  variablePattern, variables)
                                
                                print('task completed')
                                for reply in replies:
                                    self.speak(reply)
                            except:
                                self.speak('Unable to find the task')
                       
                        elif isPositiveOrNegativeResponse['prediction'] == 'negative':
                            self.teachBot(text)
                    else:
                        self.teachBot(text) 
                
                
            elif response['prediction'] == 'reply':
                self.awaitFunction(self.replyClassifier)
                
                response = self.replyClassifier.getresponse(text) 
                maxBow = 0
                replyData = ''
                pattern = None
                
                for pd in response['responses']:
                    if response['bow'][pd] > maxBow:
                        maxBow = response['bow'][pd]
                        replyData = response['responses'][pd]
                        pattern = pd
                
                print(response, maxBow, replyData) 

                if float(response['accuracy']) > 0.8 and maxBow > 0.5:
                    print(replyData)
                    self.speak(replyData)
                else:
                    if float(response['accuracy']) < 0.5 and pattern:
                        self.speak(f'just want to make sure, what i understood, {pattern}, is it correct?')
                        
                        
                        isPositiveOrNegative = self.getText()

                        self.awaitFunction(self.commandReplyClassifier)
                        isPositiveOrNegativeResponse = self.commandReplyClassifier.getresponse(isPositiveOrNegative)
                        replyFileLocation = self.dataDir + f'/{self.faceRec.lastUser.lower()}/reply.json'
                        
                        if isPositiveOrNegativeResponse['prediction'] == 'positive':
                            self.speak(replyData) 
                            
                            self.addDataToTag(self.mainChatbotDataFile, text, 'reply')
                            self.addDataToTag(replyFileLocation, text, response['prediction'])
                            
                            self.resetClassifiers() 
                            
                        elif isPositiveOrNegativeResponse['prediction'] == 'negative':
                            self.teachChatBot(text)
                    else:
                        self.teachChatBot(text)
                 
    
    '''
        This is a callback function used to get recognized Data
    '''
    def voiceCallbackFunction(self, text: str):
        text = text.lower()
        print(text)
        self.voiceCallbackFunctionText = text
        self.processText()
            
    def cameraCallbackFunction(self, userName):
        if userName.lower() == 'unknown':
            self.speak("Unknown user found, would you like to register your face", 5)
             
            
            text = self.getText()
            
            self.awaitFunction(self.commandReplyClassifier)
            response = self.commandReplyClassifier.getresponse(text)
            print(response)
             
            if response['prediction'] == 'positive' and float(response['accuracy']) > 0.8: 
                print('register face')
                self.speak("Please provide your name", 5)
                
                
                text = self.getText()
                
                self.speak(f'Hello {text}, please stay still for registration', 4)
                try:
                    self.faceRec.stopRecognition()
                    self.faceRecStartRecognizingFaceThread = None
                    
                    self.faceRec.captureAndTrain(text, time())
                    
                    self.initEnginesThread()
                    self.faceRecStartRecognizingFaceThread.start()

                except Exception as e:
                    print(e)
                
        elif userName:
            self.speak(f"Welcome back, {userName}")
            
            replyFileLocation = self.dataDir + f'/{userName}/reply.json'
            commandFileLocation = self.dataDir + f'/{userName}/command.json'
            
            if os.path.exists(replyFileLocation) and os.path.exists(commandFileLocation):
                self.replyClassifier = None 
                self.commandClassifier = None  

            if os.path.exists(replyFileLocation):
                self.replyClassifier = None 
                self.replyClassifier = Chatbot(replyFileLocation)
                
            if os.path.exists(commandFileLocation):
                self.commandClassifier = None 
                self.commandClassifier = Chatbot(commandFileLocation)
                

    """_summary_
        getter for speaking

    Returns:
        bool: is speaking
    """
    def getIsPauseThread(self):
        return self.speaking
        
    '''
        INIT Thread
    '''
    def initEnginesThread(self):
        if not self.faceRecStartRecognizingFaceThread: 
            self.faceRecStartRecognizingFaceThread = Thread(target=self.faceRec.startRecognizingFace)
        if not self.sttRunEngineThread:
            self.sttRunEngineThread = Thread(target=self.stt.runEngine, \
                args=(self.voiceCallbackFunction, self.getIsPauseThread, ))
        
        self.faceRec.registerForOnUserChange(self.cameraCallbackFunction)

    '''
        Run all the engines
    '''
    def runEngine(self):
        self.initEnginesThread()

        self.faceRecStartRecognizingFaceThread.start()
        self.sttRunEngineThread.start()
    
    def speak(self, text, duration=3):
        """_summary_
        
        write a better way to implement it

        Args:
            text (_type_): _description_
        """
        self.speaking = True
       
        self.tts.speak(text)
        print(text, '-tts')
        
        self.speaking = False 
       
        

main = Main()
main.runEngine()