import pyttsx3
from time import sleep
from threading import Thread

class TTS:
    """
    Text To Speech Engine (TTS)
    """

    def __init__(self):
        self.tts_engine = self._set_voice_engine()
        
        print('TTS INIT')

    def run_engine(self):
        try:
           self.tts_engine.runAndWait() 
        except RuntimeError:
            self.tts_engine.endLoop()
            raise Exception("Unable to speak")
            
    
    def speak(self, text): 
        try:
            self.tts_engine.say(text)
            self.run_engine()
        except:
            self.tts_engine.say(text)
            self.run_engine()

    @staticmethod
    def _set_voice_engine():
        """
        Setup text to speech engine
        :return: pyttsx engine object
        """
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('voice', 'com.apple.speech.synthesis.voice.samantha')
        tts_engine.setProperty('rate', 160)  # Setting up new voice rate
        tts_engine.setProperty('volume', 1.0)  # Setting up volume level  between 0 and 1
        return tts_engine

    def stopEngine(self):
        self.tts_engine.stop()
        
     