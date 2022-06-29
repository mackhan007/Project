import spacy
from nltk.tokenize import word_tokenize

class PartOfSpeech:
    def __init__(self) -> None:
        self.sp = spacy.load('en_core_web_sm')

    def getPartOfSpeech(self, text):
        result = self.sp(text)

        for i in result:
            print(i, i.tag_, spacy.explain(i.tag_))

        return result

from nltk.stem.lancaster import LancasterStemmer

class Stemming:
    def __init__(self) -> None:
        self.stemmer = LancasterStemmer()

    def getStem(self, words: list[str]):
        result = []

        for i in words:
            result.append(self.stemmer.stem(i.lower()))
        
        return result


pos = PartOfSpeech()

print(pos.getPartOfSpeech("Hii, My name is Aman Khan"))
print(pos.getPartOfSpeech("Open whatsapp"))

stemming = Stemming()

print(stemming.getStem(word_tokenize("Programmers program with programming languages")))
