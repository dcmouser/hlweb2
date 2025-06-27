# main class that manages fingerprint tasks

# basic workflow/taks:
# 1. LOAD fingerprint data from different sources, store it internally
# 2. CREATE virtual people and their fingerprints using distributions
# 3. Build fingerprint directories
# 4. API to return specific fingerprint images for use in an application/game

# our modules
from .virtualfinger import VirtualFingerManager
from .virtualperson import VirtualPersonManager, VirtualPerson
#
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint

# python modules
import os
import random
import json



DefVersionString = "v1.2 (6/4/25)"
DefAuthorString = "Jesse Reichler <jessereichler@gmail.com>"








class FingerPrinter:
    def __init__(self, baseDataDirectory):
        self.baseDataDirectory = baseDataDirectory
        self.personManager = VirtualPersonManager()
        self.fingerManager = VirtualFingerManager()
        self.availableFingers = {}
        #
        self.options = {
            "fingersPerPerson": 10,
            "typeDistribution": {
                "Whorl": 25,
                "RightLoop": 30,
                "LeftLoop": 20,
                "DoubleLoop": 15,
                "Arch": 7,
                "TentedArch": 3,
            }
        }
        self.cachedTypeWeights = {}

    def getFingerManager(self):
        return self.fingerManager
    
    def getBaseDataDirectory(self):
        return self.baseDataDirectory
    
    def makeRelativeImageFileAbsolute(self, fpath):
        return self.getBaseDataDirectory() + "/" + fpath

    def getFingerImpressionAsAbsoluteLatexPath(self, finger, impressionIndex):
        impression = finger.getImpressionByIndex(impressionIndex)
        path = self.makeRelativeImageFileAbsolute(impression["path"])
        latexPath = path.replace("\\","/")
        return latexPath

    @staticmethod
    def getStaticSourceTemplateDirectoryPath():
        currentDirectory = os.path.dirname(os.path.realpath(__file__))
        return currentDirectory + "/templates"

    @staticmethod
    def getStaticSourceDataDirectoryPath():
        currentDirectory = os.path.dirname(os.path.realpath(__file__))
        return currentDirectory + "/data"

    @staticmethod
    def getFingerprintImageDirectoryPath():
        currentDirectory = os.path.dirname(os.path.realpath(__file__))
        return currentDirectory + "/data"






    def createVirtualPeople(self, numPeople, leadIds, dNames, pcats):
        self.prepareForAssignments()
        for personId in range(0,numPeople):
            jrprint("Fingerprinter creating virtual person #{}...".format(personId))
            if (leadIds is None):
                personLeadId = self.generateRandomFakeLeadId()
            else:
                personLeadId = leadIds[personId]
                personDname = dNames[personId]
                personPcat = pcats[personId]
            #
            person = VirtualPerson(personId, personLeadId, personDname, personPcat)
            self.personManager.addPerson(person, personId)
            # add fingers
            self.assignFingersToPerson(person)
        # now SORT by person id
        self.personManager.sortByLeadId()




    def prepareForAssignments(self):
        # prepare structures to do probability distribution assignments
        self.availableFingers = self.fingerManager.buildClassFingerDict()
        # cache
        dist = self.options["typeDistribution"]
        weights = dist.values()
        sumWeight = sum(weights)
        probs = [w/sumWeight for w in weights]
        self.cachedTypeWeights = {
            "choices": list(dist.keys()),
            "probs": probs,
        }



    def assignFingersToPerson(self, person):
        numFingers = self.options["fingersPerPerson"]
        for fingerNum in range(0,numFingers):
            finger = self.chooseAvailableFinger()
            person.assignFinger(fingerNum, finger)
    

    def chooseAvailableFinger(self):
        # choose a virtual finger to assign using probabilities
        # step 1 choose a weighted type
        fingerClassType = self.weightedChooseFingerprintClassType()
        # step 2 choose one from available
        availables = self.availableFingers[fingerClassType]
        numAvailable = len(availables)
        if (numAvailable==0):
            raise Exception("Could not create virtual finger of type {} as none are left.".format(numAvailable))
        index = random.randint(0, numAvailable-1)
        # get it and remove it so it won't be chosen again
        finger = availables.pop(index)
        # return it
        return finger


    def weightedChooseFingerprintClassType(self):
        # helper (we put this import here so we dont need numpy imported unless we are GENERATING fingerprints (as opposed to looking them up in a runtime use))
        # ATTN: this generates a problem in IDE when numpy is not known buts its a non-issue
        import numpy.random as npr
        #
        choices = self.cachedTypeWeights["choices"]
        probs = self.cachedTypeWeights["probs"]
        index = npr.choice(len(choices), p=probs)
        category = choices[index]
        return category

















    def buildFingerprintDirectory(self, outFilePath, extraPreamble, templateName, flagNonAnonymous, flagAnonymous):
         # open file
         jrprint("Writing fingerprint directory to: {}.".format(outFilePath))
         filep = open(outFilePath, 'w')
         # write part 0 preamble
         self.buildFingerprintDirectoryPreamble(filep, extraPreamble, templateName)
         # write part 2 (by class)
         self.buildFingerprintDirectoryClasses(filep, flagNonAnonymous, flagAnonymous)
         # write part 1 (by person)
         self.buildFingerprintDirectoryPersons(filep, flagNonAnonymous, flagAnonymous)
         # end
         self.buildFingerprintDirectoryEnd(filep)
         filep.close()


    def buildFingerprintDirectoryPreamble(self, filep, extraPreamble, templateName):
        latex = r"% FINGERPRINT DIRECTORY BUILD " + DefVersionString + "\n\n"
        #
        if (extraPreamble is not None):
            latex += extraPreamble + "\n\n\n\n"
        else:
            latex += r"\newcommand\hlDataVersion{1.0} \newcommand\hlDataDate{12/17/24} \newcommand\hlBuildVersion{1.0} \newcommand\hlBuildDate{12/17/24} " + "\n\n\n\n"

        #
        latex += jrfuncs.loadTxtFromFile(FingerPrinter.getStaticSourceTemplateDirectoryPath() + "/" + templateName + ".latex", True)
        filep.write(latex)
    
    def buildFingerprintDirectoryEnd(self, filep):
        latex = "\n" + r"\end{document}" + "\n"
        filep.write(latex)



    def buildFingerprintDirectoryPersons(self, filep, flagNonAnonymous, flagAnonymous):
        latex = r"\cleardoublepage" + "\n\n\n" + r"\centering\section*{" + "SUSPECTS SECTION" + "}" + "\n\n"
        #latex += "Hands: L=Left, R=Right\n\n"
        #latex += "Fingers: 1=Thumb, 2=Index, 3=Middle, 4=Ring, 5=Pinky\n\n"
        #latex += "\nNOTE: Suspect Lead ID Number is shown under L1.\n\n"
        filep.write(latex)
        # FUCK OFF LATEX
        if (True):
            latex = r"\addcontentsline{toc}{section}{SUSPECTS SECTION}" + "\n"
            filep.write(latex)
        #
        latex = r"\newpage" + "\n"
        filep.write(latex)
        #
        for personId, person in self.personManager.getPersons().items():
            isAnonymous = person.getIsAnonymous()
            if (flagNonAnonymous and (not isAnonymous)) or (flagAnonymous and isAnonymous):
                self.writeFingerprintDirectoryPerson(person, filep, True)
        #
        #latex = r"\end{NoHyper}" + "\n"
        #filep.write(latex)



    def writeFingerprintDirectoryPerson(self, person, filep, optionShowId):
        if (optionShowId):
            caption = person.getCaption()
        else:
            caption = None
        #
        latex = self.buildFingerprintDirectoryPerson(person, caption, True, False)
        # write it
        filep.write(latex)



    def buildFingerprintDirectoryPerson(self, person, caption, optionAddToc, flagCompact):
        officialFingerprintIndex = 1
        latex = ""

        # the fingers of the person
        fingerList = person.getFingers()

        if (flagCompact):
            styleSuffix = "C"
            latex += r"\setFingerPrintSetWidthCompact" + "\n"
        else:
            styleSuffix = ""
            latex += r"\setFingerPrintSetWidthNormal" + "\n"

        if (caption=="leadId"):
            caption = person.getCaption()
        if (optionAddToc and (caption is not None)):
            latex += r"\phantomsection\addcontentsline{toc}{subsection}{" + caption + "}" + "\n"

        # left
        latex += r"\myfpersontableSetLeft"
        latex += "{" + self.getFingerImpressionAsAbsoluteLatexPath(fingerList[0], officialFingerprintIndex) + "}%\n"
        latex += "{" + self.getFingerImpressionAsAbsoluteLatexPath(fingerList[1], officialFingerprintIndex) + "}%\n"
        latex += "{" + self.getFingerImpressionAsAbsoluteLatexPath(fingerList[2], officialFingerprintIndex) + "}%\n"
        latex += "{" + self.getFingerImpressionAsAbsoluteLatexPath(fingerList[3], officialFingerprintIndex) + "}%\n"
        latex += "{" + self.getFingerImpressionAsAbsoluteLatexPath(fingerList[4], officialFingerprintIndex) + "}%\n"
        # right
        latex += r"\myfpersontableSetRight"
        latex += "{" + self.getFingerImpressionAsAbsoluteLatexPath(fingerList[5], officialFingerprintIndex) + "}%\n"
        latex += "{" + self.getFingerImpressionAsAbsoluteLatexPath(fingerList[6], officialFingerprintIndex) + "}%\n"
        latex += "{" + self.getFingerImpressionAsAbsoluteLatexPath(fingerList[7], officialFingerprintIndex) + "}%\n"
        latex += "{" + self.getFingerImpressionAsAbsoluteLatexPath(fingerList[8], officialFingerprintIndex) + "}%\n"
        latex += "{" + self.getFingerImpressionAsAbsoluteLatexPath(fingerList[9], officialFingerprintIndex) + "}%\n"

        #
        latex += r"\myfpersontable" + styleSuffix
        if (caption is not None):
            latex += "{" + caption + "}\n"
        else:
            latex += "{}\n"

        latex += "\n"

        # write it
        return latex





    def buildFingerprintDirectoryClasses(self, filep, flagNonAnonymous, flagAnonymous):
        # iterate each class (starting a new page for each)
        # FUCK OFF LATEX
        if (True):
            latex = r"\phantomsection\addcontentsline{toc}{section}{FINGERPRINT CLASSES}" + "\n"
            filep.write(latex)
        #
        classTypeStrings = self.options["typeDistribution"].keys()
        for classTypeString in classTypeStrings:
            self.buildFingerprintDirectoryClass(filep, classTypeString, flagNonAnonymous, flagAnonymous)


    def buildFingerprintDirectoryClass(self, filep, classTypeString, flagNonAnonymous, flagAnonymous):
        latex = ""
        classNameToCaption = {
                "Whorl": "Whorls",
                "RightLoop": "Right Loops",
                "LeftLoop": "Left Loops",
                "DoubleLoop": "Double Loops / Double Whorls",
                "Arch": "Plain Arches",
                "TentedArch": "Tented Arches",
        }
        classCaption = classNameToCaption[classTypeString]
        #classCaptionLatexSafe = classCaption.replace("/","//")
        latex += r"\cleardoublepage" + "\n" + r"\subsection*{" + classCaption + "}" + "\n"
        latex += r"\addcontentsline{toc}{subsection}{" + classCaption + "}" + "\n"
        filep.write(latex)
        # build the list of USED fingerprints of this class
        usedFingers = self.personManager.buildAndOwnUsedFingersMatchingClassType(classTypeString)
        # now display them in a nice table
        self.buildFingerprintDirectoryTable(filep, usedFingers, flagNonAnonymous, flagAnonymous)


    def buildFingerprintDirectoryTable(self, filep, fingerList, flagNonAnonymous, flagAnonymous):
        # ATTN: code duplication, combine
        officialFingerprintIndex = 1
        latex = ""
        perRow = 5

        startLatex = r"\begin{myfprowtable}" + "\n"
        endLatex = "\n" + r"\end{myfprowtable}" + "\n\n"

        # the fingers of the person
        latex += startLatex
        rowIndex = 0
        totIndex = 0
        for index, finger in enumerate(fingerList):          
            impression = finger.getImpressionByIndex(officialFingerprintIndex)
            imagePath = self.makeRelativeImageFileAbsolute(impression["path"])
            imagePath = imagePath.replace("\\","/")
            isAnonymous = finger.getIsAnonymous()
            if (not flagNonAnonymous) and (not isAnonymous):
                # in anonymous directory mode we dont show the fingerprint at all
                continue
            if (flagAnonymous and isAnonymous):
                imageCaption = finger.getPlayerCaptionPlus()
            elif (flagNonAnonymous and (not isAnonymous)):
                imageCaption = finger.getCaption()
            else:
                # anonymize it
                #imageCaption = "X-XXXX"
                imageCaption = finger.getPlayerCaption()
            #
            if (rowIndex==perRow):
                # make a new row
                latex += endLatex + startLatex
                rowIndex = 0
            elif (totIndex>0):
                latex += " &\n"
            #
            latex += r"\fpimage{" + imagePath + "}" + "{" + imageCaption + "}"
            rowIndex += 1
            totIndex += 1
    
        latex += endLatex

        # write it
        filep.write(latex)




    def generateRandomFakeLeadId(self):
        # ATTN: test
        leadId = "F{}-{}{}{}{}".format(random.randint(1, 9), random.randint(1, 9), random.randint(0, 9), random.randint(0, 9), random.randint(0, 9))
        return leadId

















    def saveData(self, dataFilePath):
        jrprint("Saving fingerprint data to {}..", format(dataFilePath))
        # note that what we save are the virtual people and their fingers; we dont care about unused image files, etc.
        # so self.personManager
        personManagerData = self.personManager.serializeData()
        data = {"personManagerData": personManagerData}
        # write it to file
        jrfuncs.saveJsonToFile(dataFilePath, data, "utf-8")
        # check for any problems
        self.personManager.checkForProblems()


    def loadData(self, dataFilePath):
        debugMode = False
        if (debugMode):
            jrprint("Loading fingerprint data from {}..", format(dataFilePath))
        # note that what we save are the virtual people and their fingers; we dont care about unused image files, etc.
        # lead from file
        data = jrfuncs.loadJsonFromFile(dataFilePath, True, "utf-8")
        personManagerData = data["personManagerData"]
        self.personManager.unSerializeData(personManagerData)
        #self.personManager.checkForProblems()



