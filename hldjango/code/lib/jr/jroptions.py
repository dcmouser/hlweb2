import re
import os
from . import jrfuncs
from .jrfuncs import jrprint

import json



class JrOptions:
    def __init__(self, optionDirectory):
        self.optionDirectory = optionDirectory
        self.dataDict = {}
        self.dirtyDict = {}
        self.readOnly = {}

    def saveOptionsFiles(self, flagOnlyIfDiry):
        for keyCat in self.dataDict.keys():
            self.saveOptionsBlock(keyCat, flagOnlyIfDiry)

    def saveOptionsBlock(self, keyCat, flagOnlyIfDiry):
        if (not flagOnlyIfDiry) or (self.dirtyDict[keyCat]):
            filePath = self.calcFilePath(keyCat)
            if (keyCat in self.readOnly) and (self.readOnly[keyCat]):
                return False
            keyDict = self.dataDict[keyCat]
            self.saveOptionsKeyData(keyCat, filePath, keyDict)
            # clear dirty flag
            self.setKeyBlockDirtyFlag(keyCat, False)


    def loadOptionsFile(self, keyCat, isReadOnly, errorIfMissing):
        # try to load the file by key json dictionary
        filePath = self.calcFilePath(keyCat)
        if (not jrfuncs.pathExists(filePath)):
            if (errorIfMissing):
                raise Exception('Required options file not found: {}.'.format(filePath))
            else:
                return False
        #
        data = self.loadOptionsKeyData(filePath)
        self.dataDict[keyCat] = data
        # clear flag
        self.setKeyBlockDirtyFlag(keyCat, False)
        self.readOnly[keyCat] = isReadOnly
        return True


    def calcFilePath(self, keyCat):
        filePath = '{}/{}.json'.format(self.optionDirectory, keyCat)
        return filePath

    def mergeRawDataForKey(self, keyCat, keyDict):
        if (keyCat not in self.dataDict):
            self.dataDict[keyCat] = keyDict
        else:
            jrfuncs.deepMergeOverwriteA(self.dataDict[keyCat], keyDict)
            #self.dataDict[keyCat] = {**self.dataDict[keyCat], ** keyDict}
        self.setKeyBlockDirtyFlag(keyCat, True)


    def getKeyBlock(self, keyCat):
        return self.dataDict[keyCat]

    def setKeyBlock(self, keyCat, blockDict):
        self.dataDict[keyCat] = blockDict
        self.setKeyBlockDirtyFlag(keyCat, True)
    
    def setKeyBlockDirtyFlag(self, keyCat, val):
        self.dirtyDict[keyCat] = val


    def getKeyValThrowException(self, keycat, key):
        if (keycat not in self.dataDict):
            raise Exception('Key category not found: {}'.format(keycat))
        if (key not in self.dataDict[keycat]):
            raise Exception('Key not found in keycat[{}]: {}'.format(keycat, key))
        return self.dataDict[keycat][key]

    def getKeyVal(self, keycat, key, defaultVal):
        if (keycat not in self.dataDict):
            return defaultVal
        if (key not in self.dataDict[keycat]):
            return defaultVal
        return self.dataDict[keycat][key]

    def setKeyVal(self, keycat, key, val):
        if (keycat not in self.dataDict):
            self.dataDict[keycat] = {key: val}
        else:
            self.dataDict[keycat][key] = val
        self.setKeyBlockDirtyFlag(keycat, True)

    def saveOptionsKeyData(self, keyCat, filePath, keyDict):
        tmpFilePath = filePath+'.tmp'
        with open (tmpFilePath, 'w') as file:
            jrprint('Saving json options {} to file {}.'.format(keyCat, filePath))
            txt = json.dumps(keyDict, indent=4)
            file.write(txt)
        jrfuncs.copyFilePath(tmpFilePath, filePath)

    def loadOptionsKeyData(self, filePath):
        jrprint('Loading options block from file: {}'.format(filePath))
        f = open(filePath)
        data = json.load(f)
        return data

    def getAllBlocks(self):
        return self.dataDict
