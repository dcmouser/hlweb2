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



# ---------------------------------------------------------------------------
class HlApi:
    def __init__(self, dataDir, options={}):
        self.dataDir = dataDir
        self.options = options
        #
        self.unusedLeads = None
        self.leads = None

    def setDataDir(self, dataDir):
        self.dataDir = dataDir

    def isEnabled(self):
        return ('enabled' not in self.options) or (self.options['enabled'])

    def enableSlowSearch(self):
        return ('disableSlowSearch' not in self.options) or (not self.options['disableSlowSearch'])



# ---------------------------------------------------------------------------
    def loadUnusedLeadsFromFile(self):
        self.unusedLeads = []
        filePath = self.dataDir + '/unusedLeads.csv'
        with open(filePath) as csvFile:
            csvReader = csv.DictReader(csvFile)
            for row in csvReader:
                self.unusedLeads.append(row)
        jrprint('{} unused leads read from "{}"'.format(len(self.unusedLeads), filePath))
        #print(self.unusedLeads)


    def popAvailableLead(self):
        if (not self.isEnabled()):
            return None
        if (self.unusedLeads is None):
            self.loadUnusedLeadsFromFile()
        return self.unusedLeads.pop()
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def loadLeads(self):
        if (not self.isEnabled()):
            return False
        
        self.leads = {}
        directoryPath = self.dataDir + '/leads/'

        for (dirPath, dirNames, fileNames) in os.walk(directoryPath):
            for fileName in fileNames:
                fileNameLower = fileName.lower()
                if (fileNameLower.endswith('.json')):
                    baseName = pathlib.Path(fileName).stem
                    fileFinishedPath = dirPath + '/' + fileName
                    self.loadLeadFile(fileFinishedPath, baseName)

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

            jrprint('Loaded {} leads from "{}" ({})'.format(len(features), fileSourceLabel, filePath))
            self.leads[fileSourceLabel] = rows


    def findLeadRowByLeadId(self, leadId):
        if (not self.isEnabled()):
            return [None, None]
        
        if (self.leads is None):
            self.loadLeads()
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

        if (self.leads is None):
            self.loadLeads()
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

        if (self.leads is None):
            self.loadLeads()
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
