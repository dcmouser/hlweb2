# imports
from lib.jr import jrfuncs
from lib.jr import jroptions
from lib.jr.jrfuncs import jrprint
from lib.jr.jrfuncs import jrException

# python imports
import csv
import os
import pathlib
import json
from difflib import SequenceMatcher
from pathlib import Path



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
        self.disabled = False
        self.flagDebug = False

    def getThisSourceDirectory(self):
        source_path = Path(__file__).resolve()
        source_dir = source_path.parent
        return str(source_dir)

    def isEnabled(self):
        return (self.disabled) or ('enabled' not in self.options) or (self.options['enabled'])

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
        return dataDir

    def getVersion(self):
        return self.options["dataVersion"]

    def addUsedLead(self, source, leadRow, renderLeadp):
        leadUseDict = {"source": source, "row": leadRow, "renderLeadp": renderLeadp}
        self.usedLeads.append(leadUseDict)
    def getUsedLeads(self):
        return self.usedLeads




# ---------------------------------------------------------------------------
    def loadUnusedLeadsFromFile(self):
        self.unusedLeads = []
        dataDir = self.calcDataDir()
        if (dataDir is None):
            return False
        filePath = dataDir + '/unusedLeads.csv'
        with open(filePath) as csvFile:
            csvReader = csv.DictReader(csvFile)
            for row in csvReader:
                self.unusedLeads.append(row)
        if (self.flagDebug):
            jrprint('{} unused leads read from "{}"'.format(len(self.unusedLeads), filePath))
        return True


    def popAvailableLead(self):
        if (not self.isEnabled()):
            return None
        if (self.unusedLeads is None):
            self.loadUnusedLeadsFromFile()
        if (len(self.unusedLeads) == 0):
            return None
        return self.unusedLeads.pop()
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def loadLeads(self):      
        self.leads = {}
        if (not self.isEnabled()):
            return False

        dataDir = self.calcDataDir()
        if (dataDir is None):
            return False
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
                if (row['properties']['address']==txt) or (row['properties']['dName']==txt):
                    return [row, sourceKey]
                dName = row['properties']['dName']
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
        address = self.getNiceAddress(leadRow, "abbreviation", False)
        label = "{} ({})".format(dName, address)
        return label


    def getNiceAddress(self, leadRow, neighborhoodOption, flagHidePrivate):
        leadRowProperties = leadRow["properties"]
        listype  = leadRowProperties["listype"]
        if (flagHidePrivate) and (listype=="private"):
            return ""
        #
        address = leadRowProperties["address"]
        jregion = leadRowProperties["jregion"]
        if (neighborhoodOption == None):
            return address
        elif (neighborhoodOption=="abbreviation"):
            return address + ", " + jregion
        else:
            return address + ", " + self.jregionToNeighborhoodLabel(jregion)


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

        if (len(self.usedLeads) == 0):
            return False

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
















