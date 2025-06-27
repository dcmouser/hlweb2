# class responsible for loading fingerprint images
# derived for my Anguli data

from .fingerprintloader import FingerPrintLoader

from lib.jr.jrfuncs import jrprint
from lib.jr import jrfuncs

# python imports
import os
import re




class FingerPrintLoaderAnguli(FingerPrintLoader):
    def __init__(self, fingerPrinter, loaderId):
        super().__init__(fingerPrinter, loaderId)


    def processFoundFile(self, filePath, fileName, rootPath, directoryPath, baseDirectoryPath):
        jrprint("Examining {} ({})'..".format(fileName, filePath))
        # for our personal Anguli data directory setup, here is what we expect:
        # at top level after directoryPath we have a directory name of the form FingerprintsXXXX where XXXX is the fingerprint CLASS (whore, arch, etc.)
        # under that we have a subdirectory "Fingerprints" which we ignore (base fingerprint pattern)
        # and a subdirectory "Meta Info" which we also ignore
        # so we only want files under directories starting with "Impression_"
        # for each of those we can find the matching Meta Info file and extrac the fingerprint type (rather than using directory path)
        # we compute a fingerId from path minus the Impression_#
        # and use Impression_1 for the clean finger image and the rest for dirty impression_N
        #
        optionLoadTypeFromMetaFile = True

        # remove base path so we only have relative
        relativePath = rootPath.replace(directoryPath,"")
        # canonicalize
        relativePath = relativePath.replace("\\","/")
        if (relativePath.startswith("/")):
            relativePath = relativePath[1:]
        # split
        pathParts = relativePath.split("/")
        baseName, extension = os.path.splitext(fileName)
        if (extension not in [".jpg",".png"]):
            # ignore it
            return False
        # ok we got an image
        topName = pathParts[0].replace("Fingerprints","")
        setName = pathParts[-1]
        groupName = pathParts[-2]
        if (not groupName.startswith("Impression_")):
            # no interest to us
            return False
        impressionId = groupName.replace("Impression_","")
        fingerprintSetNumber = int(setName.replace("fp_",""))
        #
        fingerUniqueId = self.getLoaderId() + "_" + topName + "Dir_" + str(fingerprintSetNumber) + "." + baseName
        #
        # get fingerprint type from meta file
        if (not optionLoadTypeFromMetaFile):
            fingerprintType = topName
        else:
            metaFilePath = directoryPath + "/" + pathParts[0] + "/Meta Info/" + setName + "/" + baseName + ".txt"
            fingerprintType = self.calcFingerprintTypeInMetaFile(metaFilePath)
        #
        jrprint("..Storing fingerid '{}', impression #{}.{} : '{}' [type={}].".format(fingerUniqueId, impressionId, fingerprintSetNumber, fileName, fingerprintType))
        # store it in fingerPrinter
        filePathRelative = filePath.replace(baseDirectoryPath,"")
        filePathRelative = filePathRelative.replace("\\","/")
        fingerProps = {"type": fingerprintType}
        self.fingerPrinter.getFingerManager().storeFingerprintImageFile(fingerUniqueId, impressionId, filePathRelative, fingerProps)



    def calcFingerprintTypeInMetaFile(self, metaFilePath):
        metaData = jrfuncs.loadTxtFromFile(metaFilePath, True)
        if (metaData is None):
            raise Exception("Meta file for fingerprint not found: '{}'.".format(metaFilePath))
        matches = re.match(r".*Type : (.*)$", metaData, re.MULTILINE)
        if (matches is None):
            return "UNKNOWN"
        fingerprintType = matches.group(1)
        # remove spaces
        fingerprintType = fingerprintType.replace(" ","")
        return fingerprintType


