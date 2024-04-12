# helper class that can scan directories for files with certain extensions (e.g images) so they can be referred to by their simple base name without path, canoncializing the name
# this can be useful for 2 reasons, first to make it EASIER for a person to reference files ilike images for inclusion; second for safety reasons so users cannot just refer to or include arbitrary files.

from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint

from os import walk
from pathlib import Path
import os



class JrFileFinder:
    def __init__(self, options):
        self.fileDict = {}
        self.useCount = {}
        self.extensionList = []
        self.directoryList = []
        self.onDuplicate = "error"
        #self.onDuplicate = "list"
        #self.onDuplicate = "replace"
        self.options = options


    def setExtensionList(self, inList):
        self.extensionList = inList
    def addExtensionList(self, inList):
        for i in inList:
            if (not i in self.extensionList):
                self.extensionList.append(i)
    def clearExtensionList(self):
        self.extensionList = []
    def addExtensionListImages(self):
        addList = [".png", ".jpg", ".jpeg", ".tiff", ".gif"]
        self.addExtensionList(addList)
    def addExtensionListPdf(self):
        addList = [".pdf"]
        self.addExtensionList(addList)

    def setDirectoryList(self, inList):
        self.directoryList = inList
    def addDirectoryList(self, inList):
        for i in inList:
            if (not i in self.directoryList):
                self.directoryList.append(i)
    def clearDirectoryList(self):
        self.directoryList = []





    def canonicalName(self, name):
        # canonicalize BOTH files found, AND names we look for, so that they are same format
        flagStripExtensions = self.options["stripExtensions"]

        # lowercase
        name = name.lower()

        # remove inc
        name = name.replace('incorporated' , 'inc.')

        # remove certain characters
        if (flagStripExtensions):
            name = name.replace('.','')
        name = name.replace("'",'')

        # strip spaces at start and end
        name = name.strip()

        # remove kludge info
        name = name.replace('_noborder','')

        # ending the
        if (name.endswith(', the')):
            name = name[0:len(name)-5]
        if (name.endswith(',the')):
            name = name[0:len(name)-4]

        # remove inc
        name = name.replace('incorporated' , 'inc')
        name = name.replace(', inc' , '')
        name = name.replace(' inc ' , '')
        if (name.endswith(' inc')):
            name = name[0:len(name)-4]

        # starting the
        if (name.startswith('the ')):
            name = name[4:]

        # remove some characters
        name = name.replace(',' , '')

        # strip spaces at start and end
        name = name.strip()

        # spaces to _
        name = name.replace(' ' , '_')

        return name


    def findImagesForName(self, name, flagMarkUsage):
        name = self.canonicalName(name)
        if (name in self.fileDict):
            if (name not in self.useCount):
                self.useCount[name] = 1
            else:
                self.useCount[name] += 1
            return self.fileDict[name]
        # not found
        return None


    def scanDirs(self, flagRemoveParentDir):
        self.fileDict = {}
        self.useCount = {}
        for i in self.directoryList:
            if (flagRemoveParentDir):
                self.scanDir(i, i)
            else:
                self.scanDir(i, "")


    def scanDir(self, directoryPath, parentPathToRemove):
        # scan directory and add any names found
        flagStripExtensions = self.options["stripExtensions"]
        jrprint('JrFileFinder (recursively) scanning directory "{}" for files ({})..'.format(directoryPath, self.extensionList))
        for (dirPath, dirNames, fileNames) in walk(directoryPath):
            for fileName in fileNames:
                baseName = Path(fileName).name
                baseNameNoExtension, fileExtension = os.path.splitext(baseName)

                fileExtension = fileExtension.lower()
                if (fileExtension not in self.extensionList) and (len(self.extensionList)>0):
                    # we dont want files of this extension
                    continue

                if (flagStripExtensions):
                    baseName = baseNameNoExtension

                if (parentPathToRemove!=''):
                    dirPathLink = dirPath.replace(parentPathToRemove,'')
                    filePath = dirPathLink + '/' + fileName
                else:
                    filePath = dirPath + '/' + fileName
                #
                baseName = self.canonicalName(baseName)

                if (baseName in self.fileDict):
                    # base name already found, so ADD this target image as a second option
                    if (self.onDuplicate == 'list'):
                        self.fileDict[baseName].append(filePath)
                    elif (self.onDuplicate == 'replace'):
                        self.fileDict[baseName] = [filePath]
                    else:
                        raise Exception("Got more than 1 file for JrFileFinder with the same base name: {}.".format(baseName))
                else:
                    # add it
                    self.fileDict[baseName] = [filePath]
                #
                jrprint('Adding entry for {} pointing to "{}".'.format(baseName, filePath))


    def reportUnusedImages(self):
        jrprint('JrFileFinder reportUnusedImages:')
        unusedCount = 0
        for k,v in self.fileDict.items():
            if (not k in self.useCount):
                unusedCount += 1
                jrprint('WARNING: JrFileFinder unused file: {}: {}.'.format(k,v))
        jrprint('Total # of unused files: {}.'.format(unusedCount))


