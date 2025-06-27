# helper class that can scan directories for files with certain extensions (e.g images) so they can be referred to by their simple base name without path, canoncializing the name
# this can be useful for 2 reasons, first to make it EASIER for a person to reference files ilike images for inclusion; second for safety reasons so users cannot just refer to or include arbitrary files.

from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
from lib.jr.jrfilefinder import JrFileFinder

from os import walk
from pathlib import Path
import os



class JrFileCleaner:
    def __init__(self, directories, extensions, recursive):
        self.directories = directories
        self.extensions = extensions
        self.recursive = recursive

        fileFinderOptions = {"stripExtensions": False}
        self.fileFinder = JrFileFinder(fileFinderOptions, "cleaning files", "unknown")
        self.fileFinder.addExtensionList(self.extensions)
        self.fileFinder.setDirectoryList(self.directories)

    def scanFiles(self):
        self.fileFinder.scanDirs(False)

    def deleteAllFiles(self, optionDryRun, excludeList, optionTruncateExcludes):
        return self.fileFinder.deleteAllFiles(optionDryRun, excludeList, optionTruncateExcludes)

    def deleteOneFile(self, path, optionDryRun, excludeList, optionTruncateExcludes):
        return self.fileFinder.deleteOneFile(path, optionDryRun, excludeList, optionTruncateExcludes)

    def getFileList(self):
        fileList = self.fileFinder.getFileListWithSizeAndTime()
        fileList = sorted(fileList, key=lambda x: x['fileTime'], reverse=True)
        return fileList

    def getFileListForDisplay(self):
        fileList = self.getFileList()
        fileListNice = []
        for f in fileList:
            fnice = {
                "baseName": f["baseName"],
                "path": f["path"],
                #"file": self.makeAHref(f["baseName"]),
                "size": jrfuncs.niceFileSizeStrRound(f["fileSize"]),
                "date": jrfuncs.niceFileDateStr(f["fileTime"]),
            }
            fileListNice.append(fnice)
        return fileListNice


    def makeAHref(self, path):
        ahref = '<a href="/">' + path + '</a>'
        return ahref