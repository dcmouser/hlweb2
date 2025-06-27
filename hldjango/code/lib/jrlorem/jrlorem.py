# simple class for generating repeatable NON-random blocks of text
from lib.jr import jrfuncs

import os
import random

class JrLorem():
    def __init__(self, dataFilePath):
        self.paras = []
        self.loadText(dataFilePath)
    
    def loadText(self, dataFilePath):
        # fix path
        if (not jrfuncs.pathExists(dataFilePath)):
            dataFilePath = os.path.dirname(os.path.realpath(__file__)) + "/data/" + dataFilePath
        # load text
        text = jrfuncs.loadTxtFromFile(dataFilePath, True, "utf-8")
        # split into paragraphs
        textLines = text.split("\n")
        self.paras = []
        for line in textLines:
            line = line.strip()
            if (line==""):
                continue
            self.paras.append(line)
    

    def getParagraphs(self, start, end, maxLen=0):
        # get a specific subset of paragraphs
        text = ""
        for i in range(start,end+1):
            text = text + self.paras[i] + "\n"
            if (len(text)>=maxLen) and (maxLen>0):
                break
        text = text.strip()
        # end abruptly at target length
        if (maxLen>0):
            text[maxLen] = "."
        return text


    def getRandomTextMaxLen(self, maxLen):
        # get some random lines that add up to a target length
        text = ""
        while (len(text)<maxLen):
            i = random.randint(0, len(self.paras)-1)
            text = text + self.paras[i]
            if (len(text)>=maxLen) and (maxLen>0):
                break
        text = text.strip()
        # end abruptly at target length
        if (maxLen>0):
            text[maxLen] = "."
        return text


    def getParagraphsMaxLen(self, start, maxLen):
        # get a specific subset of paragraphs
        text = ""
        for i in range(start,len(self.paras)):
            text = text + self.paras[i] + "\n"
            if (len(text)>=maxLen) and (maxLen>0):
                break
        text = text.strip()
        # end abruptly at target length
        if (maxLen>0):
            text[maxLen] = "."
        return text

