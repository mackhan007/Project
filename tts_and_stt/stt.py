import speech_recognition as sr
from threading import Thread

class STT:
    """
        _summary_
        used to recognize voice 
    """
    def __init__(self):
        self.speechRecognizer = sr.Recognizer() 
        self.microphone = sr.Microphone(device_index=0) # device_index = 2 is used as it only takes external sounds
        self.speechRecognizer.pause_threshold = 0.5
        self.speechRecognizer.energy_threshold = 300 
        self.speechRecognizer.dynamic_energy_threshold = True
        self.ERROR_TEXT = 'unable to recognize'
        self.stop = False
        
        self.lastCallback = None 
        self.lastPauseThread = None

        print('STT INIT')
    
    def record(self, source, callback, pauseThread):
        self.speechRecognizer.adjust_for_ambient_noise(source)
        audio_data = self.speechRecognizer.listen(source)
        thread = Thread(target=self.recognize, args=(audio_data,callback,pauseThread, ))
        thread.start()
    

    def recognize(self, audio_data, callback, pauseThread):
        if pauseThread() or self.stop: return
        
        print("Recognizing...")
        
        try:
            text = self.speechRecognizer.recognize_google(audio_data)
            callback(text)
            # print(text, 'engine')
        except:
            print(self.ERROR_TEXT) 
    
    def runEngine(self, callback, pauseThread):
        print('STT RUN ENGINE')

        self.lastCallback = callback 
        self.lastPauseThread = pauseThread
        
        while(not self.stop): 
            if pauseThread(): continue

            print("Please talk")
            
            with self.microphone as source:
                self.record(source, callback, pauseThread)

    def stopEngine(self):
        print('STOP STT')
        self.stop = True
        
    def startEngine(self):
        self.stop = False
        
        # if self.lastCallback and self.lastPauseThread:
        #     self.runEngine(self.lastCallback, self.lastPauseThread)



