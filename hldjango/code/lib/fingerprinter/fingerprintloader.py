# class responsible for loading fingerprint images
# can be subclassed to handle different sources of data
#
# the job of the FingerPrintLoader is to create virtualFinget objects

from lib.jr.jrfuncs import jrprint

# python imports
import os



class FingerPrintLoader:
    def __init__(self, fingerPrinter, loaderId):
        self.fingerPrinter = fingerPrinter
        self.loaderId = loaderId

    def getLoaderId(self):
        return self.loaderId

    def loadFromSubDirectory(self, subDirectoryPath):
        # load data from directory
        baseDirectoryPath = self.fingerPrinter.getBaseDataDirectory() + "/"
        directoryPath = baseDirectoryPath + subDirectoryPath
        for rootPath, dirs, files in os.walk(directoryPath):
            for fileName in files:
                filePath = os.path.join(rootPath, fileName)
                self.processFoundFile(filePath, fileName, rootPath, directoryPath, baseDirectoryPath)

