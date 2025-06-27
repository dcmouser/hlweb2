# imports
from lib.jr import jrfuncs
from lib.jr import jroptions
from lib.jr.jrfuncs import jrprint
from lib.jr.jrfuncs import jrException
from lib.jr.jrhashrange import stringToFeistelRange
#
from lib.fingerprinter.fingerprinter import FingerPrinter

# python imports
import csv
import os
import pathlib
import json
from difflib import SequenceMatcher
from pathlib import Path
import random
import re



# ---------------------------------------------------------------------------
class HlApi:
    def __init__(self, baseDataDir, options={}):
        if (baseDataDir is None):
            baseDataDir = self.getThisSourceDirectory() + "/hldata"
        #
        self.baseDataDir = baseDataDir
        self.options = options
        #
        self.unusedLeads = None
        self.leads = None
        self.regionData = None
        #
        self.usedLeads = []
        self.usedLeadIds = []
        self.previousUnusedHashKeys = []
        self.disabled = False
        self.flagDebug = False
        #
        self.fingerprinter = None
        #
        self.reservedLeads = []

    def getThisSourceDirectory(self):
        source_path = Path(__file__).resolve()
        source_dir = source_path.parent
        return str(source_dir)

    def isEnabled(self):
        return (not self.disabled) and (('enabled' not in self.options) or (self.options['enabled']))

    def enableSlowSearch(self):
        return ('disableSlowSearch' not in self.options) or (not self.options['disableSlowSearch'])

    def loadLeadsIfNeeded(self):
        if (not self.isEnabled()):
            return False
        if (self.leads is None):
            self.loadLeads()
        if (self.unusedLeads is None):
            self.loadUnusedLeadsFromFile()
        return True

    def setDisabled(self, val):
        self.disabled = val

    def configure(self, options):
        # overwrite options with new
        jrfuncs.deepMergeOverwriteA(self.options, options)
        # force reload
        self.unusedLeads = None

    def calcDataDir(self):
        if ("dataVersion" not in self.options):
            return None
        dataVersion = self.options["dataVersion"]
        dataDir = self.baseDataDir + "/" + dataVersion
        jrfuncs.createDirIfMissing(dataDir)
        return dataDir

    def calcDataParentDir(self):
        return self.getThisSourceDirectory() + "/hldata"

    def getVersion(self):
        return self.options["dataVersion"]

    def getUsedLeads(self):
        return self.usedLeads

    def getOption(self, key, defaultVal):
        return jrfuncs.getDictValueOrDefault(self.options, key, defaultVal)



# ---------------------------------------------------------------------------
    def loadUnusedLeadsFromFile(self):
        unUsedLeadRowList = []
        dataDir = self.calcDataDir()
        if (dataDir is None):
            return False
        
        # kludge; support for unused lead generators
        dataVersion = self.options["dataVersion"]
        generatedUnusedLeads = self.generateUnusedLeadsUsingPattern(dataVersion)
        if (generatedUnusedLeads is not None):
            # use this list
            for leadId in generatedUnusedLeads:
                if (leadId in self.reservedLeads):
                    # this lead is reserved so dont add it
                    pass
                else:
                    unUsedLeadRowList.append({"lead":str(leadId)})
        else:
            filePath = dataDir + '/unusedLeads.csv'
            with open(filePath) as csvFile:
                csvReader = csv.DictReader(csvFile)
                for row in csvReader:
                    if (row["lead"] in self.reservedLeads):
                        # this lead is reserved so dont add it
                        pass
                    else:
                        unUsedLeadRowList.append(row)
            if (self.flagDebug):
                jrprint('{} unused leads read from "{}"'.format(len(unUsedLeadRowList), filePath))

        # post processing of unused lead rows
        self.postProcessLoadedUnusedLeads(unUsedLeadRowList)

        return True
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
    def postProcessLoadedUnusedLeads(self, unUsedLeadRowList):
        # random shuffle using seed for predictability?
        # ATTN: we no longer do this
        if (False):
            prng = random.Random(self.getSeed())
            prng.shuffle(self.unusedLeads)
        # itereate list of unused rows and build disctionary by lead
        self.unusedLeads = {}
        for row in unUsedLeadRowList:
            leadId = row["lead"]
            self.unusedLeads[leadId] = row
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def getSeed(self):
        return self.getOption("seed", 0)

    def reserveLead(self, id):
        if (not self.isEnabled()):
            return False
        self.reservedLeads.append(id)
        # if not loaded yet, then return
        if (self.unusedLeads is None):
            return True
        # already loaded, so remove now
        if (id in self.unusedLeads):
            del self.unusedLeads[id]
            return True
        return False
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def loadLeads(self):      
        self.leads = {}
        if (not self.isEnabled()):
            return False

        dataDir = self.calcDataDir()
        if (dataDir is None):
            return False

        # try to load all in one, then fall back to indivdual jsons (old method)
        fileFinishedPath = dataDir + "/leadsCombined/places_formap_allinone.json"
        if False and (jrfuncs.pathExists(fileFinishedPath)):
            # no longer do this because we need to know what files these come from when we write out
            baseName = pathlib.Path(fileFinishedPath).stem
            self.loadLeadFile(fileFinishedPath, baseName)
        else:
            filePath = dataDir + "/leads"
            for (dirPath, dirNames, fileNames) in os.walk(filePath):
                for fileName in fileNames:
                    fileNameLower = fileName.lower()
                    if (fileNameLower.endswith('.json')):
                        baseName = pathlib.Path(fileName).stem
                        fileFinishedPath = dirPath + '/' + fileName
                        self.loadLeadFile(fileFinishedPath, baseName)

        filePath = dataDir + "/other"
        fileFinishedPath = filePath + '/regions.json'
        self.loadRegionFile(fileFinishedPath)

        return True


    def loadLeadFile(self, filePath, fileSourceLabel):
        #jrprint('Loading leads from "{}" ({})..'.format(fileSourceLabel, filePath))
        encoding='utf-8'
        with open(filePath, 'r', encoding=encoding) as jsonFile:
            jsonRows = json.load(jsonFile)
            features = jsonRows['features']
            rows = []
            for row in features:
                #thisRow = row['properties']
                rows.append(row)

            if (self.flagDebug):
                jrprint('Loaded {} leads from "{}" ({})'.format(len(features), fileSourceLabel, filePath))
            self.leads[fileSourceLabel] = rows


    def loadRegionFile(self, filePath):
        #jrprint('Loading region data from "{}"..'.format(filePath))
        encoding='utf-8'
        self.regionData = []
        with open(filePath, 'r', encoding=encoding) as jsonFile:
            jsonRows = json.load(jsonFile)
            features = jsonRows['features']
            rows = []
            for row in features:
                rows.append(row)
            if (self.flagDebug):
                jrprint('Loaded {} regions from "{}"'.format(len(features), filePath))
            self.regionData = rows





    def findLeadRowByLeadId(self, leadId):
        if (not self.isEnabled()):
            return [None, None]
        
        if (not self.loadLeadsIfNeeded()):
            return [None,None]

        if (leadId.startswith('#')):
            leadId = leadId[1:]
        #
        for sourceKey, leadRows in self.leads.items():
            for row in leadRows:
                if (row['properties']['lead']==leadId):
                    return [row, sourceKey]
        # not found
        return [None, None]


    def findLeadRowByNameOrAddress(self, txt):
        if (not self.isEnabled()):
            return [None, None]
        #if (not self.enableSlowSearch()):
        #    return [None, None, 0]
        txt = txt.strip()
        if (txt==''):
            return [None, None]

        if (not self.loadLeadsIfNeeded()):
            return [None,None]

        for sourceKey, leadRows in self.leads.items():
            for row in leadRows:
                rowProperties = row['properties']
                if (rowProperties['address']==txt) or (rowProperties['dName']==txt) or (rowProperties['lead']==txt):
                    # found it
                    return [row, sourceKey]
        # not found
        return [None, None]





    def findLeadRowSimilarByNameOrAddress(self, txt):
        if (not self.isEnabled()):
            return [None, None, 0]
        if (not self.enableSlowSearch()):
            return [None, None, 0]
        txt = txt.strip()
        if (txt==''):
            return [None, None]

        if (not self.loadLeadsIfNeeded()):
            return [None,None]

        # walk ALL and find max
        txtUpper = txt.upper()
        startLen = 5 
        maxDist = 0
        maxMatchRow = None
        maxMatchSourceKey = None
        for sourceKey, leadRows in self.leads.items():
            for row in leadRows:
                distName = SequenceMatcher(None, txt, row['properties']['dName']).ratio()
                distAddr = SequenceMatcher(None, txt, row['properties']['address']).ratio()
                # kludge for startswith
                if (txtUpper.startswith(row['properties']['dName'][0:startLen].upper())):
                    distName += 0.5
                thisMaxDist = max(distName, distAddr)
                if (thisMaxDist > maxDist):
                    maxDist = thisMaxDist
                    maxMatchRow = row
                    maxMatchSourceKey = sourceKey
        # not found
        return [maxMatchRow, maxMatchSourceKey, maxDist]
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    # helper function
    def leadRowHasSimilarLabel(self, leadRow, proposedLabel):
        if (proposedLabel is None) or (proposedLabel == ""):
            return False

        leadRowProperties = leadRow["properties"]
        dName = leadRowProperties["dName"]
        dNameLower = self.standardizeLabelForCompare(dName)
        proposedLabelLower = self.standardizeLabelForCompare(proposedLabel)
        if (dNameLower in proposedLabelLower) or (proposedLabelLower in dNameLower):
            return True
        # try firstname lastname?
        firstName = leadRowProperties["firstName"]
        if (firstName is not None) and (firstName!=""):
            lastName = leadRowProperties["lastName"]
            dName = firstName + " " + lastName
            dNameLower = self.standardizeLabelForCompare(dName)
            if (dNameLower in proposedLabelLower) or (proposedLabelLower in dNameLower):
                return True
            # first initial only? (at start or end)
            dName = firstName[0] + " " + lastName
            dNameLower = self.standardizeLabelForCompare(dName)
            if (dNameLower in proposedLabelLower) or (proposedLabelLower in dNameLower):
                return True
            dName = lastName + firstName[0]
            dNameLower = self.standardizeLabelForCompare(dName)
            if (dNameLower in proposedLabelLower) or (proposedLabelLower in dNameLower):
                return True
        return False


    def standardizeLabelForCompare(self, text):
        text = text.lower()
        text = text.replace(",","")
        text = text.replace(".","")
        text = text.replace(" ","")
        text = text.replace("’","'") # keep apostrophes but normalize unicode ones
        text = text.replace("“","\"") # standardize unicode quotes
        text = text.replace("”","\"") # standardize unicode quotes
        #text = text.replace("'","")
        return text

    def getNiceFullLabelWithAddress(self, leadRow):
        dName = leadRow["properties"]["dName"]
        [address, addressWithApt] = self.getNiceAddress(leadRow, ["abbreviation","loclabel"], False)
        label = "{} ({})".format(dName, addressWithApt)
        return label


    def getNiceAddress(self, leadRow, neighborhoodOptions, flagHidePrivate):
        leadRowProperties = leadRow["properties"]
        listype  = leadRowProperties["listype"]
        if (flagHidePrivate) and (listype=="private"):
            return ""
        #
        address = leadRowProperties["address"]
        jregion = leadRowProperties["jregion"]
        if ("loclabel" in leadRowProperties):
            loclabel = leadRowProperties["loclabel"]
        else:
            loclabel = None

        # add apt
        apt = leadRowProperties["apt"]
        if (apt is not None) and (apt!="") and (apt!="nan"):
            aptPart = " (apt. " + apt + ")"
        else:
            aptPart = ""

        if ("noneighborhood" in neighborhoodOptions):
            retAddress = address
        elif ("abbreviation" in neighborhoodOptions):
            if (address!=""):
                retAddress = address + ", " + jregion
            else:
                retAddress = jregion
            if ("loclabel" in neighborhoodOptions) and (loclabel is not None):
                retAddress += "-" + loclabel
        else:
            if (address!=""):
                retAddress = address + ", " + self.jregionToNeighborhoodLabel(jregion)
            else:
                retAddress = self.jregionToNeighborhoodLabel(jregion)
            if ("loclabel" in neighborhoodOptions) and (loclabel is not None):
                retAddress += " #" + loclabel
        #
        return [retAddress, retAddress+aptPart]


    def jregionToNeighborhoodLabel(self, jregion):
        for row in self.regionData:
            if (row['properties']['jregion']==jregion):
                return row['properties']['jlabel']
        return jregion
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
    # write out a set of json sets of leads used by the case
    # we want one file that has ALL referenced leads (for mapping)
    # but then 2 more userWhite and userYellow which ONLY include leads from the yellow and people dbs which are from randomly generated json files, so that they can be merged into manual userWhite and userYellow files
    # in all cases we want to add a forceSourceLabel to show where they are used
        
    def writeOutUsedLeadJsons(self, saveDir, baseFilename, forceSourceLabel):
        fileList = []
        fictionalSourceList = self.getFictionalLeadSourceNameList()
        leadFeatures = {}

        #if (len(self.usedLeads) == 0):
        #    return []

        jrfuncs.createDirIfMissing(saveDir)

        for usedItem in self.usedLeads:
            fileSource = usedItem["source"]
            existingLeadRow = usedItem["row"]
            existingLeadRowProperties = existingLeadRow['properties']
            #
            source = existingLeadRowProperties['source'] if ('source' in existingLeadRowProperties) else fileSource
            ptype = existingLeadRowProperties['ptype']
            #
            # build copy of row (copy so we can add/change props)
            propCopy = jrfuncs.deepCopyListDict(existingLeadRowProperties)
            # add items
            propCopy['jfrozen'] = 110
            propCopy['source'] = forceSourceLabel
            # build new row
            geometry = existingLeadRow['geometry']
            featureRow = {"type": "Feature", "properties": propCopy, "geometry": geometry}

            # add only fictional to special fictional files
            if (source in fictionalSourceList):
                # add it to save list
                if (ptype not in leadFeatures):
                    leadFeatures[ptype] = []
                #
                leadFeatures[ptype].append(featureRow)

            # add ALL rows to formap, and this time also add geometry
            fname = 'allForMap'
            if (fname not in leadFeatures):
                leadFeatures[fname] = []
            leadFeatures[fname].append(featureRow)     

        if (True):
            # lets ALWAYS write out these two files (empty versions) just so we KNOW when they are intentionally black
            emptyList = ["person", "yellow"]
            for i in emptyList:
                if (i not in leadFeatures):
                    leadFeatures[i+"_empty"] = []

        # save
        jrfuncs.createDirIfMissing(saveDir)

        # delete previous even if we dont generate them
        for ptype in fictionalSourceList:
            outFilePath = self.makeLeadDbOutFilePath(saveDir, baseFilename, ptype)
            jrfuncs.deleteFilePathIfExists(outFilePath)
        
        encoding = "utf-8"
        usedLeadCount = len(self.usedLeads)
        for ptype, features in leadFeatures.items():
            outFilePath = self.makeLeadDbOutFilePath(saveDir, baseFilename, ptype)
            # we write it out with manual text so that we can line break in customized way
            with open(outFilePath, 'w', encoding=encoding) as outfile:
                text = '{\n"type": "FeatureCollection",\n"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::2263" } },\n"features": [\n'
                outfile.write(text)
                numRows = len(features)
                for i, row in enumerate(features):
                    json.dump(row, outfile)
                    if (i<numRows-1):
                        outfile.write(',\n')
                    else:
                        outfile.write('\n')
                text = ']\n}\n'
                outfile.write(text)
            #
            fileList.append(outFilePath)
            if (self.flagDebug):
                jrprint('   wrote {} of {} leads to {}.'.format(len(features), usedLeadCount, outFilePath))

        return fileList



    def makeLeadDbOutFilePath(self, saveDir, baseFilename, ptype):
        return saveDir + '/{}_dbuserleads_{}.json'.format(baseFilename, ptype)


    def getFictionalLeadSourceNameList(self):
        return ['yellow', 'places_yellow', 'people', 'places_people', 'person']


    def isLeadRowSourceFromVolatileDb(self, sourceKey):
        fictionalSourceList = self.getFictionalLeadSourceNameList()
        if (sourceKey in fictionalSourceList):
            return True
        return False
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
    def getLoadFingerprinter(self):
        if (self.fingerprinter is None):
            # create it
            fpSavedDataPath = self.calcDataDir() + "/fingerprintData/fingerprintData.json"
            # and directory where images are based off of (we could change this to use dif directory for data versions)
            #baseFingerprintDirectory = self.calcDataDir() + "/fingerprintData"
            baseFingerprintDirectory = FingerPrinter.getStaticSourceDataDirectoryPath()
            self.fingerprinter = FingerPrinter(baseFingerprintDirectory)
            # load data about fingerprint people
            self.fingerprinter.loadData(fpSavedDataPath)

        # return it
        return self.fingerprinter


    def lookupFingerprintPerson(self, id):
        # return [relativePath, imageFullPath]
        fp = self.getLoadFingerprinter()
        person = fp.personManager.findPersonByLeadId(id)
        if (person is None):
            raise Exception("Fingerprint personlead #{} not found.".format(id))
        return person
    

    def lookupFingerprintImagePath(self, id, fingerId, impressionKey):
        # return [relativePath, imageFullPath]
        fp = self.getLoadFingerprinter()
        person = fp.personManager.findPersonByLeadId(id)
        if (person is None):
            raise Exception("Fingerprint personlead #{} not found.".format(id))
        finger = person.findFingerById(fingerId)
        if (finger is None):
            raise Exception("Finger id '{}' not found (should be from [L1,L2,L3,L4,L5,R1,R2,R3,R4,R5]).".format(fingerId))
        impression = finger.findImpressionByKey(impressionKey) 
        if (impression is None):
            raise Exception("Impression key '{}' not found (should be 1 or 2 currently?).".format(impressionKey))
        pathRelative = impression["path"]
        pathAbsolute = fp.makeRelativeImageFileAbsolute(pathRelative)
        fingerCaption = finger.getPlayerCaption()
        return [pathRelative, pathAbsolute, fingerCaption]


    def generateFingerprintSetLatexByLeadId(self, id, caption, flagCompact):
        # return [relativePath, imageFullPath]
        fp = self.getLoadFingerprinter()
        person = fp.personManager.findPersonByLeadId(id)
        if (person is None):
            raise Exception("Fingerprint personlead #{} not found.".format(id))
        latex = fp.buildFingerprintDirectoryPerson(person, caption, False, flagCompact)
        return latex


    def getFingerprintImageDirectoryPath(self):
        # we cannot getLoadFingerprint() yet because we dont know which fingerprinter data we need; but that shouldnt stop us form getting static path to fingerprint image
        #fp = self.getLoadFingerprinter()
        return FingerPrinter.getFingerprintImageDirectoryPath()



    def generateUnusedLeadsUsingPattern(self, dataVersion):
        if (dataVersion=="numbers99"):
            return list(range(10,99))
        elif (dataVersion=="numbers999"):
            return list(range(100,999))
        elif (dataVersion=="numbers9999"):
            return list(range(1000,9999))
        return None

# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
# helper functions for doing text replacement of place mentions
    def flexiblyAddLeadNumbersToText(self, text, outFormat):
        # search text and try to add lead numbers to places
        # some regex patterns that may identify place names

        regexAfterColon = re.compile(r'^([^\:]*)(\:\s*)(.*)()$')
        regexLineBeforeParent = re.compile(r'^([\*\.]?\s*)(.*[^\s])(\s*\(.*)$')
        regexInSquareBrackets = re.compile(r'^(.*)\[(.*)\](.*)$')
        regexInCurlyBrackets = re.compile(r'^(.*)\{(.*)\}(.*)$')

        lines = text.split('\n')
        textOut = ''
        addCount = 0
        for line in lines:
            replaced = False
            matchLead = None
            if (not replaced):
                matches = regexAfterColon.match(line)
                if (matches is not None):
                    text = matches.group(3)
                    [matchLead, text, thisAddCount] = self.flexiblyAddLeadNumberToPotentialTextString(text, outFormat, False)
                    if (thisAddCount):
                        addCount += 1
                        replaced = True
                        line = matches.group(1)+matches.group(2)+text+matches.group(4)
            if (not replaced):
                matches = regexLineBeforeParent.match(line)
                if (matches is not None):
                    text = matches.group(2)
                    [matchLead, text, thisAddCount] = self.flexiblyAddLeadNumberToPotentialTextString(text, outFormat, False)
                    if (thisAddCount):
                        addCount += 1
                        replaced = True
                        line = matches.group(1)+text+matches.group(3)
            if (not replaced):
                matches = regexInSquareBrackets.match(line)
                if (matches is not None):
                    text = matches.group(2)
                    [matchLead, text, thisAddCount] = self.flexiblyAddLeadNumberToPotentialTextString(text, outFormat, True)
                    if (thisAddCount):
                        addCount += 1
                        replaced = True
                        line = matches.group(1)+text+matches.group(3)
            #
            if (replaced):
                # remove trailing space
                if (len(line)>0):
                    if (line[len(line)-1]==' '):
                        line = line[0:len(line)-1]
            #
            textOut += line + '\n'

        return [textOut, addCount]


    def flexiblyAddLeadNumberToPotentialTextString(self, text, outFormat, optionErrorIfNotFound):
        # look for > character; if we find it, remove it but remember location
        text = text.strip()
        breakPos = text.find('>')
        if (breakPos>-1):
            # the > means what follows IS part of search but only use whats after > as label
            labelStr = text[breakPos+1:].strip()
            stext = text.replace('>','')
        else:
            breakPos = text.find('|')
            # the | means what follows is NOT part of search, use whats after as label
            if (breakPos>-1):
                labelStr = text[breakPos+1:].strip()
                stext = text[0:breakPos].strip()
            else:
                stext = text
                labelStr = text

        #
        addCount = 0

        [guessLead, guessSource] = self.findLeadRowByNameOrAddress(stext)
        if (guessLead is None):
            # fallback
            if (stext.lower().startswith('the ')):
                stext = stext[4:]
                [guessLead, guessSource] = self.findLeadRowByNameOrAddress(stext)
            if (guessLead is None):
                stext = stext + ', The'
                [guessLead, guessSource] = self.findLeadRowByNameOrAddress(stext)
        if (guessLead is not None):
            guessLeadProperties = guessLead["properties"]
            guessLeadId = guessLeadProperties['lead']
            #jrprint('Matched string of "{}" to lead {}'.format(stext, guessLeadId))
            addCount += 1
            if (outFormat in ['markdownCb']):
                if (labelStr!=''):
                    text = '**{}**: **{}** '.format(labelStr, guessLeadId)
                else:
                    text = '**{}** '.format(guessLeadId)
            elif (outFormat in ['markdown']):
                if (labelStr!=''):
                    text = '**{}**: **{}** '.format(guessLeadId, labelStr)
                else:
                    text = '**{}** '.format(guessLeadId)
            elif (outFormat in ['html']):
                if (labelStr!=''):
                    text = '**{}:&nbsp;&nbsp;{}** '.format(guessLeadId, labelStr)
                else:
                    text = '**{}** '.format(guessLeadId)
            elif (outFormat=='latex'):
                if (labelStr!=''):
                    text = r'\textbf{' + '{}:~~{}** '.format(guessLeadId, labelStr) + '}'
                else:
                    text = r'\textbf{' + '{} '.format(guessLeadId) + '}'
            elif (outFormat=='leadid'):
                text = guessLeadId
            else:
                raise Exception("In flexiblyAddLeadNumberToPotentialTextString, outFormat '{}' not understood.".format(outFormat))
                if (labelStr!=''):
                    text = '{}:  {} '.format(guessLeadId, labelStr)
                else:
                    text = '{} '.format(guessLeadId)
        else:
            if (optionErrorIfNotFound):
                raise Exception("Failed to find a matching lead entry for text reference '{}' (stext='{}' label='{}').".format(text, stext, labelStr))
        return [guessLead, text, addCount]

# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def checkLoadUnusedLeads(self):
        if (not self.isEnabled()):
            return False
        if (self.unusedLeads is None):
            self.loadUnusedLeadsFromFile()
        if (len(self.unusedLeads) == 0):
            return False
        return True

    def popAvailableLead(self):
        if (not self.checkLoadUnusedLeads()):
            return None
        if (True):
            raise Exception("ERROR: Use of popAvailableLead() is now deprecated in favor of chooseUnusedLeadUsingStableHashKey()")
        else:
            # pick random row, remove it, return it
            key = random.choice(list(self.unusedLeads))
            row = self.unusedLeads[key]
            del self.unusedLeads[key]
            return row
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def addUsedLead(self, source, leadRow, renderLeadp, flagNotAlreadyBeInUsedList):
        leadId = leadRow["properties"]["lead"]

        # flag if its already been used and add it to simple use list, and remove from reserved
        self.addUsedLeadSimpleId(leadId, flagNotAlreadyBeInUsedList)

        # add it to used list, which we will use for exporting?
        leadUseDict = {"source": source, "row": leadRow, "renderLeadp": renderLeadp}
        self.usedLeads.append(leadUseDict)



    def addUsedLeadSimpleId(self, leadId, flagNotAlreadyBeInUsedList):
        # for when a lead id is used but we do not have full info about it (may not even be in db)
        # we provide this so we can auto reserve otherwise unused leads and detect duplicate lead use issues
        if (flagNotAlreadyBeInUsedList):
            if (leadId in self.usedLeadIds):
                raise Exception("Trying to addUsedLeadSimpleId but it's already been addded.")
        if (leadId not in self.usedLeadIds):
            self.usedLeadIds.append(leadId)

        # ATTN: TODO - should we remove it from unused in case they are adding a used lead that we would otherwise use
        if (True):
            self.reserveLead(leadId)
# ---------------------------------------------------------------------------






















# ---------------------------------------------------------------------------
    def getNumericLeadRange(self):
        return [1000, 99999]
    
    def calcLeadIdFromNumber(self, leadIdAsNumber):
        # convert a number in range 1000-99999 to standard lead #-#### format
        lstring = str(leadIdAsNumber)
        leadId = "{}-{}".format(lstring[0], lstring[1:])
        return leadId

    # we want a way of choosing stable unused lead that's don't change after modifications to game source
    def chooseUnusedLeadUsingStableHashKey(self, hashKeyString):
        if (not self.checkLoadUnusedLeads()):
            return None

        # here's a nice feature, let's try to alert when we dont get a unique hashkey
        if (hashKeyString in self.previousUnusedHashKeys):
            jrprint("ATTN: Warning, hit collision duplicate hask key used for chooseUnusedLeadUsingStableHashKey({}).".format(hashKeyString))
        else:
            self.previousUnusedHashKeys.append(hashKeyString)

        if (len(self.unusedLeads)==0):
            raise Exception("ERROR: No unused leads to choose from in chooseUnusedLeadUsingStableHashKey().")

        # ok first we need a numeric RANGE
        [rmin, rmax] = self.getNumericLeadRange()

        # now we loop until we get a hit
        tryCount = 0
        warnThreshold = 20
        exitThreshold = 5000
        while (True):
            tryCount += 1
            hashKeyStringTry = hashKeyString + "_try"+str(tryCount)
            # generate a unique number if range
            leadIdAsNumber = self.stableHashToNumberRange(rmin, rmax, hashKeyStringTry)
            leadId = self.calcLeadIdFromNumber(leadIdAsNumber)
            if (leadId in self.unusedLeads):
                # found one!
                row = self.unusedLeads[leadId]
                del self.unusedLeads[leadId]
                return row
            if (tryCount>warnThreshold):
                jrprint("ATTN: WARNING: Failed to find stable hash key after {} tries; last try: {}.".format(tryCount, leadId))
                warnThreshold = warnThreshold * 2
            if (tryCount>exitThreshold):
                raise Exception("ERROR: Giving up after {} attempts to find a chooseUnusedLeadUsingStableHashKey for {}; there are {} remaining unused leads.".format(tryCount, hashKeyString, len(self.unusedLeads)))


    def stableHashToNumberRange(self, rmin, rmax, keyStringTry):
        roundsToRun = 4
        seedKey = str(self.getSeed())
        num = stringToFeistelRange(keyStringTry, rmin, rmax, seedKey, roundsToRun)
        return num
# ---------------------------------------------------------------------------






































# ---------------------------------------------------------------------------
class HlApiTable(HlApi):
    def __init__(self, baseDataDir, options, numbersPerColumn, columns, tables, templateSuffix, flagMultiTablesOnOnePage, pageTitle):
        super().__init__(baseDataDir, options)
        #
        self.numbersPerColumn = numbersPerColumn
        self.numberRows = list(range(1,self.numbersPerColumn+1))
        self.columns = columns
        self.columnKeys = columns.keys()
        self.tables = tables
        self.templateSuffix = templateSuffix
        self.flagMultiTablesOnOnePage = flagMultiTablesOnOnePage
        #
        self.numberMap = {}
        self.unusedNumbers = []
        self.loaded = False
        #
        self.blankLead = "999"
        #
        self.tableToc = "Paragraph Lookup Table"
        self.tableTitle = "PARAGRAPH~ LOOKUP~ TABLE"
        self.pageTitle = pageTitle


    def makeOrLoadDataTable(self, flagForceLatexTableCreate):
        if (self.loaded):
            return True
        retv = self.loadTableAndUnusedNumberData()
        if (not retv):
            # can't be loaded, so make it
            self.makeSaveDataTable()
        else:
            # we just loaded it
            if (flagForceLatexTableCreate):
                # force a write of latex table document
                self.writeLatexDataTableDoc()


    def loadTableAndUnusedNumberData(self):
        # this is not for ny noir but for using tables of lead paragraph numbers
        # return True on success, or False if we need to create it ourselves
        # load table data
        baseDataDir = self.calcDataDir()
        filePath = baseDataDir + "/tableData.json"
        if (not jrfuncs.pathExists(filePath)):
            # not found
            return False
        jsonData = jrfuncs.loadJsonFromFile(filePath, True, "utf-8")
        self.numberMap = jsonData
        # load unused numbers (this is similar to ow we normally load it, but this is alternate copy of hlapi not the version we use to assign unsed leads, so we dont even really use this currently)
        filePath = baseDataDir + "/unusedLeads.csv"
        if (not jrfuncs.pathExists(filePath)):
            # not found
            return False
        self.unusedNumbers = []
        with open(filePath) as csvFile:
            csvReader = csv.DictReader(csvFile)
            for row in csvReader:
                val = row["lead"]
                self.unusedNumbers.append(int(val))

        # success
        self.loaded = True
        return True

    
    def lookupTableEntry(self, neighborhoodColumn, numRow, tableId):
        return self.numberMap[tableId][neighborhoodColumn][numRow]

    def makeSaveDataTable(self):
        # available paragraph numbers to use
        startNumber = 100
        endNumber = 999
        availableNumbers = list(range(startNumber, endNumber + 1))
        # shuffle them randomly
        random.shuffle(availableNumbers)
        # ok now walk table and build it using numbers
        self.numberMap = {}
        if (self.tables is None):
            tableList = {"": None}
        else:
            tableList = self.tables
        for tid,tv in tableList.items():
            if (tid not in self.numberMap):
                self.numberMap[tid] = {}
            for k,v in self.columns.items():
                for num in self.numberRows:
                    numStr = str(num)
                    if (k not in self.numberMap[tid]):
                        self.numberMap[tid][k] = {}
                    if (num<=v):
                        cval = str(availableNumbers.pop())
                    else:
                        cval = self.blankLead
                    self.numberMap[tid][k][numStr] = cval
        # ok now we have our table, AND our list of UNUSED numbers
        self.unusedNumbers = availableNumbers
        # set flag saying loaded
        self.loaded = True
        # write out the table data
        self.writeDataTable()
        # write out the unused numbers
        self.writeUnusedLeads()
        # write the latex table
        self.writeLatexDataTableDoc()

    

    def writeDataTable(self):
        baseDataDir = self.calcDataDir()
        filePath = baseDataDir + "/tableData.json"
        jsonText = json.dumps(self.numberMap)
        retv = jrfuncs.saveTxtToFile(filePath, jsonText, "utf-8")
        return retv

    def writeUnusedLeads(self):
        baseDataDir = self.calcDataDir()
        filePath = baseDataDir + "/unusedLeads.csv"
        with open(filePath, "w", encoding="utf-8") as file:
            file.write("{},{}\n".format("","lead"))
            for index, value in enumerate(self.unusedNumbers):
                file.write("{},{}\n".format(index,value))
    

    def writeLatexDataTableDoc(self):
        self.makeOrLoadDataTable(False)
        # load preamble
        baseDataDir = self.calcDataDir()
        templateDir = self.calcDataParentDir() + "/templates"
        templateSuffix = self.templateSuffix
        preambleLatex = jrfuncs.loadTxtFromFile(templateDir + "/mapTablePreamble.latex", True, "utf-8")
        preambleLatex += jrfuncs.loadTxtFromFile(templateDir + "/mapTablePreamble" + templateSuffix + ".latex", True, "utf-8")
        postambleLatex = jrfuncs.loadTxtFromFile(templateDir + "/mapTablePostamble.latex", True, "utf-8")
        latex = preambleLatex + "\n\n\n"

        rowsPerColumn = 50
        columnsPerPage = 2
        flagMultiTablesOnOnePage = self.flagMultiTablesOnOnePage


        # now add latex code
        # start
        latex += "\n\n"

        if (self.tables is None):
            tableList = {"": None}
        else:
            tableList = self.tables

        if (flagMultiTablesOnOnePage):
                pageTitle = self.pageTitle.strip()
                toc=pageTitle.trip()
                latex += "\\cbTableSheading{" + toc + "}{" + pageTitle + "}{}%\n"     

        # early table labels and multicols if we are going to try to put 2 tables on one page (50 row tables)
        if (flagMultiTablesOnOnePage):
            latex += "\\begin{multicols*}{" + str(columnsPerPage) + "}\n"



        # support for multiple tables
        tableIndex = 0
        for tid,tv in tableList.items():

            # table title, etc.
            if (tableIndex>0):
                if (flagMultiTablesOnOnePage):
                    latex += "\\columnbreak"
                else:
                    latex += "\\newpage"
            tableIndex += 1
            #
            if (tv is not None):
                toc = tv["toc"]
                tableTitle = tv["title"]
                if (len(tableList)>1):
                    tableTitleParen = "[" + tid + "]"
                else:
                    tableTitleParen = ""
            else:
                toc = self.tableToc
                tableTitle = self.tableTitle
                tableTitleParen = ""
            #

            # begin interior table
            if (not flagMultiTablesOnOnePage):
                # each table can start its own new multicols
                latex += "\\cbTableSheading{" + toc + "}{" + tableTitle + "}{" + tableTitleParen + "}%\n"
                latex += "\\begin{multicols*}{" + str(columnsPerPage) + "}\n"

            # ok tabular environment and alignment of columns
            tabularBeginLatex = "\\begin{center}" + "\n"
            #tabularBeginLatex = "\\centering" + "\n"
            if (flagMultiTablesOnOnePage):
                # table title at top of column
                tabularBeginLatex += "\\cbTableSheadingInline{" + toc + "}{" + tableTitle + "}{" + tableTitleParen + "}%\n"
                tabularBeginLatex += "\\par\\nopagebreak[4]\n"

            tabularBeginLatex += "\\begin{tabular}{r|"
            for col in self.columns:
                tabularBeginLatex += "c"
            tabularBeginLatex += "}\n"

            # table header
            for k,v in self.columns.items():
                tabularBeginLatex += "& \\textFontHead{" + k + "} "
            tabularBeginLatex += "\\\\ \n"
            tabularBeginLatex += "\\hline\n"
            tabularEndLatex = "\\end{tabular}\n"
            tabularEndLatex += "\\end{center}\n"

            # rows
            rowCountInColumn = 0
            needsCloseTabular = False
            for num in self.numberRows:
                if (not needsCloseTabular):
                    # start of table
                    latex += tabularBeginLatex
                    needsCloseTabular = True
                #
                rowCountInColumn += 1
                #
                rowId = str(num)
                # row prefix
                latex += "\\textFontHead{" + rowId + "} "
                # column values for this row
                for k,v in self.columns.items():
                    val = self.numberMap[tid][k][rowId]
                    valStr = str(val)
                    latex += "& \\textFontInner{" + valStr + "} "
                latex += "\\\\ \n"
                # end of column
                if (rowCountInColumn==rowsPerColumn):
                    # end tabular
                    latex += tabularEndLatex
                    latex += "\\columnbreak\n"
                    needsCloseTabular = False
                    rowCountInColumn = 0
            
            # done
            if (needsCloseTabular):
                # end tabular
                latex += tabularEndLatex
                latex += "\\columnbreak\n"
                needsCloseTabular = False

            # end interior
            if (not flagMultiTablesOnOnePage):
                latex += "\\end{multicols*}\n"

            latex += "\n\n\n"

        # end exterior cols
        if (flagMultiTablesOnOnePage):
            latex += "\\end{multicols*}\n"

        # end
        latex += postambleLatex + "\n"


        # now write it
        fileDir = baseDataDir + "/output"
        jrfuncs.createDirIfMissing(fileDir)
        filePath = fileDir + "/ParagraphLookupTable" + self.options["outSuffix"] + ".latex"
        jrfuncs.saveTxtToFile(filePath, latex, "utf-8")
# ---------------------------------------------------------------------------










