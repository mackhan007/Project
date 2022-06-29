# IMPORTS
import os
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
import numpy as np
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
import pandas as pd
import random
import json
# nltk.download('punkt')

class Chatbot:
    def __init__(self, fileName='data.json') -> None:
        self.model = None
        self.words = []
        self.classes = []
        self.documents = []
        self.train_x = None
        self.train_y = None
        self.data = None
        self.projectDir = os.getcwd()
        self.cwd = f'{self.projectDir}/chatbotV2/'

        self.fileName = (self.cwd + fileName) if fileName == 'data.json' else fileName

        try:
            self.createData()
            self.model = load_model(self.cwd+'chatbot.h5')
        except:
            self.model_reboot()
        
        self.model_reboot()

    # Formatting the data
    def createData(self):
        datafile = open(self.fileName)
        self.data = json.load(datafile)

        for data in self.data['data']:
            for pattern in data['patterns']:
                w = nltk.word_tokenize(pattern)
                self.words.extend(w)
                if (w, data['tag']) not in self.documents: 
                    self.documents.append((w, data['tag']))
                if data['tag'] not in self.classes:
                    self.classes.append(data['tag'])

        self.words = [stemmer.stem(w.lower()) for w in self.words if w not in '?']
        self.words = sorted(list(set(self.words)))
        self.classes = sorted(list(set(self.classes)))

        training = []
        output_empty = [0] * len(self.classes)

        for doc in self.documents:
            bag = []
            pattern_words = doc[0]
            pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
            # print(self.words)
            # print(pattern_words)
            for w in self.words:
                bag.append(1) if w in pattern_words else bag.append(0)
            # print(bag)
            output_row = list(output_empty)
            output_row[self.classes.index(doc[1])] = 1
            # print(output_row)
		    
            training.append([bag, output_row])

        random.shuffle(training)
        training = np.array(training, dtype=list)
        self.train_x = list(training[:,0])
        self.train_y = list(training[:,1])
        # print(self.train_x), print(self.train_y)

    # creating the model
    def create_model(self):
        self.model = Sequential()
        self.model.add(Dense(128, input_shape=(len(self.train_x[0]),), activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(len(self.train_y[0]), activation='softmax'))

    # compiling the model
    def compile_model(self):
        sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        self.model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
    
    # training the model
    def train_model(self):
        self.model.fit(
            np.array(self.train_x), 
            np.array(self.train_y), 
            epochs=100, 
            batch_size=5, 
            verbose=1
        )
        self.model.save(self.cwd+'chatbot.h5')

    # tokenizing the sentence
    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
        return sentence_words

    # bag of words function used for training the model
    def bow(self, sentence, words, show_details=True):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0]*len(words)  
        for s in sentence_words:
            for i,w in enumerate(words):
                if w == s: 
                    bag[i] = 1

        return np.array(bag)

	# for getting the lists of responses
    def classify_local(self, sentence):
        ERROR_THRESHOLD = 0.25
        input_data = pd.DataFrame([self.bow(sentence, self.words)], dtype=float, index=['input'])
        results = self.model.predict([input_data])[0]
        results = [[i,r] for i,r in enumerate(results) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append([self.classes[r[0]], str(r[1])])
	    
        return return_list
    
    def getBowForPattern(self, sentence, pattern):
        sentence = set(self.clean_up_sentence(sentence))
        pattern = set(self.clean_up_sentence(pattern))
        
        counter = 0
        
        for word in sentence:
            if word in pattern:
                counter += 1 
                
        return (counter / len(pattern))

    # for getting a response
    def getresponse(self, inputString):
        ans = self.classify_local(inputString)
        prediction_list = [ans[i][1] for i in range(len(ans))]
        prediction = max(prediction_list)
        predicted_index = prediction_list.index(prediction)
        
        responses = {}
        bow = {}
        
        for tag in self.data['data']:
            if tag['tag'] == ans[predicted_index][0]:
                if 'responses' not in tag: 
                    for pd in tag['patterns']:
                        responses[pd] = '' 
                        bow[pd] = self.getBowForPattern(inputString, pd)
                else:
                    for pd, rd in zip(tag['patterns'], tag['responses']):
                        responses[pd] = rd
                        bow[pd] = self.getBowForPattern(inputString, pd)
        
        return {
            'prediction': ans[predicted_index][0],
            'accuracy': prediction,
            'responses': responses,
            'bow': bow
        }

	# rebooting the model
    def model_reboot(self):
        self.createData()

        self.create_model()
        self.compile_model()

        self.train_model()

# chatbot = Chatbot()

# print(chatbot.getresponse('hi'))