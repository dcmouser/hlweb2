# helper class that can scan directories for files with certain extensions (e.g images) so they can be referred to by their simple base name without path, canoncializing the name
# this can be useful for 2 reasons, first to make it EASIER for a person to reference files ilike images for inclusion; second for safety reasons so users cannot just refer to or include arbitrary files.

from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint

from os import walk
from pathlib import Path
import os



class JrFileFinder:
    def __init__(self, options, sourceLabel):
        self.fileDict = {}
        self.useCount = {}
        self.extensionList = []
        self.directoryList = []
        self.onDuplicate = "error"
        #self.onDuplicate = "list"
        #self.onDuplicate = "replace"
        self.options = options
        self.sourceLabel = sourceLabel

    def getSourceLabel(self):
        return self.sourceLabel

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

    def setDirectoryList(self, inDirList):
        self.directoryList = inDirList
    def addDirectoryList(self, inDirList):
        for i in inDirList:
            if (not i in self.directoryList):
                self.directoryList.append(i)
    def clearDirectoryList(self):
        self.directoryList = []

    def resetUsageCount(self):
        self.useCount = {}
    
    def getCount(self):
        return len(self.fileDict)



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

    def findFullPath(self, name, flagMarkUsage=False, flagRevertToPrefix=False):
        paths = self.findImagesForName(name, flagMarkUsage, flagRevertToPrefix)
        if (paths is None) or (len(paths)==0):
            return None
        path = paths[0]
        path = path.replace("\\" , "/")
        return path


    def findImagesForName(self, name, flagMarkUsage, flagRevertToPrefix):
        name = self.canonicalName(name)

        if (not name in self.fileDict) and (flagRevertToPrefix):
            # try to find a prefix
            sname = name + '_'
            for k,v in self.fileDict.items():
                if (k.startswith(sname)):
                    # got a prefix
                    name = k
                    break

        if (name in self.fileDict):
            if (flagMarkUsage):
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
            prefix = i['prefix']
            path = i['path']
            if (flagRemoveParentDir):
                self.scanDir(path, path, prefix)
            else:
                self.scanDir(path, "", prefix)


    def scanDir(self, directoryPath, parentPathToRemove, prefix):
        # scan directory and add any names found

        if (prefix!=''):
            prefixAdd = prefix + '/'
        else:
            prefixAdd = ''

        flagStripExtensions = self.options["stripExtensions"]
        #jrprint('JrFileFinder (recursively) scanning directory "{}" for files ({})..'.format(directoryPath, self.extensionList))
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
                fullDirPath = os.path.join(dirPath, baseName)
                relPath = jrfuncs.replaceInitialDirectoryPath(fullDirPath, directoryPath)
                relPath = jrfuncs.canonicalFilePath(relPath)
                baseName = prefixAdd + relPath

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
                #jrprint('Adding entry for {} pointing to "{}".'.format(baseName, filePath))




    def reportUnusedImages(self):
        jrprint('JrFileFinder reportUnusedImages:')
        unusedCount = 0
        for k,v in self.fileDict.items():
            if (not k in self.useCount):
                unusedCount += 1
                jrprint('WARNING: JrFileFinder unused file: {}: {}.'.format(k,v))
        jrprint('Total # of unused files: {}.'.format(unusedCount))


    def getUnusedFiles(self):
        unusedItemList = []
        for k,v in self.fileDict.items():
            if (not k in self.useCount):
                path = v[0]
                path = path.replace("\\" , "/")
                unusedItemList.append([k, path])
        return unusedItemList