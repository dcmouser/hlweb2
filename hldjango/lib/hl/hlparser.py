# helper class for hl parser tool

from lib.jr import jrfuncs
from lib.jr import jroptions
from lib.jr.jrfuncs import jrprint, jrlog
from lib.jr.jrfuncs import jrException

from lib.jr.hlmarkdown import HlMarkdown
from . import hlapi
from lib.jr import jrmindmap
from lib.jr.jrfilefinder import JrFileFinder

# for compiling latex
import pylatex
from pylatex.utils import dumps_list, rm_temp_dir, NoEscape
import pdflatex
from pdflatex import PDFLaTeX

# python modules
import re
import os
import pathlib
from collections import OrderedDict
import json
import random
import argparse
import subprocess
from subprocess import PIPE
import sys
import errno
import math
import traceback
import datetime




# ---------------------------------------------------------------------------
buildVersion = '3.1jr'
# ---------------------------------------------------------------------------







# ---------------------------------------------------------------------------
# NOT A CLASS FUNCTION
def fastExtractSettingsDictionary(text):
    # we might normally extract settings during parsing, but we want to have a quick way to do it.
    # ATTN: TODO: Note that this code uses a regex to extract the settings, compared to how the settings might be extracted during full processing, which may be able to ignore comment lines, etc
    # so it is possible that this version may error out in ways that the full function won't

    #
    settings = {}
    # extract json settings
    # evilness
    text = jrfuncs.fixupUtfQuotesEtc(text)
    #
    #regexSettings = re.compile(r'#\s*options\s*\n\{([\S\s]*?\})(\n+#)', re.MULTILINE | re.IGNORECASE)
    #regexSettings = re.compile(r'(.*)#\s*options\s*\n(\{[\S\s]*?\})(\n+#).*', re.MULTILINE | re.IGNORECASE)
    regexSettings = re.compile(r'#\s*options\s*\n(\{[\S\s]*?\})(\n+#)', re.MULTILINE | re.IGNORECASE)
    matches = regexSettings.search(text)
    #matches = regexSettings.match(text)
    if (matches):
        # kludge to make error line number inside json match up with text line number
        start = matches.start()
        end = matches.end()
        priorText = text[0:start]
        priorTextNewlineCount=priorText.count("\n")
        if (priorTextNewlineCount>0):
            prorTextKludge= "\n" * (priorTextNewlineCount+1)
        else:
            prorTextKludge=""
        #
        settingsString = prorTextKludge + matches[1]
        settings = json.loads(settingsString)
    else:
        raise Exception("No options block found in text.")
    #

    return settings
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
class HlParser:

    def __init__(self, optionsDirPath, overrideOptions={}):
        # load options
        self.jroptions = None
        self.jroptionsWorkingDir = None
        self.storyFileList = []
        self.headBlocks = []
        self.leads = []
        self.leadStats = {}

        self.warnings = []
        self.dynamicLeadMap = {}
        self.leadSections = {}
        #
        # tags
        self.tagMap = {}
        #
        self.tagConditionLabelsAvailable = []
        self.tagConditionLabelStage = 0
        self.tagDocumentIndex = 0
        #
        self.notes = []
        #
        self.userVars = {}
        self.tText = {'goto': 'go to', 'returnto': 'return to', 'restbreak': '*If you\'ve been playing for a couple of hours, now might be a good time to take a break before continuing...*',
                      'condition':'marker', 'timeAdvances': '%Symbol.Clock%  Time advances', 'Symbol.Clock': '%Symbol.Clock%', 'Symbol.Mark': '%Symbol.Mark%', 'Symbol.Doc': '%Symbol.Doc%',
                      'Symbol.Checkbox': '%Symbol.Checkbox%', 'Template.BoxStart': '%boxstart%', 'Template.BoxStartRed': '%boxstartred%', 'Template.BoxEnd': '%boxend%'}
        #
        self.markBoxesTracker = {}
        #
        self.argDefs = {
            'header': {
                'named': ['id', 'label', 'existing', 'ignore', 'section', 'type', 'warning', 'autoid', 'render', 'sort', 'stop', 'map', 'info', 'location', 'labelcontd', 'deadline', 'time'],
                'positional': [],
                'required': []
            },
            'tag': {'named': ['id'], 'required': ['id']},
            'golead': {'named': ['leadId', 'link', 'comeback'], 'required': ['leadId']},
            'goleadback': {'named': ['leadId', 'link', 'comeback'], 'required': ['leadId']},
            'reflead': {'named': ['leadId', 'link', 'comeback'], 'required': ['leadId']},
            'returnlead': {'named': ['leadId', 'link'], 'required': ['leadId']},
            'leadid': {'named': ['leadId', 'link'], 'required': ['leadId']},
            'options': {'named': ['json'],  'required': ['json']},
            'returninline': {'named': ['link']},

            'gofake': {'named': ['link']},
            'gofakeback': {'named': ['link']},
            #
            'inline': {'named': ['label', 'link', 'after', 'demerits', 'demerithours', 'back', 'resume', 'time', 'unless']},
            'inlineback': {'named': ['label', 'link', 'after', 'demerits', 'demerithours', 'back', 'resume', 'time', 'unless']},
            'inlinehint': {'named': ['demerits', 'label', 'link', 'after', 'demerithours', 'back', 'resume', 'time', 'unless']},
            #'inlinehint': {'named': ['amount', 'back']},
            #'inlineback': {'named': ['label', 'link', 'after']},
            #'inlinebacks': {'named': ['label', 'link', 'after']},
            #'inlinedemerit': {'named': ['amount', 'back']},
            #'inlinedemerithours': {'named': ['amount', 'back']},

            # tags
            'definetag': {'named': ['id', 'comment'], 'required': ['id']},
            'gaintag': {'named': ['id', 'define'], 'required': ['id']},
            'hastag': {'named': ['id'], 'required': ['id']},
            'hasanytag': {'named': ['id'], 'required': ['id']},
            'hasalltags': {'named': ['id'], 'required': ['id']},
            'missingtag': {'named': ['id'], 'required': ['id']},
            'missinganytags': {'named': ['id'], 'required': ['id']},
            'missingalltags': {'named': ['id'], 'required': ['id']},
            'requiretag': {'named': ['id', 'type', 'amount', 'time'], 'required': ['id']},
            'mentiontags': {'named': ['id'], 'required': ['id']},


            'beforeday': {'named': ['day'], 'required': ['day']},
            'afterday': {'named': ['day'],  'required': ['day']},
            'onday': {'named': ['day'], 'required': ['day']},
            'endjump': {},
            'insertlead': {'named': ['leadId'], 'required': ['leadId']},
            'get': {'named': ['varName'],  'required': ['varName']},
            'set': {'named': ['varName', 'value'], 'required': ['varName', 'value']},
            'empty': {},
            'mark': {'named': ['type', 'amount'], 'required': ['type']},
            'demerits': {'named': ['amount']},
            'backdemerit': {'named': ['demerits', 'goto', 'lead']},
            'resumebriefing': {'named': ['demerits', 'goto']},

            'form': {'named': ['type','choices'], 'required': ['type']},
            'report': {'named': ['comment']},
            'otherwise': {},
            'logicmentions': {'named': ['target', 'link']},
            'logicimplies': {'named': ['target', 'link']},
            'logicimpliedby': {'named': ['target', 'link']},
            'logicsuggests': {'named': ['target', 'link']},
            'logicsuggestedby': {'named': ['target', 'link']},
            'logicidea': {'named': ['name', 'link', 'type'], 'required': ['name']},
            'logicab': {'named': ['a', 'b', 'link'], 'required': ['a', 'link']},
            'logicaba': {'named': ['a', 'b', 'link'], 'required': ['a', 'link']},
            'logicirrelevant': {},
            'onlyonce': {},
            'warning': {'named': ['msg']},
            'remind': {'named': ['type'], 'required': ['type']},

            'autohint': {},
            'deadlineinfo': {'named': ['day', 'stage', 'limit', 'last', 'start', 'end']},

            'time': {'named': ['amount']},
            'otime': {'named': ['amount']},

            'ifcond': {'named': ['condition']},
            'include': {'named': ['file']},

            'begin': {},
            'end': {},
        }
        #
        self.doLoadAllOptions(optionsDirPath, overrideOptions)
        #
        self.calculatedRenderOptions = None
        #
        renderOptions = self.getComputedRenderOptions()
        markdownOptions = renderOptions['markdown']
        self.hlMarkdown = HlMarkdown(markdownOptions, self)
        #
        # hl api
        self.hlapi = None
        self.hlapiPrev = None
        #
        # mindmap
        mindMapOptions = self.getOptionVal('mindMapOptions', {})
        self.mindMap = jrmindmap.JrMindMap(mindMapOptions)
        #
        self.clearBuildLog()
        #
        self.didRunDebugExtraSteps = False
        self.didRender = False
        self.storegGameText = ''
        #
        self.generatedFiles = []
        self.getGeneratedFilesForZip = []
        #
        # game file manager
        self.gameFileManager = self.getOptionValThrowException('gameFileManager')
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
    def getVersion(self):
        return buildVersion
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
    def storedGameTextClear(self):
        self.storedGameText = ''
    def storedGameTextAdd(self, text):
        if (self.storegGameText!=''):
            self.storegGameText += '\n'
        self.storegGameText += text
    def getStoredGameText(self):
        return self.storegGameText

    def addGeneratedFile(self, filePath, flagAddZipList = True):
        self.generatedFiles.append(filePath)
        if (flagAddZipList):
            self.getGeneratedFilesForZip.append(filePath)

    def getGeneratedFileList(self):
        return self.generatedFiles
    def getGeneratedFileListForZip(self):
        return self.getGeneratedFilesForZip

    def clearGeneratedFileListForZip(self):
        self.getGeneratedFilesForZip = []
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
    def getHlApi(self):
        if (self.hlapi is None):
            dversion = self.getOptionVal('hlDataDirVersion', None)
            hlDataDirVersioned = self.getOptionValThrowException('hlDataDir') + '/' + dversion
            hlDataDirVersioned = self.resolveTemplateVars(hlDataDirVersioned)
            hlApiOptions = self.getOptionVal('hlApiOptions', {})
            self.hlapi = hlapi.HlApi(hlDataDirVersioned, hlApiOptions)
        return self.hlapi


    def getHlApiPrev(self):
        if (self.hlapiPrev is None):
            dversion = self.getOptionVal('hlDataDirVersion', None)
            dversionPrev = self.getOptionVal('hlDataDirVersionPrev', None)
            if (dversionPrev is None) or (dversion == dversionPrev):
                return None
            hlDataDirVersionedPrev = self.getOptionValThrowException('hlDataDir') + '/' + dversionPrev
            hlDataDirVersionedPrev = self.resolveTemplateVars(hlDataDirVersionedPrev)
            hlApiOptions = self.getOptionVal('hlApiOptions', {})
            self.hlapiPrev = hlapi.HlApi(hlDataDirVersionedPrev, hlApiOptions)
        return self.hlapiPrev


    def getHlApiList(self):
        api1 = self.getHlApi()
        api2 = self.getHlApiPrev()
        if (api2 is not None):
            return [api1, api2]
        return [api1]

    def updateHlApiDirs(self):
        # called after processing working dir options; ugly reuse of code above
        api1 = self.getHlApi()
        dversion = self.getOptionVal('hlDataDirVersion', None)
        hlDataDirVersioned = self.getOptionValThrowException('hlDataDir') + '/' + dversion
        hlDataDirVersioned = self.resolveTemplateVars(hlDataDirVersioned)
        api1.setDataDir(hlDataDirVersioned)
        api2 = self.getHlApiPrev()
        if (api2 is not None):
            dversionPrev = self.getOptionVal('hlDataDirVersionPrev', None)
            hlDataDirVersionedPrev = self.getOptionValThrowException('hlDataDir') + '/' + dversionPrev
            hlDataDirVersionedPrev = self.resolveTemplateVars(hlDataDirVersionedPrev)
            api2.setDataDir(hlDataDirVersionedPrev)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def clearBuildLog(self):
        self.buildLog = ''
        self.buildErrorStatus = False
        self.buildErrorCount = 0

    def getBuildLog(self):
        return self.buildLog

    def getBuildErrorStatus(self):
        return self.buildErrorStatus
    def getBuildErrorCount(self):
        return self.buildErrorCount

    def addBuildErrorStatus(self):
        self.buildErrorStatus = True
        self.buildErrorCount += 1

    def addBuildLog(self, msg, isError):
        if (isError):
            self.addBuildErrorStatus()
        if (self.buildLog != ''):
            self.buildLog += '\n-----\n'
        self.buildLog += msg
# ---------------------------------------------------------------------------









        

# ---------------------------------------------------------------------------
    def processCommandline(self, appName, appInfo):
        parser = argparse.ArgumentParser(prog = appName, description = appInfo)
        parser.add_argument('-c', '--command', required=False)
        parser.add_argument('-w', '--workingdir', required=False)
        args = parser.parse_args()
        #
        workingdir = args.workingdir
        if (workingdir):
            self.mergeOverrideOptions({'workingdir': workingdir})
        #
        if (args.command == 'reftest'):
            self.testMakeReferenceGuide()
        else:
            self.runAll()
# ---------------------------------------------------------------------------







# ---------------------------------------------------------------------------
    def getSaveDir(self):
        saveDir = self.getOptionValThrowException('savedir')
        saveDir = self.resolveTemplateVars(saveDir)
        jrfuncs.createDirIfMissing(saveDir)
        return saveDir

    def calcOutFileDerivedName(self, baseFileName):
        saveDir = self.getSaveDir()
        info = self.getOptionValThrowException('info')
        chapterName = self.getChapterName()
        outFilePath = saveDir + '/' + chapterName + baseFileName
        return outFilePath
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
    def getChapterName(self):
        return self.chapterName

    def setChapterName(self, chapterName):
        self.chapterName = chapterName
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def doLoadAllOptions(self, optionsDirPath, overrideOptions):
        self.loadOptions(optionsDirPath)
        # apply overrides (which may include a workingdir override)
        self.mergeOverrideOptions(overrideOptions)
        # load workingdir options
        workingDirPath = self.getBaseOptionValThrowException('workingdir')
        self.loadWorkingDirOptions(workingDirPath)


    def loadOptions(self, optionsDirPath):
        # create jroptions helper
        self.jroptions = jroptions.JrOptions(optionsDirPath)
        jrprint('Loading options from {}..'.format(optionsDirPath))
        # load basics
        self.jroptions.loadOptionsFile('options', True, True)
        self.jroptions.loadOptionsFile('private', True, False)

    def saveOptions(self):
        jrprint('Saving options back to original option data files..')
        self.jroptions.saveOptionsFiles(True)

    def mergeOverrideOptions(self, overrideOptions):
        if (len(overrideOptions)>0):
            jrprint('Merging options: {}.'.format(overrideOptions))
            self.jroptions.mergeRawDataForKey('options', overrideOptions)


    def loadWorkingDirOptions(self, optionsDirPath):
        # create jroptions helper
        self.jroptionsWorkingDir = jroptions.JrOptions(optionsDirPath)
        if (optionsDirPath==None):
            return
        jrprint('Loading workingdir options from {}..'.format(optionsDirPath))
        # load basics
        self.jroptionsWorkingDir.loadOptionsFile('options', True, False)
        self.jroptionsWorkingDir.loadOptionsFile('private', True, False)

    def getOptionValThrowException(self, keyName):
        # try to get from working dir options, fall back to base options
        val = self.getWorkingOptionVal(keyName, None)
        if (val==None):
            val = self.getBaseOptionVal(keyName, None)
        if (val==None):
            raise Exception('Key "{}" not found in options.'.format(keyName))
        return val
    
    def getOptionVal(self, keyName, defaultVal):
        # try to get from working dir options, fall back to base options
        val = self.getWorkingOptionVal(keyName, None)
        if (val==None):
            val = self.getBaseOptionVal(keyName, None)
        if (val==None):
            val = defaultVal
        return val

    def setOption(self, keyName, val):
        self.jroptionsWorkingDir.setKeyVal('options',keyName, val)


    #
    def getBaseOptionValThrowException(self, keyName):
        return self.jroptions.getKeyValThrowException('options', keyName)
    def getWorkingOptionValThrowException(self, keyName):
        return self.getKeyValThrowException.getKeyVal('options', keyName)
    def getBaseOptionVal(self, keyName, defaultVal):
        return self.jroptions.getKeyVal('options', keyName, defaultVal)
    def getWorkingOptionVal(self, keyName, defaultVal):
        return self.jroptionsWorkingDir.getKeyVal('options', keyName, defaultVal)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
    def loadStoryFilesIntoBlocks(self):
        jrprint('Scanning for and loading lead files..')
        self.storedGameTextClear()
        storyDirectoriesList = self.getOptionValThrowException("storyDirectories")
        for storyDir in storyDirectoriesList:
            self.findStoryFilesFromDir(storyDir)
        # ok now with each lead file we found, process it
        for storyFilePath in self.storyFileList:
            self.loadStoryFileIntoBlocks(storyFilePath)


    def findStoryFilesFromDir(self, directoryPathOrig):
        directoryPath = self.resolveTemplateVars(directoryPathOrig)
        #
        if (directoryPath != directoryPathOrig):
            jrprint("Scanning for story files in {} ({}):".format(directoryPath, directoryPathOrig))
        else:
            jrprint("Scanning for story files in {}:".format(directoryPath))

        if (not jrfuncs.pathExists(directoryPath)):
            raise Exception('Error directory does not exist: {}'.format(directoryPath))

        # recursive scan
        for (dirPath, dirNames, fileNames) in os.walk(directoryPath):
            for fileName in fileNames:
                fileNameLower = fileName.lower()
                baseName = pathlib.Path(fileName).stem
                dirPathLink = dirPath
                fileFinishedPath = dirPathLink + '/' + fileName
                if (fileNameLower.endswith('.txt')):
                    jrprint('Adding file "{}" to lead queue.'.format(fileFinishedPath, baseName))
                    self.storyFileList.append(fileFinishedPath)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
    def makeChapterSaveDirFileName(self, subdir, suffix):
        info = self.getOptionValThrowException('info')
        chapterName = self.getChapterName()
        baseOutputFileName = chapterName + suffix
        saveDir = self.getSaveDir()
        if (subdir!=''):
            saveDir = saveDir + '/' + subdir
        jrfuncs.createDirIfMissing(saveDir)
        outFilePath = saveDir + '/' + baseOutputFileName
        return outFilePath

    def saveTextLeads(self):
        fileText = self.getStoredGameText()
        #outFilePath = self.makeChapterSaveDirFileName('dataout','_leads.txt')
        outFilePath = self.makeChapterSaveDirFileName('','_leads.txt')
        encoding = 'utf-8'
        jrfuncs.saveTxtToFile(outFilePath, fileText, encoding)
        self.addGeneratedFile(outFilePath)

    def saveAltStoryTextDefault(self):
        fileText = self.getStoredGameText()
        #
        #outFilePath = self.makeChapterSaveDirFileName('dataout','_labeledLeads.txt')
        outFilePath = self.makeChapterSaveDirFileName('','_labeledLeads.txt')
        encoding = 'utf-8'
        self.saveAltStoryText(fileText, outFilePath, encoding)
        #
        self.addGeneratedFile(outFilePath)


    def saveAltStoryFilesAddLeads(self):
        for filePath in self.storyFileList:
            self.saveAltStoryFile(filePath)
    

    def saveAltStoryFile(self, filePath):
        outFilePath = filePath.replace('.txt','.labeled')
        if (outFilePath == filePath):
            outFilePath = filePath + '.labeled'
        jrprint('Saving version of storyfile with labels added: {}'.format(outFilePath))
        # load it
        encoding = self.getOptionValThrowException('storyFileEncoding')
        fileText = jrfuncs.loadTxtFromFile(filePath, True, encoding)
        #
        self.saveAltStoryText(fileText, outFilePath, encoding)


    def saveAltStoryText(self, fileText, outFilePath, encoding):
        # 
        leadHeadRegex = re.compile(r'^# ([^:\(\)\/]*[^\s])(\s*\(.*\))?(\s*\/\/.*)?$')
        # walk it and write it
        with open(outFilePath, 'w', encoding=encoding) as outfile:
            fileText.replace('\r\n','\n')
            lines = fileText.split('\n')
            for line in lines:
                # fixup \r\n lines?
                matches = leadHeadRegex.match(line)
                if (matches is not None):
                    # got a match - can we find an id?
                    leadId = matches[1].strip()
                    [existingLeadRow, existingRowSourceKey] = self.getHlApi().findLeadRowByLeadId(leadId)
                    if (not existingLeadRow is None):
                        # found a lead
                        label = self.calcLeadLabelForLeadRow(existingLeadRow)
                        if (':' in label) or ('(' in label) or (')' in label):
                            label = '"{}"'.format(label)
                        line = '# {}: {}'.format(leadId, label)
                        if (matches.group(2) is not None):
                            line += matches.group(2)
                        if (matches.group(3) is not None):
                            line += matches.group(3)

                #
                outfile.write(line+'\n')
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
    def loadStoryFileIntoBlocks(self, filePath):
        jrprint('Loading story file: "{}"'.format(filePath))
        sourceLabel = 'FILE "{}"'.format(filePath)
        encoding = self.getOptionValThrowException('storyFileEncoding')
        fileText = jrfuncs.loadTxtFromFile(filePath, True, encoding)
        # parse text file into blocks
        #
        self.parseStoryTextIntoBlocks(fileText, sourceLabel)



    def parseStoryTextIntoBlocks(self, text, sourceLabel):
        headBlock = None
        curTextBlock = None
        curText = ''
        inSingleLineComment = False
        inSingleLineHead = False
        inBlockCommentDepth = 0
        inCodeBlackDepth = 0
        inRaw = False
        lineNumber = 0
        lineNumberStart = 0
        posOnLine = -1
        cprev = ''
        inDoubleQuotes = False
        #
        self.storedGameTextAdd(text)
        #
        # add head comments to text so we skip all beginning stuff
        text = '# comments\n' + text
        #
        text = self.textReplacementsEarlyMarkdown(text, sourceLabel)
        #
        validShortCodeStartCharacterList = 'abcdefghijklmnopqrstuvwxyz'
        #
        trackEnclosusers = {'comment': [], 'code': []}
        #
        # add newline to text to make sure we handle end of last line
        text = text + '\n'
        textlen = len(text)
        #
        i = -1
        while (True):
            i += 1
            if (i>=textlen):
                break
            # handle end of previous line
            if (cprev == '\n'):
                # last character was end of line
                posOnLine = 0
                lineNumber += 1
                # reset double quotes (kludge)
                inDoubleQuotes = False
            else:
                posOnLine += 1
            #  get this and next char
            c = text[i]
            cprev = c
            if (i<textlen-1):
                cnext = text[i+1]
            else:
                cnext = ''
            #



            if (c=='\n'):
                # FIRST we need to kick out of single line comment (very imp)
                if (inSingleLineComment):
                    # single line comments end at end of line
                    inSingleLineComment = False
                    # now we drop down to handle end of single line head

                if (inSingleLineHead):
                    # process the single line head
                    inSingleLineHead = False
                    curText = curText.strip()
                    headBlock = self.makeBlockHeader(curText, sourceLabel, lineNumber, 'lead')
                    self.addHeadBlock(headBlock)
                    if ('raw' in headBlock['properties']) and (headBlock['properties']['raw']==True):
                        # raw mode grabs EVERYTHING as text until the next header
                        inRaw = True
                    # clear current text
                    curText = ''
                    continue





            # warnings
            if (not inRaw):
                if (c=='#') and (cnext==' ') and (posOnLine==0) and ((inCodeBlackDepth>0) ):
                    jrprint('WARNING: got a header inside a code block; source: {} line: {} pos: {}'.format(sourceLabel, lineNumber, posOnLine))
                if (c=='#') and (cnext==' ') and (posOnLine==0) and ((inBlockCommentDepth>0) ):
                    jrprint('WARNING: got a header inside a comment block; source: {} line: {} pos: {}'.format(sourceLabel, lineNumber, posOnLine))

                if (c=='#') and (cnext!=' ') and (cnext!='#') and (posOnLine<=1):
                    # probably an error
                    self.raiseParseException('#LEAD without space encountered at start of line -- this is an error; you must have a space after the #.', i, posOnLine, lineNumber, text, sourceLabel)
                    #jrprint('WARNING!!!!!!!: got a #lead syntax without SPACE after the # this is almost always an error; source: {} line: {} pos: {}'.format(sourceLabel, lineNumber, posOnLine))
           

            if (inSingleLineComment):
                # we are on a comment line, just ignore it
                continue
            #
            if (c=='/') and (cnext=='*'):
                # blockComment start
                i+=1
                inBlockCommentDepth += 1
                if (inBlockCommentDepth==1):
                    # clear current text block
                    curTextBlock = None
                trackEnclosusers['comment'].append('line {} pos {}'.format(lineNumber,posOnLine))
                continue
            if (c=='*') and (cnext=='/'):
                # blockComment end
                if (inBlockCommentDepth==0):
                    self.raiseParseException('End of block comment encountered (*/) without matching start comment block (/*).', i, posOnLine, lineNumber, text, sourceLabel)
                i+=1
                inBlockCommentDepth -= 1
                trackEnclosusers['comment'].pop()
                if (inBlockCommentDepth<0):
                    self.raiseParseException('End of comment block "*/" found without matching start.', i, posOnLine, lineNumber, text, sourceLabel)
                continue
            if (inBlockCommentDepth>0):
                # in multi-line comment, ignore it
                continue

            if (c=='"') or (c=='“') or (c=='”'):
                # toggle in double quotes
                inDoubleQuotes = not inDoubleQuotes
                # we use this to ignore // looking comment which could be url

            #
            if (c=='/') and (cnext=='/') and (not inDoubleQuotes):
                # single comment line start
                inSingleLineComment = True
                continue



            if (inRaw):
                # grabbing everything until we get a valid next head block
                if (c=='#') and (cnext==' ') and (posOnLine==0):
                    # we got something new
                    inRaw = False
                else:              
                    # raw text glob
                    if (curTextBlock is None):
                        # create new text block
                        curTextBlock = self.makeBlockText(sourceLabel, lineNumber)
                        self.addChildBlock(headBlock, curTextBlock)
                    # add character to textblock
                    curTextBlock['text'] += c
                    continue

            # comments after this


            #
            if (c=='{') and (not inSingleLineHead):
                # code block start
                inCodeBlackDepth += 1
                trackEnclosusers['code'].append('line {} pos {}'.format(lineNumber,posOnLine))
                if (inCodeBlackDepth==1):
                    # outer code block { does not capture
                    # clear current text block
                    curTextBlock = None
                    codeBlockStartLineNumber = lineNumber
                    lastStartLabelCodeBlock = 'line {} pos {}'.format(lineNumber,posOnLine)
                    continue
            if (c=='}') and (not inSingleLineHead):
                # code block end
                inCodeBlackDepth -= 1
                trackEnclosusers['code'].pop()
                if (inCodeBlackDepth<0):
                    self.raiseParseException('End of code block "}" found without matching start.', i, posOnLine, lineNumber, text, sourceLabel)
                if (inCodeBlackDepth==0):
                    # close of code block
                    curText = curText.strip()
                    block = self.makeBlockCode(curText, sourceLabel, codeBlockStartLineNumber, False)
                    self.addChildBlock(headBlock, block)
                    # clear current text to prepare for next block section
                    curText = ''
                    # out code block } does not capture
                    continue
            #
            if (c=='$') and (cnext in validShortCodeStartCharacterList) and (not inSingleLineHead) and (inCodeBlackDepth==0):
                # got a shorthand code line (does not use {} but rather of the form $func(params))
                # just consume it all now
                [shortCodeText, resumePos] = self.consumeShortCodeFromText(text, sourceLabel, lineNumber, posOnLine, i+1)
                if (resumePos==-1):
                    # false alarm no shortcode
                    pass
                else:
                    # got some shortcode
                    shortCodeText = shortCodeText.strip()
                    block = self.makeBlockCode(shortCodeText, sourceLabel, lineNumber, True)
                    self.addChildBlock(headBlock, block)
                    # clear current text to prepare for next block section
                    curText = ''
                    curTextBlock = None
                    i = resumePos-1
                    continue
            #
            if (c=='#') and (cnext==' ') and (posOnLine==0) and (not inSingleLineHead) and (inCodeBlackDepth==0):
                # "#" at start of line followed by space means we have a header
                # skip next char
                i+=1
                inSingleLineHead = True
                # clear current text block
                curTextBlock = None
                continue
            #
            if (not inSingleLineHead) and (inCodeBlackDepth==0) and (not inSingleLineComment) and (inBlockCommentDepth==0):
                # we are in a text block
                if (curTextBlock is None):
                    # create new text block
                    curTextBlock = self.makeBlockText(sourceLabel, lineNumber)
                    self.addChildBlock(headBlock, curTextBlock)
                # add character to textblock
                curTextBlock['text'] += c
            else:
                # accumulating text for later block use
                # add c to current text (be in codeblock, or text, or header)
                curText += c

        # make sure didnt end in comments, etc.
        if (inSingleLineHead):
            self.raiseParseException('Unexpected end of text while parsing "#" header.', i, posOnLine, lineNumber, text, sourceLabel)
        if (inCodeBlackDepth>0):
            stackHistoryString = ';'.join(trackEnclosusers['code'])
            self.raiseParseException('Unexpected end of text while inside code block [stack {}].'.format(stackHistoryString), i, posOnLine, lineNumber, text, sourceLabel)
        if (inBlockCommentDepth>0):
            stackHistoryString = ';'.join(trackEnclosusers['comment'])
            self.raiseParseException('Unexpected end of text while inside comment block  [stack {}].'.format(stackHistoryString), i, posOnLine, lineNumber, text, sourceLabel)

        # and eof which can help stop us from following one lead to subsequent one from another file
        block = self.makeBlockEndFile(sourceLabel, lineNumber)
        self.addChildBlock(headBlock, block)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
    def raiseParseException(self, msg, posInText, posOnLine, lineNumber, text, sourceLabel):
        msgExpanded = 'Parsing error: {} in {} at line {} pos {}.'.format(msg, sourceLabel, lineNumber, posOnLine)
        jrprint(msgExpanded)
        raise Exception(msgExpanded)

    def addParseWarning(self, msg, posInText, posOnLine, lineNumber, text, sourceLabel):
        msgExpanded = 'Parsing error: {} in {} at line {} pos {}.'.format(msg, sourceLabel, lineNumber, posOnLine)
        self.addWarning(msgExpanded)
# ---------------------------------------------------------------------------





























































# ---------------------------------------------------------------------------
    def addHeadBlock(self, headBlock):
        self.headBlocks.append(headBlock)

    def addChildBlock(self, headBlock, block):
        if (headBlock is None):
            self.raiseBlockException(block, 0, 'Child block ({}) specified but no previous parent headblock found.'.format(block['type']))

        # add as child block
        if ('blocks' not in headBlock):
            headBlock['blocks'] = []
        headBlock['blocks'].append(block)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def makeBlockEndFile(self, sourceLabel, lineNumber):
        block = self.makeBlock(sourceLabel, lineNumber, 'eof')
        return block

    def makeBlockText(self, sourceLabel, lineNumber):
        block = self.makeBlock(sourceLabel, lineNumber, 'text')
        return block

    def makeBlockCode(self, codeText, sourceLabel, lineNumber, embeddedShortCode):
        block = self.makeBlock(sourceLabel, lineNumber, 'code')
        block['text'] = codeText
        block['properties']['embeddedShortCode'] = embeddedShortCode
        return block

    def makeBlock(self, sourceLabel, lineNumber, blockType):
        # create it
        block = {}
        block['sourceLabel'] = sourceLabel
        block['lineNumber'] = lineNumber
        block['type'] = blockType
        block['text'] = ''
        block['properties'] = {}
        # return it
        return block
# ---------------------------------------------------------------------------
    

# ---------------------------------------------------------------------------
    def makeBlockHeader(self, headerText, sourceLabel, lineNumber, defaultHeaderType):
        #
        block = self.makeBlock(sourceLabel, lineNumber, 'header')

        # parse the header
        # ATTN: this needs to be recoded to not use regex and to support quotes labels that can contain ()
        # this checks for things that look like:
        #   ID STRING
        #   ID STRING: ID LABEL HERE
        #   ID STRING (extra options here)
        #   ID STRING: ID LABEL HERE (extra options here)
        #   ID STRING: (extra options here)

        # manual parse
        pos = 0
        [id, pos, nextc] = self.parseConsumeFunctionCallArgNext(block, headerText, pos, [':','(', ''])
        if (nextc==':'):
            [label, pos, nextc] = self.parseConsumeFunctionCallArgNext(block, headerText, pos+1, ['(', ''])
        else:
            label = None
        if (nextc=='('):
            argString = headerText[pos:]
        else:
            argString = ''

        
        linePos = 0
        # args first taken from any explicit ly passed
        if (argString!=''):
            [properties, pos] = self.parseFuncArgs('header', argString, sourceLabel, lineNumber, linePos)
        else:
            properties = {}

        # now set id and label
        if ('id' not in properties):
            properties['id'] = id
        else:
            id = properties['id']

        # label
        if ('label' not in properties):
            properties['label'] = label

        # default header subtype arg
        if ('type' not in properties):
            if (re.match('^doc\.(.*)$', id) is not None):
                properties['type'] = 'doc'
            elif (re.match('^hint\.(.*)$', id) is not None):
                properties['type'] = 'hint'
            else:
                properties['type'] = defaultHeaderType

        # special ids
        self.handleSpecialHeadIdProperties(id, properties)


        # store properties
        block['properties'] = properties

        return block
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def handleSpecialHeadIdProperties(self, id, properties):
        # kludge to handle specially named head leads/sections
        if (id=='options'):
            properties['type']= 'options'
            properties['raw'] = True
        if (id=='comments'):
            properties['type']= 'comments'
            properties['raw'] = True
        if (id=='cover'):
            properties['noid']= True
            properties['section'] = 'cover'
            properties['map'] = 'false'
            if (not 'stop' in properties):
                properties['stop'] = True
        if (id=='toc'):
            properties['section'] = 'toc'
            if (not 'stop' in properties):
                properties['stop'] = True
        if (id=='setup'):
            properties['section'] = 'debugReport'
            properties['render'] = False
        if (id=='summary'):
            properties['section'] = 'cover'
            properties['map'] = 'false'
            properties['idlabel'] = 'false'
            if (not 'stop' in properties):
                properties['stop'] = True
        if (id=='debugReport'):
            properties['noid']= True
            properties['section'] = 'debugReport'
            if (not 'stop' in properties):
                properties['stop'] = True
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
    def consumeShortCodeFromText(self, text, sourceLabel, lineNumber, posOnLine, textPos):
        # return [shortCodeText, resumePos]
        remainderText = text[textPos:]
        matches = re.match(r'^([a-z][A-Za-z0-9_]*)(\(.*)$', remainderText, re.MULTILINE)
        if (matches is None):
            # not a shortcode
            # let's see if we want to ERROR or warn
            matches = re.match(r'^([a-z][A-Za-z0-9_]*)([^A-Za-z0-9_].*)$', remainderText, re.MULTILINE)
            if (matches is None):
                matches = re.match(r'^([a-z][A-Za-z0-9_]*)(\b.*)$', remainderText, re.MULTILINE)
            if (matches is not None):
                # warning error
                word = matches.group(1)
                msg = 'Looks like we found a shortcode function "{}" that should have a () at end but is something else.'.format(word)
                if (word in self.argDefs):
                    # certainly an error
                    self.raiseParseException(msg, textPos, posOnLine, lineNumber, text, sourceLabel)
                    pass
                else:
                    # probably an error
                    if (True):
                        self.raiseParseException(msg, textPos, posOnLine, lineNumber, text, sourceLabel)
                    else:
                        self.addParseWarning(msg, textPos, posOnLine, lineNumber, text, sourceLabel)
            return ['',-1]
        funcName = matches[1]
        argText = matches[2]
        [argVals, afterPos] = self.parseFuncArgs(funcName, argText, sourceLabel, lineNumber, posOnLine)
        parsedParamLen = afterPos+1
        codeFullText = funcName + argText[0:parsedParamLen-1]
        returnPos = textPos + len(funcName) + parsedParamLen - 1
        return [codeFullText, returnPos]
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def parseFuncArgs(self, funcName, text, sourceLabel, lineNumber, posOnLine):
        # expect comma separated list of possibly named arguments
        argVals = {}

        # now grab inside ()
        # this can be TRICKY because of nesting quoutes escaped characters etc
        #return tuple [args,pos] where pos is position of the ) at the end

        # struct for reporting errors
        block = {'sourceLabel': sourceLabel, 'lineNumber': lineNumber}

        # what args do we expect for this function
        argDefs = self.funcArgDef(funcName)
        namedArgs = argDefs['named'] if ('named' in argDefs) else []
        positionalArgs = argDefs['positional'] if ('positional' in argDefs) else namedArgs
        #positionalArgs = namedArgs
        requiredArgs = argDefs['required'] if ('required' in argDefs) else []


        # confirm we start with ()
        pos = 0
        if (text[pos]!='('):
            self.raiseBlockExceptionAtPos(block, pos, 'Expected function name')
            return False 

        # iterate through all comma separated params
        isDone = False
        argIndex = -1
        pos += 1
        while (not isDone):
            ePos = pos
            [key, val, pos, isDone] = self.parseConsumeFunctionCallArgPairNext(block, text, pos)
            # ATTN: 12/26/23 new to add code here to ensure its legal parameter (positional or named)
            # parsed a paramPair val
            # add it
            argIndex += 1
            if (val=='') and (key is None):
                # no arg available
                if (not isDone):
                    self.raiseBlockExceptionAtPos(block, posOnLine+ePos, 'Got blank arg but not done with args ({}) passed to function {}.'.format(argIndex, funcName))
                    return False 
            elif (key is None):
                # its positional; convert to argdef defined prop name
                if (len(positionalArgs)<=argIndex):
                    self.raiseBlockExceptionAtPos(block, posOnLine+ePos, 'Too many args ({}) passed to function {}.'.format(argIndex, funcName))
                    return False 
                propName = positionalArgs[argIndex]
                argVals[propName] = val
            else:
                # use the key
                if (key not in namedArgs):
                    self.raiseBlockExceptionAtPos(block, posOnLine+ePos, 'Unknown named parameter ({}) passed to function {}.'.format(key, funcName))
                    return False 
                argVals[key] = val

        # ATTN: 12/26/23 need to add code here to make sure all REQUIRED params are passed
        for key in requiredArgs:
            if (key not in argVals):
                self.raiseBlockExceptionAtPos(block, posOnLine, 'Missing required arg({}) passed to function call {}.'.format(key, funcName))
                return False   

        # return parsed argVals and pos after end of parsing which should be ')' location
        return [argVals, pos]
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
    def parseConsumeFunctionCallArgPairNext(self, block, blockText, startPos):
        key = None
        pos =  startPos
        stopCharList = [',' , '=' , ')']
        #

        # get first val
        [val, pos, nextc] = self.parseConsumeFunctionCallArgNext(block, blockText, pos, stopCharList)

        #c = blockText[pos]
        c = nextc
        if (c == '='):
            # we have a named param
            key = val
            pos += 1
            [val, pos, nextc] = self.parseConsumeFunctionCallArgNext(block, blockText, pos, stopCharList)
            #c = blockText[pos]
            c = nextc
        if (c==')'):
            isDone = True
        elif (c==','):
            # more params left
            isDone = False
        else:
            # error syntax
            self.raiseBlockExceptionAtPos(block, startPos, 'Syntax error while parsing function call parameters')
            return False 
        # advance over comma )
        pos += 1

        # advance following whitespace? i dont think we want to
        if (False):
            textlen = len(blockText)
            while (pos<textlen) and (blockText[pos].isspace()):
                pos += 1
        # return
        return [key, val, pos, isDone]



    def parseConsumeFunctionCallArgNext(self, block, blockText, startPos, stopCharList):
        # parse next comma separate val or var=val
        wrapperCharList = ['"', "'", '{', '“', '”']
        textlen = len(blockText)

        # go to first non-space character
        pos = startPos
        while (blockText[pos].isspace()) and (pos<textlen):
            pos += 1
        if (pos>=textlen):
            self.raiseBlockExceptionAtPos(block, startPos, 'Unexpected end inside function call parameters')
            return False 

        # skip comments
        pos = self.skipComments(block, blockText, pos)
        extractedText = ''

        # ok now see if we have an ENCLOSING character
        c = blockText[pos]
        openingChar = ''
        keepFinalClose = False
        if (c in wrapperCharList):
            # yes we have an enclosing
            if (c=='{'):
                openingChar = '{'
                closingChar = '}'
                keepFinalClose = True
                extractedText = c
            elif (c=='“'):
                openingChar = '“'
                closingChar = '”'
                keepFinalClose = False
                extractedText = ''
            elif (c=='('):
                openingChar = '('
                closingChar = ')'
                keepFinalClose = True
                extractedText = c
            else:
                openingChar = ''
                closingChar = c
                keepFinalClose = False
            wrapperDepth = 1
            # advance inside
            pos += 1
        else:
            closingChar = None
            wrapperDepth = 0

        # loop
        wasWrapped = (wrapperDepth>0)
        startContentPos = pos
        inEscapeNextChar = False
        expectingEnd = False
        while (pos<textlen):
            # skip comments
            c = blockText[pos]
            if (inEscapeNextChar):
                # this character is escaped
                extractedText += jrfuncs.escapedCharacterConvert(c)
                inEscapeNextChar = False
            else:
                # skip comments
                if (wrapperDepth==0) or (True):
                    # do we want to do this even if in wrapper? YES for now (note this is different from most programming languages)
                    pos = self.skipComments(block, blockText, pos)
                    c = blockText[pos]

                if (wrapperDepth>0):
                    # inside wrapper the only thing we care about is close of wrapper
                    if (c=='\\'):
                        # escape
                        inEscapeNextChar = True
                        pass
                    elif (c==closingChar):
                        # got close of wrapper
                        wrapperDepth -= 1
                        if (wrapperDepth==0):
                            expectingEnd = True
                        if (keepFinalClose) or (wrapperDepth>0):
                            extractedText += c
                        if (wrapperDepth<0):
                            self.raiseBlockExceptionAtPos(block, startContentPos, 'Syntax error while parsing function call parameters; unexpected unbalanced wrapper close symbol')
                            return False 
                    elif (c==openingChar):
                        wrapperDepth += 1
                        extractedText += c
                    else:
                        # stay in wrapper
                        extractedText += c
                        pass
                else:
                    # not in wrapper
                    #
                    if (c in stopCharList):
                        # this ends our parse since we are not in wrapper
                        break
                    elif (expectingEnd) and (not c.isspace()):
                        # error since we thought we were done
                        self.raiseBlockExceptionAtPos(block, startContentPos, 'Syntax error while parsing function call parameters; expecting end but there was something else')
                        return False 
                    # characters allowed
                    elif (c=='\\'):
                        # escape
                        inEscapeNextChar = True
                        pass
                    else:
                        # just a normal character
                        extractedText += c
            # advance to next char
            pos += 1

        if (inEscapeNextChar):
            self.raiseBlockExceptionAtPos(block, startContentPos, 'Syntax error (unexpected end of line while in escape char) while parsing function call parameters')
            return False 
        if (wrapperDepth>0):
            self.raiseBlockExceptionAtPos(block, startContentPos, 'Syntax error (unexpected end of line while in wrapper quotes/brackets/etc) while parsing function call parameters')
            return False 

        if (pos>=textlen):
            if (not '' in stopCharList):
                self.raiseBlockExceptionAtPos(block, startContentPos, 'Syntax error (unexpected end of line) while parsing function call parameters')
                return False 
            else:
                # last char '' to mean end of string
                c = ''

        if (not wasWrapped):
            # trim spaces front and back if not in wrapper
            extractedText = extractedText.strip()
        #    
        return [extractedText, pos, c]
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def parseFunctionCallAndArgs(self, block, text):
        # 
        sourceLabel = block['sourceLabel']
        lineNumber = block['lineNumber']
        linePos = 0
        pos = 0
        #

        if (text.strip()==''):
            # just an empty placeholder
            return ['empty', {}, 0]

        [funcName, pos, nextc] = self.parseConsumeFunctionCallArgNext(block, text, pos, ['(', ''])
        if (nextc=='('):
            argString = text[pos:]
        else:
            argString = ''

        # args first taken from any explicit ly passed
        if (argString!=''):
            [properties, pos] = self.parseFuncArgs(funcName, argString, sourceLabel, lineNumber, linePos)
        else:
            properties = {}

        return [funcName, properties, pos]
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def skipComments(self, block, text, pos):
        startPos = pos
        textlen = len(text)
        blockCommentDepth = 0

        while (pos<textlen):
            if (text[pos]=='/') and (text[pos+1]=='/'):
                # skip till end of line
                pos += 2
                while (pos<textlen) and (text[pos-1]!='\n'):
                    pos += 1
            elif (text[pos]=='/') and (text[pos+1]=='*'):
                blockCommentDepth += 1
                pos += 2
                while (pos<textlen-1):
                    if (text[pos]=='*') and (text[pos+1]=='/'):
                        blockCommentDepth -= 1
                        pos += 2
                        if (blockCommentDepth==0):
                            break
                        if (blockCommentDepth<0):
                            self.raiseBlockExceptionAtPos(block, pos-2, 'Syntax error close block comment without start */ unterminated.')
                            return False
                    elif (text[pos]=='/') and (text[pos+1]=='*'):
                        # nested block comment
                        blockCommentDepth += 1
                        pos += 2
                    else:
                        # still in block continue
                        pos += 1
            else:
                break

        if (blockCommentDepth!=0):
            self.raiseBlockExceptionAtPos(block, startPos, 'Syntax error nested block comments /* */ unterminated.')
            return False

        return pos
# ---------------------------------------------------------------------------





    







































# ---------------------------------------------------------------------------
    def processHeadBlocks(self):
        # first we make a pass for EARLY stage processing
        # we need to do this in multiple stages because we do NOT want to fully process a lead if it is overwritten by another later
        jrprint('Parsing {} head blocks..'.format(len(self.headBlocks)))
        for block in self.headBlocks:
            self.processHeadBlock(block)


    def processLeads(self):
        # now process leads
        jrprint('Processing {} leads..'.format(len(self.leads)))
        # note we have to get keys as list here and then iterate because self.leads changes
        leadCount = len(self.leads)
        for i in range(0,leadCount):
            lead = self.leads[i]
            self.processLeadStage1(lead,i)
        
        # we now do a second stage walking through leads fixing up BLANK ones that should copy the ones below them
        leadCount = len(self.leads)
        for i in range(0, leadCount):
            lead = self.leads[i]
            self.processLeadStage2(lead,i)

        leadStats = self.calcLeadStats()
        jrprint('FINISHED PROCESSING; SUMMARY STATS: ' + leadStats['summaryString'] + ".")



    def databaseDebugLeads(self):
        jrprint('Database debugging {} leads..'.format(len(self.leads)))
        # note we have to get keys as list here and then iterate because self.leads changes
        leadCount = len(self.leads)
        for i in range(0,leadCount):
            lead = self.leads[i]
            self.databaseDebugLead(lead)


    def calcLeadStats(self):
        if ('count' in self.leadStats) and (self.leadStats['count'] == len(self.leads)):
            return self.leadStats
        # recalc
        textLength = 0
        wordCount = 0
        for lead in self.leads:
            textLength += len(lead['text'])
            wordCount += len(lead['text'].split(' '))
        self.leadStats['textLength'] = textLength
        self.leadStats['count'] = len(self.leads)
        self.leadStats['wordCount'] = wordCount
        self.leadStats['summaryString'] = '{} Leads / {:.2f}k of text / {:,} words'.format(self.leadStats['count'], self.leadStats['textLength'] / 1000, self.leadStats['wordCount'])
        return self.leadStats
    
    
    def getLeadStats(self):
        return self.leadStats



    def processHeadBlock(self, block):
        # there's THREE things that happen when parsing a block.
        # 1) we can parse functions that set PROPERTIES for the block (like identify it as a lead, and set its LEAD ID etc)
        # 2) we can parse functions that do replacements inside the text of the block
        # 3) we can parse functions that create other data (more leads, etc)
        #jrprint('Processing a block..')

        # now post-process it based on type
        properties = block['properties']
        blockType = properties['type']
        if (blockType is None):
            self.raiseBlockException(block, 0, 'Block encountered but of unknown type.')

        if (blockType in ['lead', 'doc', 'hint']):
            # it's a lead type of block, our most common
            id = properties['id']
            existingLead = self.findLeadById(id, True)
            if (existingLead is not None):
                existingLegalValues = ['defer', 'overwrite']
                errorMsg = None
                # already have a lead of with this id
                existingBehaviorNew = properties['existing'] if ('existing' in properties) else None
                propertiesPrior = existingLead['properties']
                existingBehaviorPrior = propertiesPrior['existing'] if ('existing' in propertiesPrior) else None
                # ok now throw an error if we get conflicting instructions
                if (existingBehaviorNew is None) and (existingBehaviorPrior is None):
                    # no instructions given what to do
                    errorMsg = 'The "existing" directive was not found in either lead, and must be specified on one or both leads [defer|overwrite]'
                elif ((existingBehaviorNew =='overwrite') or (existingBehaviorNew is None)) and ((existingBehaviorPrior is None) or (existingBehaviorPrior=='defer')):
                    # this is fine, we overwrite
                    existingBehaviorNew = 'overwrite'
                elif ((existingBehaviorNew == 'defer') or (existingBehaviorNew is None)) and ((existingBehaviorPrior is None) or (existingBehaviorPrior=='overwrite')):
                    # this is fine, we defer
                    existingBehaviorNew = 'defer'
                elif (existingBehaviorNew == 'defer') and (existingBehaviorPrior=='defer'):
                    # this is fine, we defer; neither care
                    existingBehaviorNew = 'defer'
                elif (existingBehaviorNew == 'overwrite') and (existingBehaviorPrior=='overwrite'):
                    # this is problem, both want to dominate
                    errorMsg = 'The "existing" directive was found in both leads and conflicts (both want "overwrite"); one should be set to "defer"'
                else:
                    # not understood
                    errorMsg = ''
                    if (existingBehaviorNew not in existingLegalValues):
                        errorMsg += 'Uknown value for "existing" directive in new lead (). '.format(existingBehaviorNew)
                    if (existingBehaviorPrior not in existingLegalValues):
                        errorMsg += 'Uknown value for "existing" directive in prior lead (). '.format(existingBehaviorNew)
                #
                if (errorMsg is not None):
                    # we have a conflict error
                    errorMsg += ' Prior lead with same id found in {} around line #{}'.format(existingLead['sourceLabel'], existingLead['lineNumber'])
                    self.raiseBlockException(block, 0, errorMsg)
                #
                if (existingBehaviorNew == 'defer'):
                    # there is an existing lead with this id and we are set to defer, so we dont add
                    warningMsg = 'WARNING: New lead with duplicate id({}) is being ignored because lead directive set to existing=defer; Prior lead with same id found in {} around line #{}.'.format(id, existingLead['sourceLabel'], existingLead['lineNumber'])
                    jrprint('WARNING: ' + warningMsg)
                    return
            else:
                # no other lead with this id so no conflict
                pass

            ignoreFlag = jrfuncs.getDictValueFromTrueFalse(properties, 'ignore', False)
            if (ignoreFlag):
                warningMsg = 'WARNING: Lead with id="{}" is being ignored because ignore=true in lead directive; lead is from {} around line #{}'.format(id, block['sourceLabel'], block['lineNumber'])
                jrprint('WARNING: ' + warningMsg)
                return

            # block text -- ATTN: we now do this in a second PASS
            blockText= ''

            # render id
            autoid = jrfuncs.getDictValueFromTrueFalse(properties, 'autoid', False)
            if (autoid):
                # assign a free leads id
                renderId = self.assignDynamicLeadId(id, block)
                properties['renderId'] = renderId
                properties['autoid'] = autoid
            else:
                renderId = id
            properties['renderId'] = renderId

            map = jrfuncs.getDictValueOrDefault(properties, 'map', '')
            properties['map'] = map

            # store section name in properties
            properties['sectionName'] = self.makeSectionNameForHeadBlock(block, id, renderId)

            # for mindmaps
            properties['mtype'] = blockType

            # ok ADD the new lead by copying values from block
            lead = {'id': self.canonicalLeadId(id), 'block': block, 'properties': properties, 'text': blockText, 'sourceLabel': block['sourceLabel'], 'lineNumber': block['lineNumber']}
            leadIndex = self.addLead(lead)

            # auto define document tags
            #matches = re.match(r'^doc\.(.*)$', id)
            #if (matches is not None):
            if (properties['type']=='doc'):
                # auto create doc tag for all docs
                tagDict = self.doCreateOrFindTagForLead(lead, 'doc')
            elif (properties['type']=='hint'):
                # auto create doc tag for all checks
                tagDict = self.doCreateTagForHintLead(lead)


        elif (blockType=='options'):
            # special options, just execute; do it here early
            self.processOptionsBlock(block)

        elif (blockType=='comments'):
            # do nothing
            pass

        elif (blockType=='ignore'):
            # just a way to say ignore this block, comments, etc
            warningMsg = 'WARNING: Block is being ignored because blocktype={}; from {} around line #{}'.format(blockType, block['sourceLabel'], block['lineNumber'])
            jrprint('WARNING: ' + warningMsg)
            return
        else:
            # something OTHER than a lead
            raise Exception('Unsupported block type: "{}"'.format(blockType))
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
    def processOptionsBlock(self, block):
        jsonOptionString = self.childRawBlockText(block)

        # kludge fix up bad characters
        jsonOptionString = jrfuncs.fixupUtfQuotesEtc(jsonOptionString)

        # kludge so that line numbers in reported error are correct
        priorTextNewlineCount = int(block['lineNumber'])
        prorTextKludge= "\n" * (priorTextNewlineCount)
        jsonOptionString = prorTextKludge + jsonOptionString

        jsonOptions = json.loads(jsonOptionString)
        # set the WORKINGDIR options
        self.jroptionsWorkingDir.mergeRawDataForKey('options', jsonOptions)
        #
        # Change api version
        self.updateHlApiDirs()

        # store chapter name
        info = self.getOptionValThrowException('info')
        self.chapterName = jrfuncs.getDictValueOrDefault(info, 'name', 'UNNAMED')

# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
    def makeSectionNameForHeadBlock(self, block, id, renderId):
        properties = block['properties']
        if ('section' in properties):
            # explicit section 
            return properties['section']

        blockType = properties['type']
        #if (blockType == 'doc') or (re.match(r'^doc\.(.*)$', id) is not None):
        if (blockType == 'doc'):
            sectionName = 'Documents'
        elif (blockType == 'hint'):
            sectionName = 'Hints'
        elif (blockType == 'lead'):
            sectionName = 'Main.' + self.calcIdSection(renderId)
        else:
            sectionName = blockType
        #
        return sectionName
# ---------------------------------------------------------------------------

























































# ---------------------------------------------------------------------------
    def calcDoesLeadHaveContent(self, lead):
        headBlock = lead['block']
        if ('blocks' in headBlock):
            childBlocks = headBlock['blocks']
            if (len(childBlocks)>0):
                # it has children of some sort so nothing to do even if it has no text
                return True
        # no child blocks, no content
        return False
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def processLeadBothStages(self, lead, index):
        self.processLeadStage1(lead,index)
        self.processLeadStage2(lead,index)
# ---------------------------------------------------------------------------








    
    

# ---------------------------------------------------------------------------
    def processLeadStage1(self, lead, index):
        # stage 1 no longer does anything
        pass
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
    def processLeadStage2(self, lead, index):
        # first render the text for the lead
        # normal full text contents of the lead; note the second time lead is passed it is the behalfLead; for normal building of text this is the case; if the lead is built to embed elsewhere this will be different
        leadId = lead['id']
        leadProprties = lead['properties']
        debugInfo = leadProprties['label']
        jrprint('Stage 2: Processing lead {:.<20}... {}'.format(leadId, debugInfo))

        # manual warnings for leads
        warningVal = jrfuncs.getDictValueOrDefault(leadProprties, 'warning', None)
        if (warningVal is not None):
            msg = 'Manual warning set: {}'.format(warningVal)
            self.appendWarningLead(msg, lead)

        # handle list of leads where only the last one has content and the others inherit
        leadHasContent = self.calcDoesLeadHaveContent(lead)
        evaluationLead = None
        if (leadHasContent):
            evaluationLead = lead
        else:
            # try to copy from subsequent lead
            leadCount = len(self.leads)
            for i in range(index+1, leadCount):
                nextLead = self.leads[i]
                if (not self.calcDoesLeadHaveContent(nextLead)):
                    continue
                # ok we found one to copy from
                # we USED to just copy the text
                # but this is no longer good enough, we have to make copies of the blocks so we can evaluate them
                # NOTE this basically functions like an insertLead() to the last last
                evaluationLead = nextLead
                break

        # dynamic fix up of labels that depend on all labels being created
        # label from labelcontd.
        labelcontd = leadProprties['labelcontd'] if ('labelcontd' in leadProprties) else None
        if (labelcontd is not None):
            labelcontdLead = self.findLeadById(labelcontd, True)
            if (labelcontdLead is None):
                msg = 'Failed to find lead referenced in labelcontd setting.'
                self.raiseLeadException(lead,0,msg)
            labelcontdLeadLink = self.makeTextLinkToLead(labelcontdLead, None, False, True)
            lead['properties']['label'] = '{} ({}) contd.'.format(labelcontdLead['properties']['label'], labelcontdLeadLink)

        if (evaluationLead is None):
            self.addWarning('Could not find subsequent content to use for lead {}.'.format(leadId))
            lead['text'] = '***BLANK***'
            lead['reportText'] = '***BLANK***'
            return

        # AFTER we copy can we evaluate code?
        [normalText, reportText] = self.evaluateHeadBlockTextCode(evaluationLead, lead, {})
        lead['text'] = normalText
        lead['reportText'] = reportText
# ---------------------------------------------------------------------------
















































# ---------------------------------------------------------------------------
    def findLeadById(self, leadId, flagCheckRenderId):
        if (type(leadId) is not str):
            # already a lead?
            return leadId
        
        leadId = self.canonicalLeadId(leadId)

        for lead in self.leads:
            propLeadId = lead['id']
            if (propLeadId == leadId):
                return lead
            if (flagCheckRenderId):
                if (lead['properties']['renderId']==leadId):
                    return lead

        return None

    def addLead(self, lead):
        #jrprint('Storing lead: {}.'.format(leadId))

        duplcateLead = self.findLeadById(lead['id'], False)
        if (duplcateLead is not None):
            duplicateLeadBlock = duplcateLead['block']
            self.raiseLeadException(lead, 0, 'Duplicate lead id (matching lead at location {}, line #{})'.format(duplcateLead['sourceLabel'], duplcateLead['lineNumber']))

        leadIndex = len(self.leads)
        lead['leadIndex'] = leadIndex
        self.leads.append(lead)
        mapStyle = jrfuncs.getDictValueOrDefault(lead['properties'],'map','')
        propType = jrfuncs.getDictValueOrDefault(lead['properties'],'type','')
        if (propType=='doc_REN'):
            mapStyle = 'false'
        # add mind map
        if (mapStyle!='false'):
            self.createMindMapLead(lead, mapStyle)
        return leadIndex

    def canonicalLeadId(self, id):
        # uppercase
        #id = id.upper()
        # no spaces
        id = id.replace(' ','')
        # add space between letters and numbers (SHCD stye) - NO THIS CAUSES PROBLEMS; instead do this on display
        if (False):
            matches = re.match(r'^([A-Za-z]+)\s*\-?\s*([0-9]+)$', id)
            if (matches is not None):
                id = matches[1] + ' ' + matches[2]
        #
        return id

    def calcIdSection(self, id):
        matches = re.match(r'^([A-Za-z0-9][A-Za-z0-9\.]+)\.(.*)$', id)
        if (matches is not None):
            # HL style id
            return matches[1].upper()
        matches = re.match(r'^([A-Za-z0-9\.]+)\s*\-\s*(.*)$', id)
        if (matches is not None):
            # HL style id
            return matches[1].upper()
        matches = re.match(r'^([A-Za-z]+)\s*\-?\s*([0-9]+)$', id)
        if (matches is not None):
            # shcd style id
            return matches[1].upper()
        matches = re.match(r'^([0-9]+)\s*\-?\s*([A-Za-z]+)$', id)
        if (matches is not None):
            # shcd style id reverse
            return matches[2].upper()
        # unknown
        return ''
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def saveLeads(self):
        saveDir = self.getSaveDir()
        #dataSaveDir = saveDir + '/dataout'
        dataSaveDir = saveDir
        jrfuncs.createDirIfMissing(dataSaveDir)
        info = self.getOptionValThrowException('info')
        chapterName = self.getChapterName()
        outFilePath = dataSaveDir + '/' + chapterName + '_leadsout.json'
        #
        # sort
        self.sortLeadsIntoSections()
        #
        jrprint('Saving leads to: {}'.format(outFilePath))
        encoding = self.getOptionValThrowException('storyFileEncoding')
        with open(outFilePath, 'w', encoding=encoding) as outfile:
            leadsJson = json.dumps(self.rootSection, indent=2)
            outfile.write(leadsJson)
        # record it was written
        self.addGeneratedFile(outFilePath)
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
    def sortLeadsIntoSections(self):
        self.rootSection = {}
        # ATTN: TODO - seed with some initial sections?
        optionSections = self.getOptionVal('sections', self.getDefaultSections())
        self.rootSection['sections'] = jrfuncs.deepCopyListDict(optionSections)
        #self.createRootChildSection('Front', 'Front', '010')
        #self.createRootChildSection('Leads', 'Leads', '020')
        #self.createRootChildSection('Back', 'Back', '030')

        self.addMissingSections()

        #
        for lead in self.leads:
            leadId = lead['id']
            section = self.calcSectionForLead(lead)
            if ('leads' not in section):
                section['leads'] = {}
            section['leads'][leadId] = lead
        
        # now walk sections and sort leads and subsections
        if (len(self.rootSection)>0):
            self.sortSection(self.rootSection, 'index')


    def getDefaultSections(self):
        defaultSections = {
		"Briefings": {"label": "Briefings", "sort": "010", "leadSort": "index", "style": "onecolumn"},
		"Main": {"label": "Main Leads", "sort": "050", "leadSort": "alpha", "style": "onecolumn"},
		"End": {"label": "Conclusion", "sort": "100", "leadSort": "index", "style": "onecolumn"},
	    }
        return defaultSections
    

    def addMissingSections(self):
        if ('debugReport' not in self.rootSection['sections']):
            self.createRootChildSection('debugReport', {'label':'Debug Report', 'sort':'002a', 'leadSort':'index', 'style':'onecolumn', 'stop': True})
        if ('cover' not in self.rootSection['sections']):
            self.createRootChildSection('cover', {'label':'', 'sort':'002b', 'leadSort':'index', 'style':'onecolumn', 'stop': True, 'cleanPage': True})
        if ('toc' not in self.rootSection['sections']):
            self.createRootChildSection('toc', {'label':'Table of Conents', 'sort':'003a', 'leadSort':'index', 'style':'twocolumn', 'stop': True})
        if ('Documents' not in self.rootSection['sections']):
            self.createRootChildSection('Documents', {'label':'Documents', 'sort':'070', 'leadSort':'index', 'style':'solo', 'stop': 'documents', 'tombstones': False})
        if ('Front' not in self.rootSection['sections']):
            self.createRootChildSection('Front', {'label':'', 'sort':'003b', 'leadSort':'index', 'style':'onecolumn', 'stop': True})
        if ('Hints' not in self.rootSection['sections']):
            self.createRootChildSection('Hints', {'label':'Hints', 'sort':'090', 'leadSort':'alpha', 'stop': 'hints'})


    def createRootChildSection(self, id, propDict):
        parentSection = self.rootSection
        if ('sections' not in parentSection):
            # no children, add it
            parentSection['sections'] = {}
        if (id not in parentSection['sections']):
            parentSection['sections'][id] = propDict
            parentSection['sections'][id]['id'] = id


    def findTopSectionByid(self, id):
        parentSection = self.rootSection
        for k,v in parentSection['sections'].items():
            if (k==id):
                return v
        return None


    def sortSection(self, section, leadSort):

        # sort leads
        if ('leads' in section):
            if ('leadsort' in section):
                raise Exception('use of key "leadsort" when it should be "leadSort"')
            elif ('leadSort' in section):
                leadSort = section['leadSort']
            else:
                leadSort = 'alpha'
            #
            leads = section['leads']
            leadIds = list(leads.keys())
            # custom sort of lead ids
            if (True):
                leadIds.sort(key=lambda idStr: self.formatLeadIdForSorting(idStr, leads[idStr], leadSort))
                leadSorted = {i: leads[i] for i in leadIds}
                section['leads'] = leadSorted
            else:
                # sort by the RENDER id
                #section['leads'] = jrfuncs.sortDictByAKeyVal(section['leads'], 'renderId')
                section['leads'] = jrfuncs.sortDictByASecondaryKeyVal(section['leads'], 'properties', 'renderId')


        # now recursively sort child sections
        if ('sections' in section):
            childSections = section['sections']
            for childid, child in childSections.items():
                self.sortSection(child, leadSort)
            # and sort keys for child sections
            section['sections'] = jrfuncs.sortDictByAKeyVal(section['sections'], 'sort')


    def calcSectionForLead(self, lead):
        # return the child section for this lead, creating the path to it if needed
        properties = lead['properties']
        sectionName = properties['sectionName']
        # split it into dot separated chain
        sectionNameParts = sectionName.split('.')
        section = self.rootSection
        for sectionNamePart in sectionNameParts:
            section = self.findCreateChildSection(section, sectionNamePart)
        return section
    

    def findCreateChildSection(self, parentSection, sectionNamePart):
        if ('sections' not in parentSection):
            # no children, add it
            parentSection['sections'] = {}
        if (sectionNamePart not in parentSection['sections']):
            sectionSortVal = jrfuncs.zeroPadNumbersAnywhereInStringAll(sectionNamePart, 6)
            newSection = {'label': sectionNamePart, 'sort': sectionSortVal, 'leadSort': 'alpha', 'timed': True}
            parentSection['sections'][sectionNamePart] = newSection

        return parentSection['sections'][sectionNamePart]
# ---------------------------------------------------------------------------
































# ---------------------------------------------------------------------------
    def debug(self):
        jrprint('\n\n---------------------------\n')
        jrprint('Debugging hlParser:')
        jrprint('Base options: {}'.format(self.jroptions.getAllBlocks()))
        jrprint('Working dir options: {}'.format(self.jroptionsWorkingDir.getAllBlocks()))
        jrprint('Scan found {} lead files: {}.'.format(len(self.storyFileList), self.storyFileList))
        jrprint('\nTag map:')
        jrprint(self.tagMap)
        if (False):
            jrprint('Headblocks:\n')
            for block in self.headBlocks:
                blockDebugText = self.calcDebugBlockText(block)
                jrprint(blockDebugText)
        jrprint('---------------------------\n')
        self.mindMap.debug()


    def calcDebugBlockText(self, block):
        # just create a debug text for the block
        optionSummarizeChildBlocks = True
        tempBlock = jrfuncs.deepCopyListDict(block)
        if (optionSummarizeChildBlocks):
            if ('blocks' in tempBlock):
                tempBlock['blocks'] = len(tempBlock['blocks'])
        debugText = json.dumps(tempBlock, indent=2)
        return debugText


    def reportWarnings(self):
        errorCount = jrfuncs.getJrPrintErrorCount()
        if (errorCount>0):
            jrprint('{} errors.'.format(errorCount))
        #
        if (len(self.warnings)==0):
            jrprint('{} warnings.'.format(len(self.warnings)))
            return
        jrprint('{} warnings:'.format(len(self.warnings)))
        for index, warning in enumerate(self.warnings):
            jrprint('[{}]: {}'.format(index+1, warning['text']))
        jrprint('\n')

    def reportNotes(self):
        if (len(self.notes)==0):
            jrprint('{} notes.'.format(len(self.warnings)))
            return
        jrprint('{} notes:'.format(len(self.notes)))
        for index, note in enumerate(self.notes):
            jrprint('[{}]: {}'.format(index+1, note['text']))
        jrprint('\n')


    def reportSummary(self):
        leadStats = self.calcLeadStats()
        jrprint('SUMMARY STATS: ' + leadStats['summaryString'] + ".")
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def combineLinesToText(self, lines):
        lineText = ''
        for line in lines:
            lineText += line['text'] + '\n'
        lineText = lineText.strip()
        return lineText
# ---------------------------------------------------------------------------







# ---------------------------------------------------------------------------
    def resolveTemplateVars(self, text):
        text = text.replace('$templatedir', self.getBaseOptionVal('templatedir', ''))
        text = text.replace('$workingdir', self.getBaseOptionVal('workingdir', ''))
        text = text.replace('$basedir', self.getBaseOptionVal('basedir', ''))
        return text
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def raiseLeadException(self, lead, lineNumber, message):
        self.raiseBlockException(lead['block'], lineNumber, message + '; in lead {}'.format(lead['id']))

    def raiseBlockException(self, block, lineNumber, message):
        if ('id' in block):
            blockIdInfo = '(id = "{}")'.format(block['id'])
        else:
            blockIdInfo = ''
        #
        msg = 'Exception encountered while processing block {} from {} around line #{}: {}'.format(blockIdInfo, block['sourceLabel'], block['lineNumber']+lineNumber, message)
        jrException(msg)
        raise Exception(msg)

    def raiseBlockExceptionAtPos(self, block, pos, message):
        # go from pos to line # and pos
        if (not 'text' in block):
            lineNumber = 0
            linePos = 0
        else:
            [lineNumber, linePos] = self.countLinesInBlockUntilPos(block['text'], pos)
        #

        msg = message + ' (at pos {}).'.format(linePos)
        self.raiseBlockException(block, lineNumber, msg)


    def countLinesInBlockUntilPos(self, text, pos):
        lineNumber = 0
        linePos = 0
        for i in range(0,pos):
            c = text[i]
            if (c=='\n'):
                linePos = 0
                lineNumber += 1
        return [lineNumber, linePos]
# ---------------------------------------------------------------------------








# ---------------------------------------------------------------------------
    def formatLeadIdForSorting(self, idStr, lead, leadSort):
        
        properties = lead['properties']
        if ('sort' in properties) and (properties['sort']!=''):
            val = properties['sort']
            if (val=='index'):
                val = str(lead['leadIndex'])
        else:
            # if there are numbers at start or end then we will sort by id
            if (leadSort=='index'):
                # no digits at start or end, so use ADD order
                val = str(lead['leadIndex'])
            elif (leadSort=='') or (leadSort=='alpha'):
                #val = idStr
                val = properties['renderId']
            else:
                raise Exception('Unknown sort value: {} near {} line {}.'.format(leadSort, lead['sourceLabel'], lead['lineNumber']))
        digitlen = 6
        return jrfuncs.zeroPadNumbersAnywhereInStringAll(val, digitlen)
        numericalLeadRegex = re.compile(r'^(\d+)\-(.*)$')
        matches = numericalLeadRegex.match(idStr)
        if (matches is not None):
            prefix = int(matches[1])
            sortKey = '{:0>4}-{}'.format(prefix, matches[2])
            print('in with "{}" out with "{}"'.format(idStr, sortKey))
            return sortKey
        # leave as is
        return idStr
# ---------------------------------------------------------------------------
    


# ---------------------------------------------------------------------------
    def funcArgDef(self, funcName):
        # return dictionary defining args expected from this function
        if (funcName in self.argDefs):
            return self.argDefs[funcName]
        raise Exception('Unknown function name in funcArgDef: {}.'.format(funcName))
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def assignDynamicLeadId(self, id, block):
        # use a lead id from our unused list and keep track of it
        if (id in self.dynamicLeadMap):
            self.raiseBlockException(block, 0, 'Duplicate DYNAMIC lead id "{}" found previously assigned to a dynamic id; needs to be unique.'.format(id))
        renderId = self.consumeUnusedLeadId()
        oldLead = self.findLeadById(renderId, True)
        if (oldLead is not None):
            self.raiseBlockException(block, 0, 'ERROR: unused lead returned an id ({}) that already exists in lead table ({} at {}) for DYNAMIC lead id "{}"'.format(renderId, oldLead['sourceLabel'], oldLead['lineNumber'], id))
        self.dynamicLeadMap[id] = renderId
        return renderId
    
    def consumeUnusedLeadId(self):
        unusedLeadRow = self.getHlApi().popAvailableLead()
        if (unusedLeadRow is None):
            # not found, unavailable from list.
            # so instead make a random one
            while (True):
                randomid = 'R-{}{}{}{}'.format(random.randint(0, 9), random.randint(0, 9), random.randint(0, 9), random.randint(0, 9))
                oldLead = self.findLeadById(randomid, True)
                if (oldLead is None):
                    break
            return randomid

        leadid = unusedLeadRow['lead']
        return leadid
# ---------------------------------------------------------------------------














































# ---------------------------------------------------------------------------
# ok here is our new code to evaluate blocks
    def childRawBlockText(self, headBlock):
        if ('blocks' not in headBlock):
            return ''
        
        # ATTN: test 12/30/23 just combine all text lines
        # ATTN: TODO handle code blocks and conditionals
        txt = ''
        childBlocks = headBlock['blocks']
        for block in childBlocks:
            blockType = block['type']
            if (blockType=='text'):
                txt += block['text']
            elif (blockType=='code'):
                txt += block['text']
            else:
                self.raiseBlockException(block, 0, 'Unknown block type "{}"'.format(blockType))

        # trim
        txt = txt.strip()

        return txt
# ---------------------------------------------------------------------------
    






# ---------------------------------------------------------------------------
# ok here is our new code to evaluate blocks
    def evaluateHeadBlockTextCode(self, lead, behalfLead, evaluationOptions):
        # this now returns the tupe [normalText, reportText]
        headBlock = lead['block']
        if ('blocks' not in headBlock):
            return ['', '']
        
        # assemble
        text = ''
        reportText = ''
        context = {}
        #
        childBlocks = headBlock['blocks']
        movedBlockIdList = headBlock['movedBlocks'] if ('movedBlocks' in headBlock) else []
        #
        blockIndex = -1
        while (blockIndex<len(childBlocks)-1):
            blockIndex += 1
            if (blockIndex in movedBlockIdList):
                continue
            block = childBlocks[blockIndex]
            blockType = block['type']
            if (blockType=='text'):
                text += block['text']
                reportText += block['text']
            elif (blockType=='code'):
                textPositionStyle = self.calcTextPositionStyle(text)
                codeResult = self.evaluateCodeBlock(block, lead, textPositionStyle, behalfLead, evaluationOptions, context)
                if ('text' in codeResult):
                    text += codeResult['text']
                if ('reportText' in codeResult):
                    reportText += codeResult['reportText']
                #
                if ('action' in codeResult):
                    action = codeResult['action']
                    if (action in ['inline']):
                        # we want to create a new lead with contents of this one until next section
                        # label?
                        args = codeResult['args']
                        mindMapLinkLabel = jrfuncs.getDictValueOrDefault(args,'link', None)
                        # label falls back on link label?
                        label = jrfuncs.getDictValueOrDefault(args,'label', mindMapLinkLabel)
                        label = jrfuncs.getDictValueOrDefault(args,'label', None)

                        if (label is None):
                            if (False):
                                # this is for inline labeling of a lead, but using the id seems odd when we are linking to it in parens
                                oLeadLabel = behalfLead['properties']['label'] if (behalfLead['properties']['label'] != '') and (behalfLead['properties']['label'] is not None) else behalfLead['id']
                            else:
                                # this leaves it blank if there is no label
                                oLeadLabel = behalfLead['properties']['label'] if (behalfLead['properties']['label'] != '') and (behalfLead['properties']['label'] is not None) else ''
                            labelContd = '({}) contd.'.format(self.makeTextLinkToLead(behalfLead, None, False, True))
                            if (oLeadLabel==''):
                                label = labelContd
                            else:
                                label = oLeadLabel + ' ' + labelContd
                        # inline pretext
                        preText = jrfuncs.getDictValueOrDefault(codeResult,'inlinePreText', '')
                        postText = jrfuncs.getDictValueOrDefault(codeResult,'inlinePostText', '')
                        # after text
                        afterText = jrfuncs.getDictValueOrDefault(args, 'after', None)
                        #
                        forcedLeadId = ''
                        # ugly kludge to handle when one lead is executing on behalf of another
                        [newLead, addTextSuffix] = self.inlineChildBlocksToNewLead(behalfLead, headBlock, label, block, blockIndex, forcedLeadId, preText, postText, args)
                        # update this list
                        movedBlockIdList = headBlock['movedBlocks'] if ('movedBlocks' in headBlock) else []
                        # resume from this blockindex afterwards
                        linkText = self.makeTextLinkToLead(newLead, None, False, True)
                        baseText = self.getText('goto') + ' ' + linkText
                        if (afterText is not None) and (afterText!=''):
                            if (afterText[0]!='.'):
                                baseText += ', ' + afterText
                            else:
                                baseText += afterText
                        else:
                            baseText += '.'
                        #
                        textPositionStyle = self.calcTextPositionStyle(text)
                        #baseText = self.modifyTextToSuitTextPositionStyle(baseText, textPositionStyle, '', True, True, False)
                        # since this is INSIDE the inline, it should always be start of line
                        #baseText = self.modifyTextToSuitTextPositionStyle(baseText, 'linestart', '', True, True, False)

                        baseText = self.modifyTextToSuitTextPositionStyle(baseText, textPositionStyle, '* ', True, False, False)
                        baseText += addTextSuffix
                        text += baseText
                        reportText += baseText
                        # mindmap
                        self.createMindMapLinkLeadGoesToLead(block, behalfLead, newLead, context, mindMapLinkLabel, True)
                        # now we also record that this LEAD HAS an inline chaild
                        lead['properties']['hasInline'] = True
                        lead['properties']['defaultTime'] = False

                    elif (action in ['conditioned']):
                        args = codeResult['args']
                        conditionVal = args['conditionVal']
                        if (conditionVal):
                            # add in the next block
                            pass
                        else:
                            # skip the next block
                            inlineDepth = 0
                            while (blockIndex<len(childBlocks)-1):
                                blockIndex += 1
                                block = childBlocks[blockIndex]
                                if (block['type']=='code'):
                                    codeText = block['text']
                                    if (codeText.startswith('begin(')):
                                        inlineDepth += 1
                                    elif (codeText.startswith('end(')):
                                        inlineDepth -= 1
                                        #if (inlineDepth<0):
                                        # we allow an $end() without a $begin to mark end of an $inline
                                        if (inlineDepth<-1):
                                            # error
                                            raise Exception('inlineDepth<-1 in action conditioned')
                                        if (inlineDepth==0):
                                            # only when not in ntest do we allow code to break us out otherwise we migrate it
                                            break
                                    continue
                                else:
                                    break
            elif (blockType=='eof'):
                # nothing to do
                pass
            else:
                self.raiseBlockException(block, 0, 'Unknown block type "{}"'.format(blockType))

        # trim
        text = text.strip()
        reportText = reportText.strip()

        return [text, reportText]
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def calcTextPositionStyle(self, text):
        # return one of: ['linestart', 'sentence', 'midsentence']
        # linestart: next text starts a line
        # sentence: next text starts a sentence (could be after a : for example
        # midstentence: should start with lowercase
        spaceCharacters = [' ']
        sentenceCharacters = [':', '.', '@', '$', '&', '*', '%']
        linestartCararacters = ['\n', '\t']
        quoteCharacters = ['"', "'"]
        #
        if (len(text)==0):
            return 'linestart'
        pos = len(text)-1
        while (pos>=0):
            c = text[pos]
            pos -= 1
            if (c in spaceCharacters):
                continue
            if (c in quoteCharacters):
                continue
            if (c in sentenceCharacters):
                return 'sentence'
            if (c in linestartCararacters):
                return 'linestart'
            # something else
            return 'midsentence'
        # at start of line
        return 'linestart'


    def modifyTextToSuitTextPositionStyle(self, text, textPositionStyle, linestartPrefix, flagCapIfStartSentence, flagBorderIfStandalone, flagPeriodIfStandalone):
        if (len(text)==0):
            return text
        #
        c = text[0]
        if (textPositionStyle in ['linestart', 'sentence']):
            if (c.isalpha):
                text= c.upper() + text[1:]
        elif (textPositionStyle in ['linestart', 'midsentence']):
            if (c.isalpha()):
                text = c.lower() + text[1:]
        #
        if (textPositionStyle == 'linestart'):
            text = linestartPrefix + text
            if (flagPeriodIfStandalone):
                text += '.'
            if (flagBorderIfStandalone):
                # border for easier visibility
                flagBoxBorder = True
                if (flagBoxBorder):
                    text = self.getText('Template.BoxStartRed') +'\n' + text + '\n' + self.getText('Template.BoxEnd') + '\n'
                else:
                    text = '---\n' + text + '\n---\n'

        return text
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def inlineChildBlocksToNewLead(self, sourceLead, headBlock, label, block, blockIndex, forcedLeadId, preText, postText, inlineArgs):
        # create new lead
        properties = {}
        addTextSuffix = ''

        # dynamically generated lead id? or forced
        if (forcedLeadId==''):
            leadId = self.consumeUnusedLeadId()
            autoid = True
        else:
            leadId = forcedLeadId
            autoid = False
        #
        oldLead = self.findLeadById(leadId, True)
        if (oldLead is not None):
            self.raiseBlockException(block, 0, 'ERROR: inlining dynamic lead returned an id ({}) that already exists in lead table ({} at {}) for DYNAMIC lead id "{}"'.format(leadId, oldLead['sourceLabel'], oldLead['lineNumber'], id))

        # create a new head block with stats from this block
        if (label!=''):
            headerString ='{}: "{}"'.format(leadId, label)
        else:
            headerString = leadId
        newHeadBlock = self.makeBlockHeader(headerString, block['sourceLabel'], block['lineNumber'], 'lead')
        self.addHeadBlock(newHeadBlock)

        properties = newHeadBlock['properties']
        properties['renderId'] = leadId
        properties['sectionName'] = self.makeSectionNameForHeadBlock(newHeadBlock, leadId, leadId)
        properties['autoid'] = autoid
        properties['inline'] = True
        properties['inlineSourceLeadId'] = sourceLead['id']

        # copy over any additional args of import
        if ('time' in inlineArgs):
            properties['time'] = inlineArgs['time']
        if ('defaultTime' in inlineArgs):
            properties['defaultTime'] = inlineArgs['defaultTime']

        # mtype is a trail from original lead plus inline
        properties['mtype'] = sourceLead['properties']['mtype'] + '.inline'

        # ok ADD the new lead by copying values from block
        lead = {'id': self.canonicalLeadId(leadId), 'block': newHeadBlock, 'properties': properties, 'text': '', 'sourceLabel': newHeadBlock['sourceLabel'], 'lineNumber': newHeadBlock['lineNumber']}
        leadIndex = self.addLead(lead)

        # now migrate children
        # THIS *MOVES* text blocks to their new incline child block
        childBlocks = headBlock['blocks']
        inlineDepth = 0
        while (blockIndex<len(childBlocks)-1):
            blockIndex += 1
            block = childBlocks[blockIndex]
            if (block['type']=='code'):
                codeText = block['text']
                if (codeText.startswith('begin(')):
                    inlineDepth += 1
                elif (codeText.startswith('end(')):
                    inlineDepth -= 1
                    #if (inlineDepth<0):
                    # we allow an $end() without a $begin to mark end of an $inline
                    if (inlineDepth<-1):
                        # error
                        self.raiseBlockException(block, 0, 'ERROR: inlining lead too many $end() without matching $begin() lead returned an id ({}) that already exists in lead table ({} at {}) for DYNAMIC lead id "{}"'.format(leadId, oldLead['sourceLabel'], oldLead['lineNumber'], id))

                #
                if (inlineDepth<=0):
                    # only when not in ntest do we allow code to break us out otherwise we migrate it

                    #
                    properties = block['properties']
                    if ('embeddedShortCode' not in properties) or (properties['embeddedShortCode']==False):
                        # we encountered a full code block so we are done
                        break
                    # ATTN: normally $functions are kept with the text and would be CAPTURED inside an $inline() operation that captures subsequent text
                    # so if you want to STOP the inlining and start some new text you COULD put {} on a line of its own
                    # but this is a bit annoying and error prone, and a very commmon thing to want to do is have an "Otherwise..." text that separates inline blocks
                    # so here we allow the use of a $otherwise function which just inserts the text "otherwise" and specially treat this as something that STOPS the globbing of inline blocks
                    # but as a kludge we have to tell our caller than an extra linebreak is needed.

                    if (codeText.startswith('otherwise')):
                        # kludge to handle lack of linebreak
                        addTextSuffix = '\n'
                        # stop inline globbing
                        break


            # move this bock
            self.addChildBlock(newHeadBlock, block)
            # this causes problems when we need to evaluate a lead on behalf of another lead, since it loses its child contents
            # what would be nice is if we could mark that the children are MOVED and not to be evaluates
            if (True):
                # new attempt, ugly kludge
                if ('movedBlocks' not in headBlock):
                    headBlock['movedBlocks'] = [blockIndex]
                else:
                    if (blockIndex not in headBlock['movedBlocks']):
                        headBlock['movedBlocks'].append(blockIndex)
            else:
                # old way, delete
                del headBlock['blocks'][blockIndex]
                blockIndex -= 1

        # now process it (it will not be processed in main loop since it is added after)
        self.processLeadBothStages(lead, leadIndex)

        #
        if (preText != ''):
            lead['text'] = preText + '\n' + lead['text']
            lead['reportText'] = preText + '\n' + lead['reportText']
        if (postText != ''):
            lead['text'] += '\n' + postText
            lead['reportText'] += '\n' + postText

        return [lead, addTextSuffix]
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
    def isRenderTextSyntaxMarkdown(self):
        renderOptions = self.getComputedRenderOptions()
        renderTextSyntax = renderOptions['textSyntax']
        if (renderTextSyntax=='markdown'):
            return True
        return False
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def makeTextLinkToLead(self, lead, customText, flagVerboseLabel, flagPageNumber):
        properties = lead['properties']
        leadId = lead['id']
        leadLabel = properties['label']
        renderId = properties['renderId']
        linkLabel = customText if (customText is not None) else renderId
        return self.makeTextLinkToLeadId(leadId, renderId, linkLabel, flagVerboseLabel, flagPageNumber)


    def makeTextLinkToLeadId(self, leadId, renderId, linkLabel, flagVerboseLabel, flagPageNumber):
        if (renderId[0].isdigit()):
            prefix='#'
        else:
            prefix = ''
        #
        linkId = self.safeMarkdownId(renderId)
        #
        if (linkLabel is not None):
            label = linkLabel
        else:
            label = renderId
        #
        if (flagVerboseLabel) and (linkLabel!='') and (linkLabel is not None) and (linkLabel!=renderId):
            if (linkLabel is not None):
                # fixup for markdown problems
                if ('(' in linkLabel) or ('[' in linkLabel):
                    linkLabel =''
            label = renderId + ': ' + linkLabel
        #
        if (self.isRenderTextSyntaxMarkdown()):
            if (flagPageNumber):
                if (type(flagPageNumber) is str):
                    text = '{}[{}](#{}{})'.format(prefix, label, linkId, flagPageNumber)
                else:
                    text = '{}[{}](#{}+p)'.format(prefix, label, linkId)
            else:
                text = '{}[{}](#{})'.format(prefix, label, linkId)
        else:
            text = prefix + label
        #
        return text


    def makeFlexLinkToLead(self, lead, flagVerboseLabel, fallbackLabel):
        if (lead is None):
            return '[' + fallbackLabel + ']'
        if (type(lead) is str):
            lead = self.findLeadById(lead, True)
        #
        properties = lead['properties']
        leadId = lead['id']
        leadLabel = properties['label']
        renderId = properties['renderId']
        #linkLabel = renderId
        linkLabel = leadLabel
        return self.makeTextLinkToLeadId(leadId, renderId, linkLabel, flagVerboseLabel, True)



    def safeMarkdownId(self, idStr):
        idStr = idStr.replace(' ','_')
        return idStr
# ---------------------------------------------------------------------------

















# ---------------------------------------------------------------------------
    def makeInsertTagLabelText(self, tagLabel):
        if (self.isRenderTextSyntaxMarkdown()):
            text = '"**[{}]**"'.format(tagLabel)
        else:
            text = '"[{}]"'.format(tagLabel)
        return text


    def appendUseNoteToTagDict(self, tagDict, text, leadInfoText, leadInfoMText, block):
        noteDict = self.makeDualNote(text, leadInfoText, leadInfoMText, block)
        tagDict['useNotes'].append(noteDict)


    def appendUseNoteDual(self, text, leadInfoText, leadInfoMText, block):
        noteDict = self.makeDualNote(text, leadInfoText, leadInfoMText, block)
        self.notes.append(noteDict)

    def makeDualNote(self, text, leadInfoText, leadInfoMText, block):
        plainText = text + ' in {} from {} near line {}.'.format(leadInfoText, block['sourceLabel'], block['lineNumber'])
        mText = text + ' in {} from {} near line {}.'.format(leadInfoMText, block['sourceLabel'], block['lineNumber'])
        return {'text': plainText, 'mtext': mText}

    def appendWarningLead(self, text, lead):
        headBlock = lead['block']
        plainText = text + '; in lead {} from {} around line {}.'.format(lead['id'], headBlock['sourceLabel'], headBlock['lineNumber'])
        mText = text + '; in lead {} from {} around line {}.'.format(self.makeTextLinkToLead(lead, None, True, True), headBlock['sourceLabel'], headBlock['lineNumber'])
        noteDict = {'text': plainText, 'mtext': mText}
        self.warnings.append(noteDict)

    def addWarning(self, text, mtext = None):
        if (mtext is None):
            mtext = text
        self.warnings.append({'text': text, 'mtext': mtext})


    def updateMarkBoxTracker(self, boxType, amount, lead):
        if (not boxType in self.markBoxesTracker):
            self.markBoxesTracker[boxType] = {'useCount': 0, 'sumAmounts': 0, 'useNotes': []}
        self.markBoxesTracker[boxType]['useCount'] += 1
        self.markBoxesTracker[boxType]['sumAmounts'] += amount
        #
        headBlock = lead['block']
        text = 'Marking {} {} boxes'.format(amount, boxType)
        plainText = text + '; in lead {} from {} around line {}.'.format(lead['id'], headBlock['sourceLabel'], headBlock['lineNumber'])
        mText = text + '; in lead {} from {} around line {}.'.format(self.makeTextLinkToLead(lead, None, True, True), headBlock['sourceLabel'], headBlock['lineNumber'])
        noteDict = {'text': plainText, 'mtext': mText} 
        self.markBoxesTracker[boxType]['useNotes'].append(noteDict)
# ---------------------------------------------------------------------------








# ---------------------------------------------------------------------------
    def evaluateCodeBlock(self, block, sourceLead, textPositionStyle, behalfLead, evaluationOptions, context):
        # note that now behalfLead is the lead that should be credited with any debug stats, and if it is None then do not count such stats
        # this is used so that we can regenerate leads in a debug mode and similar things without effecting such stats

        # options
        optionConditionTagsAsLetters = self.getConditionTagsAsLetters()

        # initial values; the None for reportText says to copy from resultText
        codeResult = {}
        resultText = ''
        reportText = None
        behalfLeadId = behalfLead['id']
        behalfLeadProperties = behalfLead['properties']

        # parse code
        codeText = block['text']
        [funcName, args, pos] = self.parseFunctionCallAndArgs(block, codeText)


        #flagDisableDemeritHours = True
        #if (flagDisableDemeritHours):
        #    funcNameFix = {'demerithours': 'demerits', 'inlinedemerithours': 'inlinedemerit'}
        #    if (funcName in funcNameFix):
        #        funcName = funcNameFix[funcName]

        if (sourceLead==behalfLead) or (behalfLead is None):
            leadInfoText = 'lead "{}"'.format(sourceLead['id'])
            leadInfoMText = 'lead "{}"'.format(self.makeTextLinkToLead(sourceLead, None, True, True))
        else:
            leadInfoText = 'lead "{}" [copied from "{}"]'.format(behalfLead['id'], sourceLead['id'])
            leadInfoMText = 'lead "{}" [copied from "{}"]'.format(self.makeTextLinkToLead(behalfLead, None, True, True), self.makeTextLinkToLead(sourceLead, None, True, True))

        if (funcName=='empty'):
            # just placeholder
            pass
        
        elif (funcName=='options'):
            # merge in options
            jsonOptionString = args['json']
            jsonOptions = json.loads(jsonOptionString)
            # set the WORKINGDIR options
            self.jroptionsWorkingDir.mergeRawDataForKey('options', jsonOptions)

        elif (funcName in ['golead','leadid', 'returnlead', 'reflead', 'goleadback']):
            # replace with a lead's rendered id
            leadId = args['leadId']
            mindMapLinkLabel = jrfuncs.getDictValueOrDefault(args,'link',None)
            comeBack = jrfuncs.getDictValueFromTrueFalse(args,'comeback',False)
            #
            existingLead = self.findLeadById(leadId, False)
            if (existingLead is None):
                self.raiseBlockException(block, 0, 'Unknown lead reference: "{}"'.format(leadId))
            #
            if (funcName == 'golead'):
                linkText = self.makeTextLinkToLead(existingLead, None, False, True)
                baseText = self.getText('goto') + ' ' + linkText
            elif (funcName == 'goleadback'):
                linkText = self.makeTextLinkToLead(existingLead, None, False, True)
                baseText = self.getText('goto') + ' ' + linkText
                baseText += ' then return here afterwards.'
            elif (funcName == 'returnlead'):
                linkText = self.makeTextLinkToLead(existingLead, None, False, True)
                baseText = self.getText('returnto') + ' ' + linkText
            elif (funcName == 'reflead'):
                linkText = self.makeTextLinkToLead(existingLead, None, False, True)
                baseText = linkText
            else:
                linkText = self.makeTextLinkToLead(existingLead, None, False, False)
                baseText = linkText
            #
            if (comeBack):
                baseText += ' and then return'

            if (funcName=='returnlead'):
                flagBoxIt = True
                #fullLineText = self.getFullLineReturnToMd(False)
                fullLineText = ''
            else:
                flagBoxIt = True
                fullLineText =  '* '
                fullLineText = ''
            baseText = self.modifyTextToSuitTextPositionStyle(baseText, textPositionStyle, fullLineText, True, flagBoxIt, False)
            resultText = baseText
            # mindmap
            self.createMindMapLinkLeadGoesToLead(block, behalfLead, existingLead, context, mindMapLinkLabel, False)
            # default no autotime on leads that go somewhere
            behalfLeadProperties['defaultTime'] = False

        elif (funcName in ['gofake', 'gofakebak']):
            leadId = self.consumeUnusedLeadId()
            if (funcName == 'gofake'):
                linkText = self.makeTextLinkToLeadId(leadId, leadId, None, False, False)
                baseText = self.getText('goto') + ' ' + linkText
            elif (funcName == 'gofakeback'):
                linkText = self.makeTextLinkToLeadId(leadId, leadId, None, False, False)
                baseText = self.getText('goto') + ' ' + linkText
                baseText += ' then return here afterwards.'
            fullLineText =  '* '
            baseText = self.modifyTextToSuitTextPositionStyle(baseText, textPositionStyle, fullLineText, True, False, False)
            resultText = baseText


        elif (funcName in ['returninline']):
            # replace with a lead's rendered id
            leadId = jrfuncs.getDictValueOrDefault(behalfLeadProperties,'inlineSourceLeadId',None)
            if (leadId is None):
                self.raiseBlockException(block, 0, 'The $returninline() function can only be used inside an inline lead; otherwise use $returnlead()')
            mindMapLinkLabel = jrfuncs.getDictValueOrDefault(args,'link',None)
            #
            existingLead = self.findLeadById(leadId, False)
            if (existingLead is None):
                self.raiseBlockException(block, 0, 'Unknown lead reference: "{}"'.format(leadId))
            #
            linkText = self.makeTextLinkToLead(existingLead, None, False, True)
            baseText = self.getText('returnto') + ' ' + linkText
            #baseText = self.modifyTextToSuitTextPositionStyle(baseText, textPositionStyle, self.getFullLineReturnToMd(False), True, False, False)
            baseText = self.modifyTextToSuitTextPositionStyle(baseText, textPositionStyle, '', True, True, False)
            resultText = baseText
            # mindmap
            self.createMindMapLinkLeadGoesToLead(block, behalfLead, existingLead, context, mindMapLinkLabel, False)
























        # tag use
        elif (funcName=='definetag'):
            # we now require pre defining tags before use to catch errors better
            self.doDefineTag('', args, behalfLead, None, block)
            resultText = ''


        elif (funcName=='gaintag'):
            # show someone text that they get a tag
            [resultText, reportText] = self.doGainTag(args, behalfLead, block, leadInfoText, leadInfoMText, textPositionStyle)

        elif (funcName in ['hastag', 'hasalltags', 'hasanytag', 'requiretag', 'requirealltags', 'requireanytags', 'missingtag','missinganytags','missingalltags', 'mentiontags']):
            # show someone text that checking a tag
            [resultText, reportText] = self.doUseTag(args, behalfLead, funcName, codeResult, context, block, leadInfoText, leadInfoMText, textPositionStyle)


















        elif (funcName in ['beforeday', 'afterday', 'onday']):
            # kludge to make condition tag a bit nicer
            #
            day = int(args['day'])
            #
            # we make it a TAG soley for mindmap graphing and keeping track of use
            virtualTagNameMap = {'beforeday': 'preday', 'afterday': 'postday', 'onday': 'day'}
            virtualTagId = 'day.{}_{}'.format(virtualTagNameMap[funcName], day)
            #
            # look up tag, do NOT convert to letter
            tagDict = self.findTag(virtualTagId, behalfLead, block, False, False)
            if (tagDict is None):
                # day tags do not have to exist ahead of time, we create them on the fly
                tagArgs = {'id': virtualTagId, 'relation': funcName, 'day': day}
                tagDict = self.doDefineTag('', tagArgs, behalfLead, None, block)
            #
            # track use
            if (behalfLead is not None):
                tagDict['useCount'] += 1
                msg = 'Checking if it is {} {}'.format(funcName, day)
                self.appendUseNoteToTagDict(tagDict, msg, leadInfoText, leadInfoMText, block)

            # remember tags for a future mindmap
            context['lastTest'] = {'block': block, 'text': virtualTagId}

            # build output
            resultText = tagDict['testText']
            resultText = self.modifyTextToSuitTextPositionStyle(resultText, textPositionStyle, '* ', True, False, False)

            # mindmap
            self.createMindMapLinkLeadChecksDay(behalfLead, tagDict['id'])














        # ATTN: new attempt to unify as 'inline'
        #elif (funcName in ['inline', 'inlinedemerit', 'inlineback', 'inlinebacks', 'inlinehint']):
        elif (funcName in ['inline', 'inlineback', 'inlinehint']):
            # tricky one, this moves the subsqeuent text blocks into a new dynamically assigned lead and returns the lead #
            # it is handled by caller not by use
            #
            codeResult['action'] = 'inline'
            codeResult['args'] = jrfuncs.deepCopyListDict(args)
            #
            leadTagType = jrfuncs.getDictValueOrDefault(behalfLeadProperties, 'leadTagType','')
            if (leadTagType=='hint'):
                # inlines derived from hints to not take up time by default
                codeResult['args']['defaultTime'] = False
            #
            # shortcut
            if (funcName in ['inlineback', 'inlinehint']):
                optionDefaultBack = True
            else:
                optionDefaultBack = False
            #
            back = jrfuncs.getDictValueFromTrueFalse(args, 'back', optionDefaultBack)
            resume = jrfuncs.getDictValueFromTrueFalse(args, 'resume', False)
            unless = jrfuncs.getDictValueOrDefault(args, 'unless', None)
            optionDisableDemeritHours = True
            demerits = jrfuncs.getDictValueOrDefault(args, 'demerits', None)
            demeritHours = jrfuncs.getDictValueOrDefault(args, 'demeritHours', None)
            if (demeritHours is not None) and (demerits is None) and optionDisableDemeritHours:
                demerits = demeritHours
                demeritHours = None
            #

            returnLink = self.makeTextLinkToLead(behalfLead, None, False, True)
            returnText = ''
            codeResult['args']['after'] = ''
            codeResult['inlinePostText'] = ''
            simplePost = True

            if (resume):
                returnText = 'resume searching for leads'
                codeResult['args']['after'] = 'then resume searching for leads'
                codeResult['inlinePostText'] = 'resume searching for leads'
            #
            if (back):
                linkText = returnLink
                if (returnText != ''):
                    returnText += ', then '
                if (codeResult['args']['after'] != ''):
                    codeResult['args']['after'] += ', '
                returnText += self.getText('returnto') + ' ' + linkText + '.'
                codeResult['args']['after'] += 'then return here afterwards.'
                codeResult['inlinePostText'] += returnText


            if (demerits is not None):
                simplePost = False
                amount = int(args['demerits'])
                markType = 'demerit'
                #
                self.updateMarkBoxTracker(markType, amount, behalfLead)
                markText = self.calcMarkInstructions(markType, amount)
                if (unless is not None):
                    markText += ' (unless {})'.format(unless)
                #postMessage = '\n---\n' + jrfuncs.uppercaseFirstLetter(markText)
                postMessage = jrfuncs.uppercaseFirstLetter(markText)
                if (codeResult['inlinePostText']!=''):
                    postMessage += ', then '
                codeResult['inlinePostText'] = postMessage + codeResult['inlinePostText']
            elif (demeritHours is not None):
                simplePost = False
                amount = int(args['demerits'])
                markType = 'demerit'
                #
                maxDemerits = 12 / amount
                self.updateMarkBoxTracker(markType, maxDemerits, behalfLead)
                markText = self.calcMarkHourInstructions(markType, amount)
                if (unless is not None):
                    markText += ' (unless {})'.format(unless)
                #postMessage = '\n---\n' + jrfuncs.uppercaseFirstLetter(markText)
                postMessage = jrfuncs.uppercaseFirstLetter(markText)
                if (codeResult['inlinePostText']!=''):
                    postMessage += ', then '
                else:
                    postMessage += '.'
                #
                codeResult['inlinePostText'] = postMessage + codeResult['inlinePostText']

            #
            if (simplePost) and (codeResult['inlinePostText']!=''):
                #codeResult['inlinePostText'] = self.getFullLineReturnToMd(False) + 'Now '+ codeResult['inlinePostText']
                codeResult['inlinePostText'] = 'Now '+ codeResult['inlinePostText']

            # put inlinePostText in box?
            if (codeResult['inlinePostText']!='') and True:
                codeResult['inlinePostText'] = r'%boxstartred% ' + codeResult['inlinePostText'] + r' %boxend%' + '\n'



        elif (funcName=='endjump'):
            # tricky one, this moves the subsqeuent text blocks into a new dynamically assigned lead and returns the lead #
            pass

        elif (funcName=='insertlead'):
            # embed contents of a lead here
            leadId = args['leadId']
            existingLead = self.findLeadById(leadId, False)
            if (existingLead is None):
                self.raiseBlockException(block, 0, 'Unknown lead reference: "{}"'.format(leadId))
            # ATTN: this RE-EVALUATES the lead text, but it would probably be better to use pre-evaluated text; the only problem is if a lead is INSERTED before it is defined
            # we COULD throw an error in this case (bad), or instead defer evaluation until later by doing this in two passes?
            # the one thing that could get messed up by this is any debug statistics and reporting that may get confused by us calling this on behalf of another lead
            # for example, our stats of recording when a tag is used will be confused into thinking the inserted lead used a tag twice instead of THIS lea
            [resultText, reportText] = self.evaluateHeadBlockTextCode(existingLead, behalfLead, evaluationOptions)

        elif (funcName=='get'):
            # insert contents of a lead here
            varName = args['varName']
            [resultText, reportText] = self.getUserVariableTuple(varName)

        elif (funcName=='set'):
            # insert contents of a lead here
            varName = args['varName']
            varVal = args['value']
            self.setUserVariable(varName, varVal)

        elif (funcName in ['mark']):
            if (funcName == 'demerits'):
                markType = 'demerit'
            else:
                markType = args['type']
            if (markType=='demerits'):
                markType = 'demerit'
            #if (markType=='demerit'):
            #    jrprint('DEBUG STOP')

            # insert contents of a lead here
            amount = int(args['amount']) if ('amount' in args) else 1
            self.updateMarkBoxTracker(markType, amount, behalfLead)
            text = self.calcMarkInstructions(markType, amount)
            text = self.modifyTextToSuitTextPositionStyle(text, textPositionStyle, '', True, True, True)
            resultText = text


        elif (funcName in ['time','otime']):
            if (funcName == 'otime') or (self.getOptionClockMode()==True):
                amount = float(args['amount']) if ('amount' in args) else 1
                text = self.calcTimeAdvanceInstructions(amount, behalfLead, True)
                text = self.modifyTextToSuitTextPositionStyle(text, textPositionStyle, '', True, True, True)
            else:
                text = ''
            resultText = text


        elif (funcName=='backdemerit'):
            # insert contents of a lead here
            amount = int(args['demerits']) if ('demerits' in args) else 1
            gotoQuestion = args['goto'] if ('goto' in args) else ''
            leadId = args['lead'] if ('lead' in args) else None
            markType = 'demerit'
            if (leadId is None):
                goText = 'return to searching for leads'
            else:
                goLead = self.findLeadById(leadId, True)
                if (goLead is None):
                    self.raiseBlockException(block, 0, 'Unknown lead reference: "{}"'.format(leadId))
                linkText = self.makeTextLinkToLead(goLead, None, False, True)
                goText = self.getText('goto') + ' ' + linkText
            #
            if (amount>0):
                if (gotoQuestion==''):
                    text = self.calcMarkInstructions(markType, amount) + ' and {}; then resume the questionnaire after you finish.'.format(goText)
                else:
                    text = self.calcMarkInstructions(markType, amount) + ' and {}, then resume at question "{}" if you can accomplish this; if you need more help continue reading.'.format(goText, gotoQuestion)                
            else:
                text = goText
            #
            text = self.modifyTextToSuitTextPositionStyle(text, textPositionStyle, '* If not, ', False, False, False)
            self.updateMarkBoxTracker(markType, amount, behalfLead)
            resultText = text




        elif (funcName=='form'):
            # insert contents of a lead here
            typeStr = args['type']
            shortInputText = '>`____________________________`'
            if (typeStr=='short'):
                text = shortInputText
            elif (typeStr in ['mini', 'score']):
                text = '_____'
            elif (typeStr=='long'):
                text = '>`__________________________________________________`\n'
            elif (typeStr=='multiline'):
                oneLine = '>`__________________________________________________`\n'
                #text = ('    ' + oneLine ) * 6
                text = oneLine * 6
            elif (typeStr=='choice'):
                choices = args['choices'].split(';')
                text = ''
                for i,choiceVal in enumerate(choices):
                    choiceVal = choiceVal.strip()
                    text += ' {}. {}\n'.format(i,choiceVal)
            else:
                self.raiseBlockException(block, 0, 'Unknown form type: "{}"'.format(typeStr))
            resultText = text

        elif (funcName=='report'):
            # just a comment to show in the report only
            reportText = '**REPORT NOTE**: {}'.format(args['comment'])

        elif (funcName=='otherwise'):
            text = 'Otherwise'

            # remember tags for a future mindmap
            context['lastTest'] = {'block': block, 'text': 'otherwise'}

            text = self.modifyTextToSuitTextPositionStyle(text, textPositionStyle, '* ', True, False, False)
            resultText = text


        # logic funcs

        elif (funcName in ['logicmentions', 'logicimplies', 'logicsuggests']):
            target = args['target']
            # mindmap
            mindMapLinkLabel = jrfuncs.getDictValueOrDefault(args,'link',None)
            linkType = funcName
            linkType = linkType.replace('logic','')
            self.createMindMapLinkLeadToNodeGeneric(behalfLead, target, linkType, mindMapLinkLabel)
            resultText = ''

        elif (funcName in ['logicmentionedby', 'logicimpliedby', 'logicsuggestedby']):
            target = args['target']
            # mindmap
            mindMapLinkLabel = jrfuncs.getDictValueOrDefault(args,'link',None)
            linkType = funcName
            if (linkType=='logicimpliedby'):
                linkType = 'implies'
            else:
                linkType = linkType.replace('logic','')
                linkType = linkType.replace('edby','s')
            self.createMindMapLinkLeadFromNodeGeneric(behalfLead, target, linkType, mindMapLinkLabel)
            resultText = ''

        elif (funcName == 'logicidea'):
            name = args['name']
            # mindmap
            mindMapNodeLabel = jrfuncs.getDictValueOrDefault(args,'link',None)
            self.createMindMapNode(name, 'idea', mindMapNodeLabel, True, behalfLead)
            resultText = ''

        elif (funcName in ['logicab', 'logicaba']):
            a = args['a']
            b = jrfuncs.getDictValueOrDefault(args,'b',None)
            if (b is None):
                b = behalfLeadId
            # mindmap
            mindMapLinkLabel = jrfuncs.getDictValueOrDefault(args,'link',None)
            if (funcName=='logicaba'):
                self.createMindMapLinkFromBidirectionNodesNodeGeneric(a, b, mindMapLinkLabel, behalfLead)
            else:
                self.createMindMapLinkFromNodeToNodeNodeGeneric(a, b, mindMapLinkLabel, behalfLead)
            resultText = ''

        elif (funcName == 'logicirrelevant'):
            # mindmap
            self.annotateMindMapLeadNode(behalfLead, {'relevance': -1})
            resultText = ''

        elif (funcName == 'onlyonce'):
            resultText = '**NOTE:** You may only visit this lead once; you may not return here to take a different path.'

        elif (funcName == 'warning'):
            msg = args['msg']
            plainText = msg + '; in lead {} from {} around line {}.'.format(behalfLead['id'], block['sourceLabel'], block['lineNumber'])
            self.addWarning(plainText)

        elif (funcName == 'remind'):
            reminderType = args['type']
            if (reminderType=='turnpage'):
                msg = "SYNTAX ERROR IN STORYBOOK; WARNING: remind(turnpage) is no longer supported because of different layout formats; ignored."
                self.addWarning(msg)
                text = ""
            elif (reminderType=='turnPageSolo'):
                if False and (self.isLeadContextSectionStyleSolo(behalfLead, context)):
                    text = '*Turn the page...*\n'
                    text += '%pagebreak%\n'
                else:
                    text = ''
            elif (reminderType=='restBreak'):
                text = self.getText('restbreak') + '\n'
                text += '%pagebreak%\n'
            elif (reminderType in ['allyHelp', 'allyHelp3pm']):
                text = "\n%Symbol.Hand%Note: There are specific hints available for each of the the day's required items (see index).  However, if you need guidance on where to focus your efforts on any given day, you can drop by your old police precinct in the Financial District for some advice"
                if (reminderType == 'allyHelp3pm'):
                    text += ' (if you arrive between 3pm-4pm you can catch the chief on his break and get his advice for free).\n'
                else:
                    text += '.\n'

            elif (reminderType=='overtimeScore'):
                isClockModeEnabled = self.getOptionClockMode()
                if (isClockModeEnabled):
                    text = 'Subtract **3** points for every day you went into overtime'
                else:
                    text = 'Subtract **1** point for every 10 overtime you accumulated (rounded down)'
            else:
                self.raiseBlockException(block, 0, 'Unknown reminder type in $remind({})'.format(reminderType))
            resultText = text

        elif (funcName == 'autohint'):
            # this assume we are in a hint lead, and we want to 
            # autohint is used within a hint, to auto link as a last resort to the lead(s) where the hint is assigned
            hintLeadList = self.buildHintLeadListForTag(behalfLead, block)          
            if (len(hintLeadList)==0):
                resultText = 'There are no more hints available for this item.\n'
            else:
                amount = int(args['amount']) if ('amount' in args) else 3
                markType = 'demerit'
                self.updateMarkBoxTracker(markType, amount, behalfLead)
                markText = self.calcMarkInstructions(markType, amount)
                #
                if (len(hintLeadList)==1):
                    resultText = '%solo.VerticalSpace%\n---\nAs a last resort, if you cannot figure out how to find it, ' + markText + ', then visit ' + hintLeadList[0] + '\n'
                else:
                    resultText = '%solo.VerticalSpace%\n---\nAs a last resort, if you cannot figure out how to find it, ' + markText + ', then visit one more more of the following:\n'
                    for line in hintLeadList:
                        resultText += ' * ' + line + '\n'
                # for link
                context['lastTest'] = {'block': block, 'text': 'autohint'}

        elif (funcName == 'deadlineinfo'):
            # this assume we are in a hint lead, and we want to 
            [resultText, reportText] = self.doDeadlineInfo(args)


        elif (funcName == 'ifcond'):
            conditionVal = True
            condition = args['condition']
            if (condition=='clocked'):
                conditionVal = self.getOptionClockMode()
            codeResult['action'] = 'conditioned'
            codeResult['args'] = {'conditionVal': conditionVal}

        elif (funcName == 'include'):
            filePath = args['file']
            resultText = self.includeUserFile(filePath)


        elif (funcName in ['begin', 'end']):
            # these do nothing and are only used for inlining
            resultText = ''


        else:
            # debug
            dbgObj = {'funcName': funcName, 'args': args, 'pos': pos}
            text = json.dumps(dbgObj)
            resultText = text
            msg = 'Syntax error; code function not understood: {}'.format(text)
            if (True):
                self.raiseBlockException(block, 0, msg)
            else:
                self.addWarning('WARNING: ' + msg)

        # store results
        codeResult['text'] = resultText
        if (reportText is None):
            reportText = resultText
        codeResult['reportText'] = reportText

        return codeResult
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def isLeadContextSectionStyleSolo(self, lead, context):
        if ('layoutOptions' not in context):
            return True
        layoutOptions = context['layoutOptions']
        if (layoutOptions['solo']):
            return True
        return False
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def calcMarkInstructions(self, markType, amount):
        text = self.getText('Symbol.Checkbox') + 'Mark **{}** {} checkbox{} in your case log'.format(amount, markType, jrfuncs.plurals(amount,'es'))
        return text

    def calcMarkHourInstructions(self, markType, amount):
        text = self.getText('Symbol.Checkbox') + 'Mark 1 {} checkbox in your case log for every {} whole hour{} remaining before 6pm (rounded up).'.format(markType, amount, jrfuncs.plurals(amount,'s'))
        return text


    def getFullLineReturnToMd(self, flagBullet):
        if (flagBullet):
            return '\n---* '
        else:
            return '\n---\n'
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
    def calcTimeAdvanceInstructions(self, amount, lead, unitsFlag):
        if (amount==0):
            text = '%Symbol.Clock%  Time does not advance'
            return text
        isClockModeEnabled = self.getOptionClockMode()
        if (not isClockModeEnabled):
            # overtime marks
            markType = 'overtime'
            self.updateMarkBoxTracker(markType, amount, lead)
            text = self.calcMarkInstructions(markType, amount)
            return text
        # clock mode!
        if (unitsFlag):
            amountPer = self.getOptionClockTimeStep()
            amountTotal = int(amount * amountPer)
        else:
            amountTotal = int(amount)
        if (amountTotal%60==0):
            amountHours = int(amountTotal/60)
            if (amountHours>=0):
                text = self.getText('timeAdvances') + ' **{}** hour{}'.format(amountHours, jrfuncs.plurals(amountHours,'s'))
            else:
                text = '%Symbol.Clock%  ' + '**ADD** **{}** hour{} to today\'s end time'.format(amountHours*-1, jrfuncs.plurals(amountHours,'s'))        
        else:
            if (amountTotal>=0):
                text = self.getText('timeAdvances') + ' **{}** minute{}'.format(amountTotal, jrfuncs.plurals(amountTotal,'s'))
            else:
                text = '%Symbol.Clock%  ' + '**ADD** **{}** minute{} to today\'s end time'.format(amountTotal*-1, jrfuncs.plurals(amountTotal,'s'))  

        return text


    def getOptionClockMode(self):
        return self.getOptionValThrowException('clockMode')
    def getOptionClockTimeStep(self):
        return self.getOptionValThrowException('clockTimeStep')
    def getOptionClockTimeDefaultLead(self):
        return self.getOptionValThrowException('clockTimeDefaultLead')
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
    def wrapTextInRedMarkersIfEnabled(self, text):
        return self.wrapTextInRedMarkers(text)

    def wrapTextInRedMarkers(self, text):
        return '%fontColorRed%' + text + '%fontColorNormal%'
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
    # user setable variables
    def getUserVariableTuple(self, varName):
        # specials
        if (varName=='buildInfo'):
            text = 'built {} v{}'.format(jrfuncs.getNiceCurrentDateTime(), self.getVersion())
            textReport = 'DEBUG REPORT - ' + text
            return [text, textReport]
        if (varName=='name'):
            info = self.getOptionValThrowException('info')
            return jrfuncs.getDictValueOrDefault(info, 'name', None)
        if (varName=='title'):
            info = self.getOptionValThrowException('info')
            return jrfuncs.getDictValueOrDefault(info, 'title', None)
        if (varName=='version'):
            info = self.getOptionValThrowException('version')
            return jrfuncs.getDictValueOrDefault(info, 'version', None)
        if (varName=='date'):
            info = self.getOptionValThrowException('info')
            return jrfuncs.getDictValueOrDefault(info, 'date', None)
        #
        return [self.userVars[varName], None]
    
    def getUserVariable(self, varName):
        # specials
        if (varName=='buildInfo'):
            buildStr = 'built {} v{}'.format(jrfuncs.getNiceCurrentDateTime(), self.getVersion())
            return {'value':buildStr}
        return self.userVars[varName]

    def setUserVariable(self, varName, value):
        if (varName not in self.userVars):
            self.userVars[varName] = {}
        self.userVars[varName]['value'] = value


    def getText(self, varName, defaultVal=None):
        if (varName in self.userVars):
            return self.userVars[varName]
        if (varName in self.tText):
            return self.tText[varName]
        if (defaultVal is not None):
            return defaultVal
        raise Exception('Unknown text template var {}.'.format(varName))
# ---------------------------------------------------------------------------










































# ---------------------------------------------------------------------------
    def saveAllManualLeads(self):
        info = self.getOptionValThrowException('info')
        forceSourceName = jrfuncs.getDictValueOrDefault(info, 'name', '')
        if (forceSourceName==''):
            forceSourceName = jrfuncs.getDictValueOrDefault(info, 'title', '')
        if (forceSourceName==''):
            forceSourceName = 'hlp'
        else:
            forceSourceName = 'hlp_' + forceSourceName
        self.saveFictionalLeadsMadeManual(forceSourceName)

        

    def saveFictionalLeadsMadeManual(self, forceSourceLabel):
        # go through all the leads, find refereneces to fictional people and places, then output them to a file that could be dumped into MANUAL list
        hlapi = self.getHlApi()
        fictionalSourceList = ['yellow', 'places_yellow', 'people', 'places_people', 'person']
        #
        jrprint('In saveFictionalLeadsMadeManual..')
        leadFeatures = {}
        countAllLeads = 0
        for lead in self.leads:
            countAllLeads += 1
            leadProprties = lead['properties']
            #
            leadId = leadProprties['id']
            #
            [existingLeadRow, existingRowSourceKey] = hlapi.findLeadRowByLeadId(leadId)
            if (existingLeadRow is None):
                continue
            existingLeadRowProperties = existingLeadRow['properties']
            #
            source = existingLeadRowProperties['source'] if ('source' in existingLeadRowProperties) else existingRowSourceKey
            ptype = existingLeadRowProperties['ptype']

            # add only fictional to special fictional files
            if (source in fictionalSourceList):
                # add it to save list
                if (ptype not in leadFeatures):
                    leadFeatures[ptype] = []
                # copy row and change some features
                propCopy = jrfuncs.deepCopyListDict(existingLeadRow['properties'])
                propCopy['jfrozen'] = 110
                propCopy['source'] = forceSourceLabel
                geometry = existingLeadRow['geometry']
                featureRow = {"type": "Feature", "properties": propCopy, "geometry": geometry}
                #
                leadFeatures[ptype].append(featureRow)

            # add ALL rows to formap, and this time also add geometry
            fname = 'allForMapping'
            if (fname not in leadFeatures):
                leadFeatures[fname] = []
            # copy row and change some features
            propCopy = jrfuncs.deepCopyListDict(existingLeadRow['properties'])
            propCopy['jfrozen'] = 110
            propCopy['source'] = forceSourceLabel
            geometry = existingLeadRow['geometry']
            featureRow = {"type": "Feature", "properties": propCopy, "geometry": geometry}
            #
            leadFeatures[fname].append(featureRow)            

        # save
        saveDir = self.getSaveDir()
        jrfuncs.createDirIfMissing(saveDir)

        info = self.getOptionValThrowException('info')
        chapterName = self.getChapterName()

        # delete previous
        #dataSaveDir = saveDir + '/dataout'
        dataSaveDir = saveDir
        jrfuncs.createDirIfMissing(dataSaveDir)
        for ptype in fictionalSourceList:
            outFilePath = dataSaveDir + '/{}_manualAdd_{}.json'.format(chapterName, ptype)
            jrfuncs.deleteFilePathIfExists(outFilePath)
        
        encoding = self.getOptionValThrowException('storyFileEncoding')
        for ptype, features in leadFeatures.items():
            outFilePath = dataSaveDir + '/{}_manualAdd_{}.json'.format(chapterName, ptype)
            
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
            # record it was written
            self.addGeneratedFile(outFilePath)
            #
            jrprint('   wrote {} of {} leads to {}.'.format(len(features), countAllLeads, outFilePath))
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def calcLeadLabelForLeadRow(self, leadRow):
        if (leadRow is None):
            return ''
        leadRowProperties = leadRow['properties']
        leadRowLabel = leadRowProperties['dName']
        leadRowAddress = leadRowProperties['address']
        if (leadRowProperties['listype'] == 'private') or (leadRowAddress==''):
            label = leadRowLabel
        else:
            label = '{} @ {}'.format(leadRowLabel, leadRowAddress)
        return label
# ---------------------------------------------------------------------------



























# ---------------------------------------------------------------------------
# mind map helpers

    def createMindMapLead(self, lead, mapStyle):
        # mindmap
        self.createMindMapLeadNode(lead, mapStyle)


    def postProcessMindMap(self):
        # add neighborhood connects
        self.postProcessMindMapLeads()
        self.postProcessMindMapDayNodes()

    def postProcessMindMapLeads(self):
        # add neighborhood connects
        leadCount = len(self.leads)
        for i in range(0,leadCount):
            lead = self.leads[i]
            mindMapLeadNode = self.findMindMapNodeByLead(lead)
            if (mindMapLeadNode is None):
                # raise Exception('Could not find mindMapLeadNode.')
                # we no longer consider this an error, some leads may not have mindmaps
                pass
            self.postProcessMindMapLeadNode(lead, mindMapLeadNode)


    def postProcessMindMapLeadNode(self, lead, node):
        # mindmap link to neighborhood
        optionMakeNeighborHoodLinks = False

        if (optionMakeNeighborHoodLinks):
            existingLeadRow = lead['existingLeadRow']
            if (existingLeadRow is not None):
                jregion = existingLeadRow['properties']['jregion']
                jregionMindMapNode = self.createMindMapJregionNodeIfNeeded(jregion)
                # link from the lead to the neighborhood, since the lead SUGGESTS the concept of the neighborhood
                lProps = {'mtype': 'suggests'}
                link = self.mindMap.createLink(node, jregionMindMapNode, lProps)
                self.mindMap.addLink(link) 


    def postProcessMindMapDayNodes(self):
        # ATTN: we are disabling this for now because i realize we use different kinds of day tags (BEFORE_DAY1), etc.
        # so to make this work we probably want to connect first any derived day tag to link to a pure day tag, and then link between pure day tasks
        # OR we could be smart about how BEFORE_DAY3 links to AFTER_DAY1 in terms of ordering
        return

        # add links between day nodes
        regexDayNum = re.compile(r'^[^\d]*(\d*)$')
        nodes = self.mindMap.getNodes()
        for node in nodes.items:
            id = node['id']
            props = node['props']
            mtype = props['mtype']
            if (mtype != 'day'):
                continue
            matches = regexDayNum.match(id)
            if (not matches):
                raise Exception('Unexpected pattern in day node id: {}'.format(id))
            dayNumStr = matches.group(1)
            dayNum = int(dayNumStr)
            if (dayNum<2):
                # this procedure links backwards
                continue


    def annotateMindMapLeadNode(self, lead, attributes):
        # find the node
        mindMapLeadNode = self.findMindMapNodeByLead(lead)
        if (mindMapLeadNode is None):
            self.raiseBlockException(lead['block'], 0, 'Failed to find mindmap node for lead.')
        return self.mindMap.annotateNode(mindMapLeadNode, attributes)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def createMindMapLeadNode(self, lead, mapStyle):
        leadProperties = lead['properties']
        # add mindmap node
        id = lead['id']
        nprops = {}
        nprops['renderId'] = leadProperties['renderId']
        nprops['label'] = self.calcNiceLeadMindmapLabel(lead)
        nprops['mtype'] = leadProperties['mtype']
        nprops['lead'] = lead
        nprops['mapsTyle'] = mapStyle
        #
        mindMapNode = self.mindMap.createNode(id, nprops)
        self.mindMap.addNode(mindMapNode)





    def createMindMapJregionNodeIfNeeded(self, jregion):
        # create neighborhood region node if needed
        if (jregion==''):
            return None
        existingMindMapNode = self.mindMap.findNodeById(jregion)
        if (existingMindMapNode is not None):
            return existingMindMapNode
        # create it
        id = jregion
        nprops = {}
        nprops['renderId'] = jregion
        nprops['label'] = jregion
        nprops['mtype'] = 'jregion'
        #
        mindMapNode = self.mindMap.createNode(id, nprops)
        self.mindMap.addNode(mindMapNode)
        return mindMapNode


    # creating links with code

    def createMindMapLinkLeadGoesToLead(self, curBlock, fromLead, toLead, context, mindMapLinkLabel, flagInline):
        fromNode = self.findMindMapNodeByLead(fromLead)
        toNode = self.findMindMapNodeByLead(toLead)
        #
        defaultLabel = 'inlines' if (flagInline) else 'goesto'
        if (mindMapLinkLabel is not None):
            label = mindMapLinkLabel
        else:
            label = self.getRecentTestFromContextOrBlank(curBlock, context, defaultLabel)
        linkProps = {'mtype': 'goto', 'inline': flagInline, 'label': label}
        link = self.mindMap.createLink(fromNode, toNode, linkProps)
        self.mindMap.addLink(link)


    def findMindMapNodeByLead(self, lead):
        id = lead['id']
        return self.mindMap.findNodeById(id)



    def createMindMapLinkLeadProvidesTag(self, lead, tagDict):
        tagType = tagDict['tagType']
        targetId = self.calcMindMapIdForTag(tagDict)
        return self.createMindMapLinkLeadToFromNode(lead, True, targetId, 'provides', None, tagType, False)

    def createMindMapLinkLeadChecksTag(self, lead, tagDict):
        tagType = tagDict['tagType']
        targetId = self.calcMindMapIdForTag(tagDict)
        return self.createMindMapLinkLeadToFromNode(lead, False, targetId, 'informs', None, tagType, False)



    def createMindMapLinkLeadChecksDay(self, lead, targetId):
        nodeThingMtype = 'day'
        label = None
        return self.createMindMapLinkLeadToFromNode(lead, False, targetId, 'informs', label, nodeThingMtype, True)


    def createMindMapLinkLeadToNodeGeneric(self, lead, targetId, linkType, linkLabel):
        return self.createMindMapLinkLeadToFromNode(lead, True, targetId, linkType, linkLabel, None, False)

    def createMindMapLinkLeadFromNodeGeneric(self, lead, targetId, linkType, linkLabel):
        return self.createMindMapLinkLeadToFromNode(lead, False, targetId, linkType, linkLabel, None, False)


    def createMindMapLinkLeadToFromNode(self, lead, flagDirectionFromLead, targetId, linkType, linkLabel, creationMtype, flagCreate):
        # figure out the target node, whether its a LEAD, a CONCEPT, idea, etc
        leadNode = self.findMindMapNodeByLead(lead)
        targetNode = self.findCreateMapMapNodeOrIdeaByNameFlexibly(targetId, creationMtype, None, flagCreate, lead)
        linkProps = {'mtype': linkType, 'label': linkLabel}
        if (flagDirectionFromLead):
            leadA = lead
            leadB = self.findLeadById(targetId, True)
            nodeA = leadNode
            nodeB = targetNode
        else:
            leadA = self.findLeadById(targetId, True)
            leadB = lead
            nodeA = targetNode
            nodeB = leadNode
        link = self.mindMap.createLink(nodeA, nodeB, linkProps)
        #
        self.mindMap.addLink(link)


    def createMindMapLinkFromNodeToNodeNodeGeneric(self, aId, bId, label, behalfLead):
        nodeA = self.findCreateMapMapNodeOrIdeaByNameFlexibly(aId, None, None, False, behalfLead)
        nodeB = self.findCreateMapMapNodeOrIdeaByNameFlexibly(bId, None, None, False, behalfLead)
        linkProps = {'mtype': label, 'label': label}
        link = self.mindMap.createLink(nodeA, nodeB, linkProps)
        self.mindMap.addLink(link)


    def createMindMapLinkFromBidirectionNodesNodeGeneric(self, aId, bId, label, behalfLead):
        self.createMindMapLinkFromNodeToNodeNodeGeneric(aId, bId, label, behalfLead)
        self.createMindMapLinkFromNodeToNodeNodeGeneric(bId, aId, label, behalfLead)



    def createMindMapLinkBetweenTagAndHint(self, tagDict, lead):
        if (True):
            self.creatMindMapNodeForTag(tagDict, lead)
        #
        tagType = tagDict['tagType']
        targetId = self.calcMindMapIdForTag(tagDict)
        return self.createMindMapLinkLeadToFromNode(lead, False, targetId, 'hint', None, tagType, False)


    def creatMindMapNodeForTag(self, tagDict, lead):
        tagType = tagDict['tagType']
        targetId = self.calcMindMapIdForTag(tagDict)
        label = tagDict['mindMapLabel']
        # create the underlying tag node, if it does not exist
        node = self.findCreateMapMapNodeOrIdeaByNameFlexibly(targetId, tagType, label, True, lead)


    def createMindMapNode(self, idstr, creationMtype, creationLabel, flagThrowExceptionIfExists, fromLead):
        node = self.mindMap.findNodeById(idstr)
        if (node is None):
            node = self.mindMap.findNodeById(self.canonicalLeadId(idstr))
        if (node is not None):
            if (flagThrowExceptionIfExists):
                raise Exception('Trying to create mind map node by id {} but it already exists.')
            return node
        # create it
        props = {'mtype': creationMtype, 'label': creationLabel}
        node = self.mindMap.createNode(idstr, props)
        self.mindMap.addNode(node)
        return node


    def findCreateMapMapNodeOrIdeaByNameFlexibly(self, idstr, creationMtype, creationLabel, flagCreate, sourceLead):
        node = self.mindMap.findNodeById(idstr)
        if (node is None):
            node = self.mindMap.findNodeById(self.canonicalLeadId(idstr))
        if (node is None):
            node = self.mindMap.findNodeById(idstr)
        if (node is None):
            # create it (note that mtype and label may be None meaning we have a forward reference that should be filled in later)
            if (not flagCreate):
                msg = 'Error: Node "{}" not found in findCreateMapMapNodeOrIdeaByNameFlexibly.'.format(idstr)
                nodeCheck = self.mindMap.findNodeById(idstr.lower())
                if (nodeCheck is None):
                    nodeCheck = self.mindMap.findNodeById(idstr.title())
                if (nodeCheck is None):
                    nodeCheck = self.mindMap.findNodeById(idstr.upper())
                if (nodeCheck is not None):
                    msg +='. PROBABLY USE OF WRONG CASE (upper/lower).'
                jrprint(msg)
                self.raiseLeadException(sourceLead,0,msg)
            node = self.createMindMapNodeFix(idstr, creationMtype, creationLabel)
        else:
            # fixup for later referenced item that is now being defined with type and label
            # ATTN: this is problematic, because it means that we might be refering to an item that 
            self.fixMindMapNodeDetails(node, idstr, creationMtype, creationLabel)
        return node


    def calcMindMapIdForTag(self, tagDict):
        tagType = tagDict['tagType']
        tagId = tagDict['id']
        if (tagType == 'day'):
            return tagId
        return tagType + '.' + tagId
    
    def calcMindMapIdForTagLinkLabel(self, tagDict):
        tagType = tagDict['tagType']
        tagId = tagDict['id']
        if (tagType == 'day'):
            return tagId
        if (tagType in ['check','cond','trophy','decoy']):
            parts = tagId.split('.')
            return parts[len(parts)-1]
        return tagType + '.' + tagId    


    def createMindMapNodeFix(self, idstr, creationMtype, creationLabel):
        creationLabel = self.tweakMindmapLabel(creationMtype, idstr, creationLabel)
        props = {'mtype': creationMtype, 'label': creationLabel}
        node = self.mindMap.createNode(idstr, props)
        self.mindMap.addNode(node)
        return node


    def fixMindMapNodeDetails(self, node, idstr, creationMtype, creationLabel):
        if (creationMtype is not None):
            if (node['props']['mtype'] is None):
                node['props']['mtype'] = creationMtype
            elif (creationMtype != node['props']['mtype']):
                # ATTN: TODO
                #raise Exception('Mismatch in mindmap node type new={} vs old={}.'.format(creationMtype, node['props']['mtype']))
                jrprint('ERROR: Mismatch in mindmap node type new={} vs old={}.'.format(creationMtype, node['props']['mtype']))
        #
        if (creationLabel is not None):
            if (node['props']['label'] is None):
                node['props']['label'] = creationLabel

        # fixup label based on type -- new label or old
        if (creationMtype is not None):
            node['props']['label'] = self.tweakMindmapLabel(creationMtype, idstr, node['props']['label'])



    def saveMindMapStuff(self, flagCleanTemp):
        #outFilePath = self.calcOutFileDerivedName('MindMap.dot')
        #self.mindMap.renderToDotFile(outFilePath)
        renderOptions = self.getComputedRenderOptions()
        if (jrfuncs.getDictValueOrDefault(renderOptions, 'renderMindMap', False)):
            if (not self.didRender):
                self.renderLeads({'suffix':'', 'mode': 'normal'}, False)
            fname = '_MindMap.dot'
            outFilePath = self.calcOutFileDerivedName(fname)
            retv = self.mindMap.renderToDotImageFile(outFilePath)
            if (retv and flagCleanTemp):
                # delete old filename
                jrfuncs.deleteFilePathIfExists(outFilePath)
            #
            if (retv):
                self.addGeneratedFile(outFilePath + '.pdf')


    def getRecentTestFromContextOrBlank(self, curBlock, context, defaultLabel):
        # idea is to guess the last test made
        if ('lastTest' not in context):
            return defaultLabel
        lastTest = context['lastTest']
        lastTestBlock = lastTest['block']
        if (self.areBlocksCloseEnoughForTestGuess(curBlock,lastTestBlock)):
            return lastTest['text']
        # not close enough
        return defaultLabel
    

    def areBlocksCloseEnoughForTestGuess(self, block1, block2):
        if (block1 is None) or (block2 is None):
            return False
        if (block1['sourceLabel'] != block2['sourceLabel']):
            # from dif source files def not close enough
            return False
        lineNumberDelta = block1['lineNumber'] - block2['lineNumber']
        if (lineNumberDelta==0):
            return True
        if (lineNumberDelta==1):
            jrprint('Warning, in areBlocksCloseEnoughForTestGuess withe LineNumber delta of 1, but sayiung not close enough.')
        return False
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
    def calcNiceLeadMindmapLabel(self, lead):
        flagShortenContd = True
        id = lead['id']
        leadProperties = lead['properties']
        label = leadProperties['label']
        if (label is None) or (label==''):
            retLabel = id
            if (id.startswith('hint')):
                # hints always attached to something with the name, so no point repeating
                retLabel = 'hint'
            elif ('.' in retLabel):
                parts = id.split('.')
                retLabel = '\n'.join(parts)
        else:
            if ('contd.' in label):
                if (flagShortenContd):
                    retLabel = 'contd.'
                else:
                    retLabel = self.simplifyLeadLabelForMindMap(label)
            else:
                retLabel = '{}:\n{}'.format(id, self.simplifyLeadLabelForMindMap(label))
        #
        return retLabel
    


    def simplifyLeadLabelForMindMap(self, text):
        if (text is None):
            return text
        matches = re.match(r'([^\(]*)\(.*contd\.', text)
        if (matches is not None):
            text = matches[1].strip() + ' contd.'
            # TEST for inline short label
            #text = 'contd.'
        text = text.strip()
        return text



    def tweakMindmapLabel(self, mtype, idstr, label):
        #
        if (mtype == 'day'):
            if (label is None) or (label == ''):
                # blank label will default to id; lets see if we want to replace that
                candidateLabel = idstr
                dpos = candidateLabel.upper().find('DAY')
                if (dpos>0):
                    # split label with newline
                    candidateLabel = candidateLabel[0:dpos] + '\n' + candidateLabel[dpos:]
                # convert _ to spaces
                candidateLabel = candidateLabel.replace('_', ' ')
                #
                if (candidateLabel != idstr):
                    # yes use our fixed label
                    label = candidateLabel
        # return it
        return label
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
    def testMakeReferenceGuide(self):
        title = 'ResearchGuide'
        filePath = 'E:/MyDocs/Programming/Python/hlparser/src/cases/docMaking/ResearchGuide.txt'
        outFilePath = 'E:/MyDocs/Programming/Python/hlparser/src/cases/docMaking/ResearchGuide.html'
        flagConvertMarkdownToHtml = True
        self.flexiblyAddLeadNumbersToTextFile(filePath, outFilePath, flagConvertMarkdownToHtml, title)

    def flexiblyAddLeadNumbersToTextFile(self, filePath, outFilePath, flagConvertMarkdownToHtml, title):
        # load file
        jrprint('Loading file "{}" for flexiblyAddLeadNumbersToTextFile.'.format(filePath))
        encoding = 'utf-8'
        text = jrfuncs.loadTxtFromFile(filePath, True, encoding = encoding)
        # process
        [text, addCount] = self.flexiblyAddLeadNumbersToText(text, flagConvertMarkdownToHtml)
        # convert markdown to Html?
        if (flagConvertMarkdownToHtml):
            renderFormat = 'html'
            [text, extras] = self.renderMarkdown(text, renderFormat, True)
            text = '<head><link rel="stylesheet" href="{}.css"><meta charset="UTF-8"></head><body>'.format(title) + text + '</body>'
        # write it out
        jrprint('Added {} lead #s to text.'.format(addCount))
        jrprint('Saving leaded file to "{}" after flexiblyAddLeadNumbersToTextFile.'.format(outFilePath))
        jrfuncs.saveTxtToFile(outFilePath, text, encoding = encoding)


    def flexiblyAddLeadNumbersToText(self, text, flagConvertMarkdownToHtml):
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
            if (not replaced):
                matches = regexAfterColon.match(line)
                if (matches is not None):
                    text = matches.group(3)
                    [text, thisAddCount] = self.flexiblyAddLeadNumberToPotentialTextString(text, flagConvertMarkdownToHtml)
                    if (thisAddCount):
                        addCount += 1
                        replaced = True
                        line = matches.group(1)+matches.group(2)+text+matches.group(4)
            if (not replaced):
                matches = regexLineBeforeParent.match(line)
                if (matches is not None):
                    text = matches.group(2)
                    [text, thisAddCount] = self.flexiblyAddLeadNumberToPotentialTextString(text, flagConvertMarkdownToHtml)
                    if (thisAddCount):
                        addCount += 1
                        replaced = True
                        line = matches.group(1)+text+matches.group(3)
            if (not replaced):
                matches = regexInSquareBrackets.match(line)
                if (matches is not None):
                    text = matches.group(2)
                    [text, thisAddCount] = self.flexiblyAddLeadNumberToPotentialTextString(text, flagConvertMarkdownToHtml)
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


    def flexiblyAddLeadNumberToPotentialTextString(self, text, flagConvertMarkdownToHtml):
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
        hlapi = self.getHlApi()
        addCount = 0

        [guessLead, guessSource] = hlapi.findLeadRowByNameOrAddress(stext)
        if (guessLead is None):
            # fallback
            if (stext.lower().startswith('the ')):
                stext = stext[4:]
                [guessLead, guessSource] = hlapi.findLeadRowByNameOrAddress(stext)
            if (guessLead is None):
                stext = stext + ', The'
                [guessLead, guessSource] = hlapi.findLeadRowByNameOrAddress(stext)
        if (guessLead is not None):
            jrprint('Matched string of "{}" to lead {}'.format(stext, guessLead['properties']['lead']))
            addCount += 1
            if (flagConvertMarkdownToHtml):
                if (labelStr!=''):
                    #text = '**{}&nbsp;&nbsp;&nbsp;#{}** '.format(labelStr, guessLead['properties']['lead'])
                    text = '**{}:&nbsp;&nbsp;{}** '.format(guessLead['properties']['lead'], labelStr)
                else:
                    #text = '**#{}** '.format(guessLead['properties']['lead'])
                    text = '**{}** '.format(guessLead['properties']['lead'])
            else:
                if (labelStr!=''):
                    #text = '{} [#{}] '.format(labelStr, guessLead['lead'])
                    text = '{}:  {} '.format(guessLead['lead'], labelStr)
                else:
                    #text = '#{} '.format(guessLead['lead'])
                    text = '{} '.format(guessLead['lead'])
        return [text, addCount]
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def addZeroLeadWarning(self):
        text = '### WARNING !\n'
        text += 'STOP. YOU ARE READING THROUGH THIS TEXT INCORRECTLY.\n'
        text += 'Do not read through these pages like a book from begining to end.\n'
        text += 'These entries are meant to be read individually only after you look up a lead by its number.\n'
        text += 'Close this booklet now and follow rulebook instructions for looking up leads.\n'
        leadId = '0-0000'
        sourceLabel = 'internal'
        existingLead = self.findLeadById(leadId, True)
        if (existingLead is not None):
            # already exists do nothing
            return
        

        # UGLY; add the lead as a text block

        newHeadBlock = self.makeBlockHeader(leadId, sourceLabel, 0, 'lead')
        self.addHeadBlock(newHeadBlock)

        properties = newHeadBlock['properties']
        properties['renderId'] = leadId
        properties['sectionName'] = self.makeSectionNameForHeadBlock(newHeadBlock, leadId, leadId)
        properties['autoid'] = False

        # mtype is a trail from original lead plus inline
        properties['mtype'] = 'lead'
        properties['map'] = 'false'
        properties['time'] = 'none'

        # ok ADD the new lead by copying values from block
        lead = {'id': self.canonicalLeadId(leadId), 'block': newHeadBlock, 'properties': properties, 'text': '', 'sourceLabel': newHeadBlock['sourceLabel'], 'lineNumber': newHeadBlock['lineNumber']}
        self.addLead(lead)

        # add text
        curTextBlock = self.makeBlockText(sourceLabel, 0)
        curTextBlock['text'] = text
        self.addChildBlock(newHeadBlock, curTextBlock)
# ---------------------------------------------------------------------------





































































































# ---------------------------------------------------------------------------
    def includeTextFromChapterHelperFile(self, saveDir, chapterName, prefix, renderFormat):
        templateFlePath = '{}/{}_{}.{}'.format(saveDir,chapterName,prefix,renderFormat)
        templateFlePath = self.resolveTemplateVars(templateFlePath)
        templateText = jrfuncs.loadTxtFromFile(templateFlePath, False)
        if (templateText is not None):
            return templateText
        return ''
# ---------------------------------------------------------------------------








# ---------------------------------------------------------------------------
    def renderLeadsDual(self, flagCleanAfter):
        renderOptions = self.getComputedRenderOptions()
        self.renderLeads({'suffix':'', 'mode': 'normal'}, flagCleanAfter)
        if (jrfuncs.getDictValueOrDefault(renderOptions, 'renderReport', False)):
            self.renderLeads({'suffix':'Report', 'mode': 'report', 'format': 'latex'}, flagCleanAfter)
        if (jrfuncs.getDictValueOrDefault(renderOptions, 'renderSummary', False)):
            self.renderLeads({'suffix':'Summary', 'mode': 'normal', 'leadList': ['summary|cover']}, flagCleanAfter)


    def renderLeads(self, leadOutputOptions, flagCleanAfter):
        errorCounterPreRun = self.getBuildErrorCount()

        # options
        # incorporate leadOutputOptions as renderOptions overrides
        self.recalcRenderOptions(leadOutputOptions)
        # now get them
        renderOptions = self.getComputedRenderOptions()
        renderFormat = leadOutputOptions['format'] if ('format' in leadOutputOptions) else renderOptions['format']
        #
        info = self.getOptionValThrowException('info')
        chapterName = self.getChapterName()
        chapterTitle = jrfuncs.getDictValueOrDefault(info, 'title', chapterName)
        #
        optionCompileLatex = jrfuncs.getDictValueOrDefault(renderOptions, 'compileLatex', True)

        #
        leadList = jrfuncs.getDictValueOrDefault(leadOutputOptions, 'leadList', None)

        if (not renderFormat in ['html','latex']):
            raise Exception('Only html & latex lead rendering currently supported, not "{}" as set with "format" option.'.format(renderFormat))

        # where to save
        baseOutputFileName = chapterName + leadOutputOptions['suffix']

        defaultSaveDir = self.getSaveDir()
        saveDir = self.getOptionVal('chapterSaveDir', defaultSaveDir)
        saveDir = self.resolveTemplateVars(saveDir)
        jrfuncs.createDirIfMissing(saveDir)
        outFilePath = '{}/{}.{}'.format(saveDir, baseOutputFileName, renderFormat)

        # announce
        jrprint('Rendering leads in {} format to: {}'.format(renderFormat, outFilePath))

        # sort leads into sections
        self.sortLeadsIntoSections()


        # build main text
        # recursively render sections and write leads, starting from root
        context = {}
        layoutOptions = self.parseLayoutOptionsForSection(None, None, leadOutputOptions)

        
        if (leadList is None):
            # render all sections starting at root
            text = self.renderSection(None, self.rootSection, layoutOptions, renderFormat, [], leadOutputOptions, context)
        else:
            # just render specifics (like cover)
            text = ''
            for leadIdStr in leadList:
                leadIdsOr = leadIdStr.split('|')
                for leadId in leadIdsOr:
                    leadId = leadId.strip()
                    lead = self.findLeadById(leadId, True)
                    if (lead is None):
                        continue
                    section = {'cleanPage': True, 'noPageBreak': True}
                    leadText = self.renderLead(lead, renderFormat, context, layoutOptions, leadOutputOptions, section)
                    text += leadText
                    break

        # optional top stuff
        addText = ''
        if (renderFormat=='html'):
            # html start
            addText += '<html>\n'
            addText += '<head><meta http-equiv="Content-type" content="text/html">\n'
            addText += '<link rel="stylesheet" type="text/css" href="hl.css">'
            addText += '<title>{}</title>\n'.format(chapterTitle)
            addText += '<!-- BUILT {} -->\n'.format(jrfuncs.getNiceCurrentDateTime())
            addText += '</head>\n'
            addText += '<body>\n\n\n'

        # optional front section import
        addText += self.includeTextFromChapterHelperFile(saveDir, chapterName, 'top', renderFormat)

        # add top stuff to text
        text = addText + text


        # latex main and top get wrapped by mistletoe packages
        renderOptions = self.getComputedRenderOptions()
        if (renderFormat=='latex'):
            preambleLatex = self.generateMetaInfo(renderFormat)
            text = self.hlMarkdown.wrapMistletoeLatexDoc(text, context, preambleLatex, renderOptions)
        else:
            text = self.generateMetaInfo(renderFormat) + text


        # bottom stuff
        addText = ''
        # book end
        if (renderFormat=='html'):
            addText += '</div> <!-- hlbook -->\n'

        # optional bottom section import
        addText += self.includeTextFromChapterHelperFile(saveDir, chapterName, 'bottom', renderFormat)

        # doc end
        if (renderFormat=='html'):
            addText += '</body>\n'
        elif (renderFormat=='latex'):
            # close doc
            addText += '\n\\end{document}\n'

        # add it to bottom
        text += addText

        # final replacements
        text = self.textReplacementsLate(text, renderFormat)

        # delete files first
        deleteFileExtensions = []
        if (renderFormat=='latex'):
            deleteFileExtensions = ['aux', 'latex', 'pdf', 'log', 'out', 'toc']
        elif (renderFormat=='html'):
            deleteFileExtensions = ['html', 'pdf']
        self.deleteExtensionFilesIfExists(saveDir,baseOutputFileName, ['aux', 'latex', 'pdf', 'html', 'log', 'out', 'toc'])
        self.deleteSaveDirFileIfExists(saveDir, 'texput.log')

        # write out text to file for input to latex
        encoding = self.getOptionValThrowException('storyFileEncoding')
        jrfuncs.saveTxtToFile(outFilePath, text, encoding)

        # compile latex?
        if (renderFormat=='latex'):
            if (optionCompileLatex):
                self.generatePdflatex(outFilePath, True)

        # cleanup delete files afterwards? but we would like to not do this if there were errors
        errorCounterPostRun = self.getBuildErrorCount()
        erroredRendering = (errorCounterPostRun > errorCounterPreRun)
        if (not erroredRendering):
            if (flagCleanAfter != "none"):
                deleteFileExtensions = []
                if (renderFormat=='latex'):
                    deleteFileExtensions = ['aux', 'log', 'out', 'toc']
                    if (flagCleanAfter=="extra"):
                        deleteFileExtensions.append('latex')
                elif (renderFormat=='html'):
                    deleteFileExtensions = []
                self.deleteExtensionFilesIfExists(saveDir,baseOutputFileName, deleteFileExtensions)
                self.deleteSaveDirFileIfExists(saveDir, 'texput.log')
            #
            outFilePathPdf = outFilePath
            outFilePathPdf = outFilePathPdf.replace('.latex', '.pdf') 
            self.addGeneratedFile(outFilePathPdf)

        # keep track that we rendered for mindmap stuff
        self.didRender = True


    def deleteExtensionFilesIfExists(self, baseDir, baseFileName, extensionList):
        for extension in extensionList:
            filePath = '{}/{}.{}'.format(baseDir, baseFileName, extension)
            jrfuncs.deleteFilePathIfExists(filePath)

    def deleteSaveDirFileIfExists(self, baseDir, fileName):
            filePath = '{}/{}'.format(baseDir, fileName)
            jrfuncs.deleteFilePathIfExists(filePath)


    def renderSection(self, parentSection, section, parentLayoutOptions, renderFormat, skipSectionList, leadOutputOptions, context):
        text = ''

        # create a COPY of layout options which includes this sections overrides added to original parent layoutOptions
        # the layout options (used by latex/html can use css) which can be changed by the section
        layoutOptions = self.parseLayoutOptionsForSection(section, parentLayoutOptions, None)
        outMode = leadOutputOptions['mode']

        # special?
        if ('id' in section):
            sectionId = section['id']
            if (sectionId=='debugReport'):
                # special automatic debugReport section
                if (outMode == 'report'):
                    if (renderFormat=='html') or (True):
                        text += self.renderDebugReportSection(section, renderFormat, leadOutputOptions)
                else:
                    # do not show this section if not in report mode
                    return text
            elif (sectionId=='toc'):
                # table of contents
                text = self.renderTableOfContents(section, renderFormat, leadOutputOptions)
                sectionStartText = ''
                sectionEndTtext = ''
                # multi columns
                if (renderFormat=='latex'):
                    if (layoutOptions['columns']>1):
                        sectionStartText += '\\begin{multicols*}{' + str(layoutOptions['columns']) + '}\n'
                        sectionEndTtext = '\\end{multicols*}\n' + sectionEndTtext
                return sectionStartText + text + sectionEndTtext
                #text += sectionStartText + text + sectionEndTtext

        # pass layoutOptions in context
        context['layoutOptions'] = layoutOptions

        # leads
        if ('leads' in section):
            leads = section['leads']
            if (len(leads)>0):
                text += self.renderSectionLeads(leads, section, layoutOptions, renderFormat, leadOutputOptions, context)
        else:
            # blank leads just show section page?
            pass

        # recurse children
        if ('sections' in section):
            childSections = section['sections']
            for childid, child in childSections.items():
                if (childid not in skipSectionList):
                    text += self.renderSection(section, child, layoutOptions, renderFormat, skipSectionList, leadOutputOptions, context)

        return text




    def renderSectionLeads(self, leads, section, layoutOptions, renderFormat, leadOutputOptions, context):
        renderOptions = self.getComputedRenderOptions()
        renderSectionHeaders = renderOptions['sectionHeaders']
        renderLeadLabels = renderOptions['leadLabels']
        renderTextSyntax = renderOptions['textSyntax']
        outMode = leadOutputOptions['mode']

        # section header
        sectionLabel = section['label']

        # start building text
        text = ''

        # iterate leads
        for leadid, lead in leads.items():
            leadProperties = lead['properties']
            flagRender = leadProperties['render'] if ('render' in leadProperties) else True
            if (flagRender=='false') or (flagRender==False):
                continue
            
            # get rendered text for lead
            leadTextRendered = self.renderLead(lead, renderFormat, context, layoutOptions, leadOutputOptions, section)

            # add it
            text += leadTextRendered

            # loop contines for all leads


        # finished lead loop
        if (text != ''):
            # there was lead content in this section, so wrap it in section container
            # section page header (big number marking the start of leads with this prefix)
            sectionStartText = ''
            sectionEndTtext = ''
            # start of containter
            if (renderFormat=='html'):
                sectionStartText += '\n\n\n<article class="leads {}">\n'.format(layoutOptions['styleFileString'])
                sectionStartText += '<div class="leadsection {}">\n'.format(layoutOptions['styleFileString'])

            # section big text header
            if (renderSectionHeaders):
                if (sectionLabel!=''):
                    # note that the sectionLabel here is rendered in a standalone call to renderTextSyntax rather than combining into LeadText
                    markdownText = '# ' + sectionLabel + '\n'
                    [outText, extras] = self.renderTextSyntax(renderTextSyntax, markdownText, renderFormat, True)
                    sectionStartText += outText + '\n'

            # special section stop?
            breakAfter = jrfuncs.getDictValueOrDefault(section, 'stop', False)
            if (type(breakAfter) is str):
                sectionStartText += self.renderedTextSpecial('stop_'+breakAfter, renderFormat)

            # end of container
            if (renderFormat=='html'):
                sectionEndTtext += '</div> <!-- lead section -->\n\n'
                sectionEndTtext += '</article>\n\n\n\n'


            # multi columns
            if (renderFormat=='latex'):
                if (layoutOptions['columns']>1):
                    sectionStartText += '\\begin{multicols*}{' + str(layoutOptions['columns']) + '}\n'
                    sectionEndTtext = '\\end{multicols*}\n' + sectionEndTtext

            # sandwhich text
            text = sectionStartText + text + sectionEndTtext

            if (jrfuncs.getDictValueOrDefault(section,'stop', False)):
                if (renderFormat=='latex'):
                    text += '\n\\newpage\n'

        # return text
        return text
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
    def renderLead(self, lead, renderFormat, context, layoutOptions, leadOutputOptions, section):
        renderOptions = self.getComputedRenderOptions()
        renderLeadLabels = renderOptions['leadLabels']
        renderTextSyntax = renderOptions['textSyntax']
        outMode = leadOutputOptions['mode']
        cleanPageOption = jrfuncs.getDictValueOrDefault(section, 'cleanPage', False)
        #
        if (True):
            leadProperties = lead['properties']
            id = leadProperties['id']
            renderId = leadProperties['renderId']
            leadTagType = jrfuncs.getDictValueOrDefault(leadProperties, 'leadTagType','')
            inline = jrfuncs.getDictValueOrDefault(leadProperties, 'inline', False)

            # assemble entire lead text in markdown format, including some inline html
            leadText = ''

            if (False):
                # we dont check this here so caller can override it
                flagRender = leadProperties['render'] if ('render' in leadProperties) else True
                if (flagRender=='false'):
                    return leadText

            flagShowIdLabel = jrfuncs.getDictValueFromTrueFalse(leadProperties, 'idlabel', True)
            if (flagShowIdLabel):
                # lead id
                if (not jrfuncs.getDictValueOrDefault(leadProperties, 'noid', False)):
                    markdownText = '## ' + renderId + '\n'
                    leadText += markdownText
                # lead label
                leadLabel = jrfuncs.getDictValueOrDefault(leadProperties,'label', '')

                if (outMode=='report') and ('reportExtra' in leadProperties):
                    if (leadLabel is None):
                        leadLabel = 'aka ({})'.format(leadProperties['reportExtra'])
                    else:
                        leadLabel += '({})'.format(leadProperties['reportExtra'])

                if (renderLeadLabels) and (leadLabel is not None) and (leadLabel!=''):
                    markdownText = '### ' + leadLabel + '\n'
                    leadText += markdownText

            # what content are we outputting, normal text or report text (annotated for author)?
            if (outMode=='normal'):
                leadText += lead['text']
            elif (outMode=='report'):
                leadText += lead['reportText']
            else:
                raise Exception('Unknown lead output mode, should be normal|report')


            # new, add default clock time if needed
            leadTime = jrfuncs.getDictValueOrDefault(leadProperties, 'time', None)
            #
            isClockModeEnabled = self.getOptionClockMode()
            hasExplicitLeadTime = (leadTime is not None) and (leadTime != 'none')
            explicitNoLeadTime = (leadTime == 'none')
            sectionTimed = jrfuncs.getDictValueOrDefault(section, 'timed', False)
            defaultTime = jrfuncs.getDictValueOrDefault(lead['properties'], 'defaultTime', True)
            shouldDefaultTime = defaultTime and (not self.getText('timeAdvances').lower() in leadText.lower()) and (not leadTagType in ['hint','doc']) and (sectionTimed)
            #
            if (isClockModeEnabled) and (not explicitNoLeadTime) and ((hasExplicitLeadTime) or shouldDefaultTime):
                # ok no time advancing, see if we have time in this lead
                if (leadTime is None) or (leadTime=='default'):
                    leadTime = self.getOptionClockTimeDefaultLead()
                else:
                    # convert from units to minutes
                    leadTime = int(float(leadTime) * self.getOptionClockTimeStep())
                if (leadTime>=0) or True:
                    # ok add default lead time
                    text = self.calcTimeAdvanceInstructions(leadTime, lead, False)
                    text = self.modifyTextToSuitTextPositionStyle(text, 'linestart', '', True, True, True)
                    #leadText += '\n---\n' + text + '\n'
                    leadText += '\n' + text + '\n'


            # some special stuff depending on solo style
            isSoloStyle = self.isLeadContextSectionStyleSolo(lead,context)
            if (isSoloStyle):
                repTextVerticalSpace = '\n~\n~\n~\n~\n~\n~\n~\n'
                repTextTurnPage = '*Turn the page...*\n%pagebreak%\n'
            else:
                repTextVerticalSpace = ''
                repTextTurnPage = ''
            leadText = leadText.replace('%solo.VerticalSpace%\n', repTextVerticalSpace)
            leadText = leadText.replace('%solo.TurnPage%\n', repTextTurnPage)


            # ok leadtext is constructed in markdown format, now convert to our target syntax (usually html)
            [leadTextRendered, extras] = self.renderTextSyntax(renderTextSyntax, leadText, renderFormat, True)


            # post render format text
            if (renderFormat=='html'):
                leadStartHtml = '<div id="{}" class="lead">\n'.format(self.safeMarkdownId(renderId))
                leadStartHtml += '<div class="leadtext">\n'
                leadTextRendered = leadStartHtml + leadTextRendered
                leadTextRendered += '\n'
                leadTextRendered += '</div> <!-- leadtext -->\n'
                leadTextRendered += '</div> <!-- leadid -->\n'
            elif (renderFormat=='latex'):
                # end of lead visual marker
                if (not cleanPageOption):
                    if (not leadTextRendered.endswith('\n')):
                        leadTextRendered += '\n'
                    useTombstone = jrfuncs.getDictValueOrDefault(section,'tombstones', True)
                    if (useTombstone):
                        # tombstone typography adds a square block at end of line
                        leadTextRendered += self.hlMarkdown.latexTombstone()

                    

            # page breaks
            breakAfter = jrfuncs.getDictValueOrDefault(leadProperties, 'stop', False)
            if ((breakAfter) or (layoutOptions['solo'])) and (not jrfuncs.getDictValueOrDefault(section, 'noPageBreak', False)):
                if (renderFormat=='html'):
                    if (not layoutOptions['solo']):
                        # solor is handled in css for html
                        leadText += '<div class="pagebreakafter"></div>\n'
                elif (renderFormat=='latex'):
                    leadTextRendered += '\n\\newpage\n'

            if (renderFormat=='latex'):
                # merge in latex extras
                if ('latexDocClassLines' in extras) and (extras['latexDocClassLines']!=''):
                    lines = extras['latexDocClassLines'].split('\n')
                    if ('latexDocClassLines' not in context):
                        context['latexDocClassLines'] = []
                    for line in lines:
                        # add only if not already there
                        if (not line in context['latexDocClassLines']):
                            context['latexDocClassLines'].append(line)

            if (type(breakAfter) is str):
                leadTextRendered += self.renderedTextSpecial('stop_'+breakAfter, renderFormat)

        return leadTextRendered
# ---------------------------------------------------------------------------











# ---------------------------------------------------------------------------
    def renderTextSyntax(self, renderTextSyntax, text, renderFormat, flagSnippetVsWholeDocument):
        extras = {}
        #
        if (renderTextSyntax=='html'):
            # input is html, nothing to do but return it
            return [text, extras]

        if (renderTextSyntax=='plainText'):
            # plaintext needs newlines into <p>s
            text = text.strip()
            textLines = text.split('\n')
            outText = ''
            for line in textLines:
                outText += '<p>{}</p>\n'.format(line)
            return [outText, extras]

        if (renderTextSyntax=='markdown'):
            # markdown
            # using mistletoe library
            [outText, extras] = self.renderMarkdown(text, renderFormat, flagSnippetVsWholeDocument)
            return [outText, extras]

        #
        raise Exception('renderTextSyntax format not understood: {}.'.format(renderTextSyntax))
    

    def renderMarkdown(self, text, renderFormat, flagSnippetVsWholeDocument):
        return self.hlMarkdown.renderMarkdown(text, renderFormat, flagSnippetVsWholeDocument)
# ---------------------------------------------------------------------------







# ---------------------------------------------------------------------------
    def parseLayoutOptionsForSection(self, section, inParentLayoutOptions, leadOutputOptions):
        if (section is None):
            # root/default options
            layoutOptions = {'columns': 1, 'solo': False, 'styleFileString': ''}
            # override with leadOutputOptions
            if ('columns' in leadOutputOptions):
                layoutOptions['columns'] = leadOutputOptions['columns']
            if ('solo' in leadOutputOptions):
                layoutOptions['solo'] = leadOutputOptions['solo']
            # we no longer want to allow style to be specified at root
            #styleString = self.getOptionValThrowException('style')
            styleString = ''
            #
            self.parseLayoutOptionsFromStyle(styleString, layoutOptions)
            return layoutOptions
        
        # now options from section override previous parents
        layoutOptions = jrfuncs.deepCopyListDict(inParentLayoutOptions)
        sectionStyleString = jrfuncs.getDictValueOrDefault(section, 'style', '')
        self.parseLayoutOptionsFromStyle(sectionStyleString, layoutOptions)
        # return it
        return layoutOptions


    def parseLayoutOptionsFromStyle(self, styleString, layoutOptions):
        styleFileNames = styleString.split(' ')
        # walk through style files, later override earlier
        layoutStyleFileString = layoutOptions['styleFileString']
        layoutStyleFileStringList = layoutStyleFileString.split(' ')
        for styleFileName in styleFileNames:
            styleFileName = styleFileName.strip()
            if ('onecolumn' in styleFileName):
                layoutOptions['columns'] = 1
                layoutOptions['solo'] = False
            elif ('twocolumn' in styleFileName):
                layoutOptions['columns'] = 2
                layoutOptions['solo'] = False
            elif ('threecolumn' in styleFileName):
                layoutOptions['columns'] = 3
                layoutOptions['solo'] = False
            elif ('fourcolumn' in styleFileName):
                layoutOptions['columns'] = 4
                layoutOptions['solo'] = False
            elif ('solo' in styleFileName):
                layoutOptions['solo'] = True
                layoutOptions['columns'] = 1
            # add it
            if (styleFileName not in layoutStyleFileStringList):
                layoutStyleFileStringList.append(styleFileName)
        # save style string for css
        layoutOptions['styleFileString'] = ' '.join(layoutStyleFileStringList)
        return
# ---------------------------------------------------------------------------











# ---------------------------------------------------------------------------
    def renderDebugReportSection(self, section, renderFormat, leadOutputOptions):
        # ATTN: this is ugly duplicative code with renderSection -- you need to merge it in better later

        # section header
        sectionLabel = section['label']

        #style = self.getOptionValThrowException('style')
        style = ''
        sectionStyle = jrfuncs.getDictValueOrDefault(section, 'style', '')
        if (sectionStyle==''):
            sectionStyle = style
        else:
            if (style != sectionStyle):
                # add, but make sure later overrides former in css (onecolumn beats twocolumn)
                sectionStyle = style + ' ' + sectionStyle
        #
        formattedText = ''

        # start
        if (renderFormat=='html'):
            formattedText += '\n\n\n<article class="report {}">\n'.format(sectionStyle)

        # debug report core
        mtext = ''
        mtext += '\n\n# {}\n\n'.format(sectionLabel)

        # basic stats
        leadStats = self.calcLeadStats()
        #
        mtext += '## Basic Info\n\n'
        if (renderFormat=='html'):
            mtext += ' * Base options: {}.\n'.format(self.jroptions.getAllBlocks())
            mtext += ' * Working dir options: {}.\n'.format(self.jroptionsWorkingDir.getAllBlocks())
        else:
            # latex chokes on this
            mtext += ' * Base options: {}.\n'.format(self.renderEscapeForSafeMarkdown(self.jroptions.getAllBlocks()))
            mtext += ' * Working dir options: {}.\n'.format(self.renderEscapeForSafeMarkdown(self.jroptionsWorkingDir.getAllBlocks()))
        mtext += ' * Scan found {} lead files: {}.\n'.format(len(self.storyFileList), self.storyFileList)
        mtext += ' * SUMMARY STATS: ' + leadStats['summaryString'] + '.\n'
        mtext += '\n\n\n'

        # warnings
        mtext += '## {} Warnings\n\n'.format(len(self.warnings))
        if (len(self.warnings)==0):
            mtext += ' * No warnings encountered.\n'
        else:
            for index, note in enumerate(self.warnings):
                noteMtext = note['mtext']
                mtext += ' * [{}]: {}\n'.format(index+1, noteMtext)
        mtext += '\n\n\n'

        # notes
        mtext += '## {} Notes\n\n'.format(len(self.notes))
        if (len(self.notes)==0):
            mtext += ' * No notes.\n'
        else:
            for index, note in enumerate(self.notes):
                noteMtext = note['mtext']
                mtext += ' * [{}]: {}\n'.format(index+1, noteMtext)
        mtext += '\n\n\n'

        # tags
        mtext += '## {} Tags\n\n'.format(len(self.tagMap))
        if (len(self.tagMap)==0):
            mtext += ' * No tags.\n'
        else:
            for index, tagDict in self.tagMap.items():
                id = tagDict['id']
                label = tagDict['label']
                tagType = tagDict['tagType']
                if (id!=label) and (tagType!='day'):
                    labelstr = ' ({})'.format(label)
                else:
                    labelstr = ''
                mtext += ' * [{}]{} was referred to {} time{}:\n'.format(id, labelstr, tagDict['useCount'], jrfuncs.plurals(len(tagDict['useNotes']),'s'))
                for index2, note in enumerate(tagDict['useNotes']):
                    noteMtext = note['mtext']
                    mtext += '   - {}\n'.format(noteMtext)
        mtext += '\n\n\n'

        # marks
        mtext += '## Checkbox Marking\n\n'
        if (len(self.markBoxesTracker)==0):
            mtext += ' * No checkboxes marked.\n'
        else:
            for boxType, trackDict in self.markBoxesTracker.items():
                mtext += ' * [{}]: instructed {} times for max total of {}:\n'.format(boxType, trackDict['useCount'], trackDict['sumAmounts'])
                for index2, note in enumerate(trackDict['useNotes']):
                    noteMtext = note['mtext']
                    mtext += '   - {}\n'.format(noteMtext)
        mtext += '\n\n\n'


        # lead list
        mtext += '## Lead List\n\n'
        leadCount = len(self.leads)
        #jrprint('ATTN:DEBUG')
        #leadCount = 0
        for i in range(0, leadCount):
            lead = self.leads[i]
            properties = lead['properties']
            leadLabel = properties['label']
            if (properties['label'] is not None):
                leadStr = '{}:{}'.format(self.makeTextLinkToLead(lead, None, False, True), leadLabel)
            else:
                leadStr = self.makeTextLinkToLead(lead, None, False, True)
            debugInfo = jrfuncs.getDictValueOrDefault(lead, 'debugInfo', '')
            if ('!' in debugInfo):
                prefix = '!!! '
            else:
                prefix = ''
            mtext += ' * {}{} ...... {}\n'.format(prefix, leadStr, debugInfo)

        mtext += '\n\n'

        mtext += '%pagebreak%\n'

        [formattedRendered, extras] = self.renderTextSyntax('markdown', mtext, renderFormat, True)
        formattedText += formattedRendered

        # end
        if (renderFormat=='html'):
            formattedText += '</article>\n\n\n\n'

        # write it
        return formattedText
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
    def renderTableOfContents(self, section, renderFormat, leadOutputOptions):
        text = ''
        if (renderFormat == 'latex'):
            if (True):
                # to fix table of contents going to page 1; see https://stackoverflow.com/questions/27765482/latex-hyperref-link-goes-to-wrong-page-when-i-clicked-at-the-content-there
                #text += '\\addtocontents{toc}{\\protect\\contentsline {chapter}{\\protect\\numberline{}Start of Book}{}{}}\\label{sec:TableOfContents}\n'
                text += '\\cleardoublepage\\phantomsection\\addcontentsline{toc}{section}{~~Table of Contents}\n'
            else:
                #text += '\\addcontentsline{toc}{chapter}{~~Table of Contents}\n'
                pass
            text += '\n\\tableofcontents\n'
            text += '\\newpage\n'
        return text
# ---------------------------------------------------------------------------





















# ---------------------------------------------------------------------------
    def renderedTextSpecial(self, typestr, renderFormat):

        if (typestr=='stop_day'):
            markdownText = 'Stop reading this case book now, and begin searching for leads in the directories.\n\nContinue to the **End-of-shift Briefing** on the next page only when you have found all required items listed on the previous page (if any).\n'
            repText = self.wrapStopText(markdownText, renderFormat)

        elif (typestr=='stop_latenight'):
            #markdownText = 'Once you have completed the **End-of-shift Briefing** questionnaire on the previous page(s) you may proceed to the next page to select late-night leads.\n'
            markdownText = 'Once you have completed the **End-of-shift Briefing** on the previous page you may proceed to the next page to select late-night leads.\n'
            repText = self.wrapStopText(markdownText, renderFormat)

        elif (typestr=='stop_afterlate'):
            #markdownText = 'Once you have completed the **End-of-shift Briefing** questionnaire on the previous page(s) you may proceed to the next page to begin the next day of the case.\n' + self.getText('restbreak')
            markdownText = 'Once you have completed the **Late Night Leads** on the previous page you may proceed to the next page to begin the next day of the case.\n' + self.getText('restbreak')
            repText = self.wrapStopText(markdownText, renderFormat)

        elif (typestr=='stop_newday'):
            #markdownText = 'Once you have completed the **End-of-shift Briefing** questionnaire on the previous page(s) you may proceed to the next page to begin the next day of the case.\n' + self.getText('restbreak')
            markdownText = 'Once you have completed the **End-of-shift Briefing** on the previous page you may proceed to the next page to begin the next day of the case.\n' + self.getText('restbreak')
            repText = self.wrapStopText(markdownText, renderFormat)


#        elif (typestr=='stop_finalday'):
#            markdownText = 'The case is now complete, and it is time to make your final recommendations and answer questions.\n\nDo not proceed to the next page unless you are finished visiting leads and are ready to answer questions.\n'
#            repText = self.wrapStopText(markdownText, renderFormat)

        elif (typestr=='stop_questions'):
            markdownText = 'The case is nearing an end. You will have another chance to search for leads, but for now..\n\nTurn to the Conclusion section.\n'
            repText = self.wrapStopText(markdownText, renderFormat)

        elif (typestr=='stop_questionpause'):
            markdownText = 'Once you have answered all questions on the previous page(s) you may continue to the next page.\n'
            repText = self.wrapStopText(markdownText, renderFormat)
        elif (typestr=='stop_resolvepause'):
            markdownText = 'Once you have resolved the previous page you may continue to the next page.\n'
            repText = self.wrapStopText(markdownText, renderFormat)

        elif (typestr=='stop_solution'):
            markdownText = 'Once you have answered all questions on the previous page(s) you may turn the page to read the final **Epilogue**.\n'
            repText = self.wrapStopText(markdownText, renderFormat)



        elif (typestr=='stop_documents'):
            markdownText = 'Do not access the documents section unless directed to retrieve a specific document.\n'
            repText = self.wrapStopText(markdownText, renderFormat)

        elif (typestr=='stop_hints'):
            markdownText = 'Do not access the hints section except when looking up a specific hint from the table of contents.\n'
            repText = self.wrapStopText(markdownText, renderFormat)

        elif (typestr=='stop_end'):
            markdownText = 'Do not turn the page until you are ready to begin wrapping up your case.\n'
            repText = self.wrapStopText(markdownText, renderFormat)


        elif (typestr=='stop_nomore'):
            markdownText = 'Your case has ended, there is nothing more to read.\n'
            repText = self.wrapStopText(markdownText, renderFormat)

        else:
            raise Exception('ERROR IN renderedTextSpecial: {} format {}'.format(typestr, renderFormat))

        return repText


    def wrapStopText(self, markdownText, renderFormat):
        [renderedText, extras] = self.renderTextSyntax('markdown', markdownText, renderFormat, True)
        if (renderFormat=='html'):
            repText = '' #</div></div>'
            repText += '<div class="pagebreakafter"></div>\n'
            repText += '<div class="pagestop">\n'
            repText += '<h2>STOP!</h2>\n'
            repText += renderedText + '\n'
            repText += '</div>\n'
            repText += '<div class="pagebreakafter"></div>\n'
            repText += '' #'<div><div>'
        elif (renderFormat=='latex'):
            repText = ''
            repText += '\\begin{Huge}\\bfseries \\textbf{STOP!}\\par\\end{Huge}\n~\\par\n'
            repText += self.genLatexSymbolStop() + '\n'
            repText += renderedText + '\n'
            repText += self.hlMarkdown.latexTombstone()
            repText += '\\newpage%\n'
        return repText
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
    def generatePdflatex(self, filepath, quietMode):
        maxRuns = 5
        filePathAbs = os.path.abspath(filepath)
        outputDirName = os.path.dirname(filePathAbs)
        currentWorkingDir = os.getcwd()
        os.chdir(outputDirName)
        # evil
        #decodeCharSet = 'ascii'
        decodeCharSet = 'latin-1'
        #
        flagSwitchToNonQuietOnError = False
        #
        errored = False
        pdfl = None

        renderOptions = self.getComputedRenderOptions()
        extraTimesToRun = jrfuncs.getDictValueOrDefault(renderOptions, 'latexExtraRuns', 0)

        # how to run latex compile
        optionPdfLatexRunViaExePath = self.getWorkingOptionVal("pdfLatexRunViaExePath", False)
        optionPdfLatexRunViaExePath = True
        if (optionPdfLatexRunViaExePath):
            # pdf latex executable manually specified
            # THIS IS SO FUCKING EVIL BUT I AM GOING INSANE AND IN SO MUCH MENTAL TRAUMA
            renderOptions = self.getComputedRenderOptions()
            pdflatexFullPath = jrfuncs.getDictValueOrDefault(renderOptions, 'pdfLatexExeFullPath', None)
            # try this
            pdflatexFullPath = "pdflatex.exe"
        else:
            # use pdflatex to invoke
            # nothing to do up here
            pass


        wantBreak = 0
        for i in range(0,maxRuns):
            runCount = i

            if (optionPdfLatexRunViaExePath):
                jrprint('{}. Launching pdflatex ({}) on "{}".'.format(i+1, pdflatexFullPath, filePathAbs))
                proc=subprocess.Popen([pdflatexFullPath, filePathAbs], stdin=PIPE, stdout=PIPE)
                [stdout_data, stderr_data] = proc.communicate()
                if (stdout_data is not None):
                    stdOutText = stdout_data.decode(decodeCharSet)
                else:
                    stdOutText = ''
                #
                if (stderr_data is not None):
                    stdErrText = stderr_data.decode(decodeCharSet)
                else:
                    stdErrText = ''
            else:
                # use pdflatex to invoke
                # see https://pypi.org/project/pdflatex/
                # works BUT seems to fail on re-running because it uses different temp file each time? FUCKED
                try:
                    if (pdfl is None):
                        pdfl = PDFLaTeX.from_texfile(filePathAbs)
                        # see https://stackoverflow.com/questions/71991645/python-3-7-pdflatex-filenotfounderror
                        pdfl.set_interaction_mode()  # setting interaction mode to None.
                    else:
                        # multiple runs
                        pass
                    pdflArgs = {"-output-directory": outputDirName}
                    pdfl.add_args(pdflArgs)
                    pdf, log, completed_process = pdfl.create_pdf(keep_pdf_file=True, keep_log_file=True)
                    stdout_data = log
                    stdOutText = log.decode(decodeCharSet)
                    stdErrText = ''
                    stderr_data = stdErrText.encode(decodeCharSet)
                except Exception as e:
                    msg = jrfuncs.exceptionPlusSimpleTraceback(e,"running pdflatex on '{}'".format(filePathAbs))
                    jrprint(msg)
                    stdOutText = ''
                    stdErrText = msg
                    stdout_data = stdOutText.encode(decodeCharSet)
                    stderr_data = stdErrText.encode(decodeCharSet)


            # check for error
            if (b'error occurred' in stdout_data) or ((stderr_data is not None) and (b'error occurred' in stderr_data)):
                jrprint('\nERROR RUNNING PDF LATEX on {}!\n\n'.format(filepath))
                msg = 'Error encountered running latex.\n'
                if (stdErrText != ''):
                    stdErrText += '. '
                stdErrText += msg
                if (flagSwitchToNonQuietOnError):
                    quietMode = False
                errored = True
                wantBreak = True
                self.addBuildLog(stdErrText, True)

            # pdflatex may require multiple runs
            if (b'Rerun to' not in stdout_data):
                wantBreak += 1
            # kludge to run multiple times
            if (wantBreak > extraTimesToRun):
                break


        if (runCount>=maxRuns-1):
            jrprint('WARNING: MAX RUNS ENCOUNTERED ({}) -- PROBABLY AN ERROR RUNNING PDFLATEX.'.format(runCount))

  
        #jrprint('Pdflatex Result: {}'.format(retv))
        # change working directory back -- this is so fucking evil
        os.chdir(currentWorkingDir)

        if (not quietMode):
            jrprint('PDFLATEX OUTPUT:')
            jrprint(stdOutText)

        # to log regardless
        jrlog('PDFLATEX OUTPUT:')
        jrlog(stdOutText)
        

        baseFileName = os.path.basename(filepath)
        if (stderr_data is not None):
            jrprint('PDFLATEX ERR processing "{}": {}'.format(baseFileName, stdErrText))
        if (not errored):
            self.addBuildLog('Pdf generation of "{}" from Latex completed successfully.'.format(baseFileName), False)
        else:
            self.addBuildLog('\n\n----------\nError generating "{}".\nFULL LATEX OUTPUT: {}\n'.format(baseFileName, stdOutText), True)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def generateMetaInfo(self, renderFormat):
        info = self.getOptionValThrowException('info')
        #
        namestr = jrfuncs.getDictValueOrDefault(info, 'name', None)
        titlestr = jrfuncs.getDictValueOrDefault(info, 'title', None)
        authorstr = jrfuncs.getDictValueOrDefault(info, 'authors', None)
        versionstr = jrfuncs.getDictValueOrDefault(info, 'version', None)
        datestr =  jrfuncs.getDictValueOrDefault(info, 'versionDate', None)  
        #
        repText = ''
        if (renderFormat == 'html'):
            pass
        elif (renderFormat == 'latex'):
            repText += '\\author{{{}}}\n'.format(authorstr)
            repText += '\\title{{{}}}\n'.format(titlestr)
            repText += '\\subject{High and Low Game}\n'
            repText += '\\date{{{} on {}}}\n'.format(versionstr, datestr)
        return repText
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def isLeadStandardNumeric(self, leadId):
        if (len(leadId)==0):
            return False
        c = leadId[0]
        matches = re.match(r'^\d\-\d*$',leadId)
        if (matches is not None):
            return True
        return False
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
    def createCommonMindMapNodes(self):
        if (False):
            self.createMindMapNode('radio', 'idea', None, True, None)
# ---------------------------------------------------------------------------











































# ---------------------------------------------------------------------------
    def textReplacementsEarlyMarkdown(self, text, sourceLabel):
        # do some early text replacements
        intext = text
        regexSpaceBullets = re.compile(r'^\s?\. ', re.MULTILINE)
        text = regexSpaceBullets.sub(' * ', text)
        # change evil unicode double quots
        text = text.replace('“', '"')
        text = text.replace('”', '"')
        return text



    def textReplacementsLate(self, text, renderFormat):

        templatePattern = self.wrapPercentString('coverstart', renderFormat)
        if (text.find(templatePattern)>-1):
            repText = self.calcCoverInfoText(renderFormat, True)
            text = text.replace(templatePattern, repText)

        templatePattern = self.wrapPercentString('coverend', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '</div> <!-- cover page -->\n'
            elif (renderFormat=='latex'):
                repText = '\end{titlepage}\n'
            #
            text = text.replace(templatePattern, repText)

        templatePattern = self.wrapPercentString('coverinfo', renderFormat)
        if (text.find(templatePattern)>-1):
            repText = self.calcCoverInfoText(renderFormat, False)
            #
            text = text.replace(templatePattern, repText)

        templatePattern = self.wrapPercentString('pagebreak', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '<div class="pagebreakafter"></div>\n'
            elif (renderFormat=='latex'):
                repText = '\n\\newpage\n'
            #
            text = text.replace(templatePattern, repText)

        templatePattern = self.wrapPercentString('casestats', renderFormat)
        if (text.find(templatePattern)>-1):
            leadStats = self.calcLeadStats()
            repTextMarkdown = ''
            #
            if (False):
                # this info is in title normall so no need for it here
                info = self.getOptionValThrowException('info')
                versionBuild = jrfuncs.getDictValueOrDefault(info, 'version', 'n/a')
                versionDate = jrfuncs.getDictValueOrDefault(info, 'date', 'n/a')
                repTextMarkdown += '* Build: {} ({})\n'.format(versionBuild, versionDate)
            #
            repTextMarkdown += self.addOptionStatMarkdown('Difficulty')
            repTextMarkdown += self.addOptionStatMarkdown('Playtime')
            repTextMarkdown += self.addOptionStatMarkdown('Warnings')
            repTextMarkdown += '* Leads: {}.\n'.format(leadStats['count'])
            repTextMarkdown += '* Text: {:.2f}k / {:,} words.\n'.format(leadStats['textLength']/1000, leadStats['wordCount'])
            [repText, extras] = self.hlMarkdown.renderMarkdown(repTextMarkdown, renderFormat, True)
            text = text.replace(templatePattern, repText)


        templatePattern = self.wrapPercentString('fontTypewriter', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '\n<div class="fontTypewriter">\n'
            elif (renderFormat=='latex'):
                repText = '\n{\\ttfamily\n\\Large\n\\raggedright\n'
            #
            text = text.replace(templatePattern, repText)

        templatePattern = self.wrapPercentString('fontHandwriting', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '\n<div class="fontHandwriting">\n'
            elif (renderFormat=='latex'):
                repText = '\n{\\Fontskrivan\n\\LARGE\n\\raggedright\n'
            #
            text = text.replace(templatePattern, repText)

        templatePattern = self.wrapPercentString('fontOff', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '\</div> <!-- font div -->\n'
            elif (renderFormat=='latex'):
                #repText = '\n\\normalfont\n\\normalsize\n\\justifying\n'
                repText = '\n}\n'
            #
            text = text.replace(templatePattern, repText)


        templatePattern = self.wrapPercentString('alignleft', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                # dont know the right way for this
                repText = ''
            elif (renderFormat=='latex'):
                #repText = '\n\\normalfont\n\\normalsize\n\\justifying\n'
                repText = '\\raggedright\n'
            text = text.replace(templatePattern, repText)
        #
        templatePattern = self.wrapPercentString('aligncenter', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                # dont know the right way for this
                repText = ''
            elif (renderFormat=='latex'):
                #repText = '\n\\normalfont\n\\normalsize\n\\justifying\n'
                repText = '\\centering\n'
            text = text.replace(templatePattern, repText)


        templatePattern = self.wrapPercentString('Symbol.Clock', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '&#x1F551;'
            elif (renderFormat=='latex'):
                repText = '\\raisebox{-3.5pt}\\VarTaschenuhr\\hspace{0.075cm}'
            #
            text = text.replace(templatePattern, repText)
        #
        templatePattern = self.wrapPercentString('Symbol.Mark', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = 'MARKSYMBOL'
            elif (renderFormat=='latex'):
                #repText = '{\\Large \\faPencil*}\\hspace{0.1cm}'
                repText = '{\\Large \\faTags}\\hspace{0.1cm}'
            #
            text = text.replace(templatePattern, repText)
        #
        templatePattern = self.wrapPercentString('Symbol.Doc', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = 'MARKSYMBOL'
            elif (renderFormat=='latex'):
                repText = '{\\Large \\faCameraRetro}\\hspace{0.1cm}'
            #
            text = text.replace(templatePattern, repText)
        #
        templatePattern = self.wrapPercentString('Symbol.Checkbox', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = 'CHECKBOXSYMBOL'
            elif (renderFormat=='latex'):
                repText = '{\\Large \\faCheckSquare[regular]}\\hspace{0.1cm}'
            #
            text = text.replace(templatePattern, repText)

        templatePattern = self.wrapPercentString('Symbol.Exclamation', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = 'Symbol.Exclamation'
            elif (renderFormat=='latex'):
                repText = '{\\Large \\color{red} \\faExclamationCircle}\\hspace{0.1cm}'
            #
            text = text.replace(templatePattern, repText)
        #
        templatePattern = self.wrapPercentString('Symbol.Stop', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = 'Symbol.Stop'
            elif (renderFormat=='latex'):
                #repText = '{\\Large \\color{red} \\faExclamationCircle}\\hspace{0.1cm}'
                repText = self.genLatexSymbolStop()
            #
            text = text.replace(templatePattern, repText)
        #
        templatePattern = self.wrapPercentString('Symbol.Hand', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = 'Symbol.Hand'
            elif (renderFormat=='latex'):
                repText = '{\\Large \\faHandPointRight[regular]}\\hspace{0.1cm}'
            #
            text = text.replace(templatePattern, repText)
        #

        templatePattern = self.wrapPercentString('Symbol.Choice', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '[Symbol.Choice]'
            elif (renderFormat=='latex'):
                #repText = '{\\Large \\color{red} \\faTheaterMasks}\\hspace{0.1cm}'
                repText = '{\\Large \\color{red} \\faBalanceScale}\\hspace{0.1cm}'
            #
            text = text.replace(templatePattern, repText)

        templatePattern = self.wrapPercentString('Symbol.Bonus', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '[Symbol.Choice]'
            elif (renderFormat=='latex'):
                repText = '{\\Large \\color{red} \\faTheaterMasks}\\hspace{0.1cm}'
            #
            text = text.replace(templatePattern, repText)



        templatePattern = self.wrapPercentString('fontColorRed', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '<font color = "red">'
            elif (renderFormat=='latex'):
                repText = '\\color{red}'
            #
            text = text.replace(templatePattern, repText)

        templatePattern = self.wrapPercentString('fontColorNormal', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '<font color = "black">'
            elif (renderFormat=='latex'):
                repText = '\\normalcolor{}'
            #
            text = text.replace(templatePattern, repText)

        templatePattern = self.wrapPercentString('boxstart', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '<hr/>'
            elif (renderFormat=='latex'):
                #repText = '\\fbox{'
                #repText = '\\fbox{\\begin{minipage}[c]\\centering{.95\\columnwidth}'
                repText = '\\setlength{\\fboxsep}{1em} \\fbox{\\begin{minipage}[c]{.95\\columnwidth}'
                #repText = '\\setlength{\\fboxsep}{1em} \\fbox{\\begin{minipage}{\\columnwidth}'
                #repText = '\\fbox{\\begin{minipage}[c]{\\columnwidth}'
            #
            text = text.replace(templatePattern, repText)
        #
        templatePattern = self.wrapPercentString('boxstartred', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '<hr/>'
            elif (renderFormat=='latex'):
                repText = '\\setlength{\\fboxsep}{1em} \\fbox{\\begin{minipage}[c]{.95\\columnwidth}\\color{red}'
            #
            text = text.replace(templatePattern, repText)
        #
        templatePattern = self.wrapPercentString('boxend', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '<hr/>'
            elif (renderFormat=='latex'):
                #repText = '}'
                repText = '\\end{minipage}}\\normalcolor{}'
            #
            text = text.replace(templatePattern, repText)



        #
        templatePattern = self.wrapPercentString('radiostart', renderFormat)+'\n\n'
        if (text.find(templatePattern)>-1):
            # little cleanup first to remove newlines at start for better symbol
            # THIS IS SO FUCKING STUPID AND EVIL
            if (False):
                text = text.replace('\%radiostart\\%\n', '\%radiostart\\%')
                text = text.replace('\%radiostart\\%\n', '\%radiostart\\%')
            if (renderFormat=='html'):
                repText = '<hr/>'
            elif (renderFormat=='latex'):
                #repText = '\\setlength{\\fboxsep}{2em} \\shadowbox{\\begin{minipage}[c]{.80\\columnwidth}\\color{blue}\\begin{quoting}'
                #repText = '\\setlength{\\fboxsep}{2em} \\begin{center}\\shadowbox{\\begin{minipage}[c]{.80\\columnwidth}\\bfseries\\itshape'
                repText = '\\setlength{\\fboxsep}{2em} \\begin{center}\\shadowbox{\\begin{minipage}[c]{.80\\columnwidth}\\ttfamily\\bfseries\\itshape'
                #repText += '{\\Large \\faCommentDots[regular]}\\hspace{0.1cm} '
                #repText += '{\\Large \\faBroadcastTower}\\hspace{0.1cm} '
                repText += '{\\Large \\faVolumeUp}\\hspace{0.1cm} '
                #repText += '{\\Large \\faRss}\\hspace{0.1cm}'
                repText += '"'
            text = text.replace(templatePattern, repText)
        #
        templatePattern = '\n\n' + self.wrapPercentString('radioend', renderFormat)
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '<hr/>'
            elif (renderFormat=='latex'):
                #repText = '}'
                #repText = '\\end{quoting}\\end{minipage}}\\normalcolor{}'
                repText = ''
                repText += '"'
                repText += '\\end{minipage}}\\end{center}'
            #
            text = text.replace(templatePattern, repText)



        #
        templatePattern = '\n\n' + self.wrapPercentString('Separator.Final', renderFormat)+'\n'
        if (text.find(templatePattern)>-1):
            if (renderFormat=='html'):
                repText = '<hr/>'
            elif (renderFormat=='latex'):
                repText = '\n\\begin{center}{\\pgfornament[anchor=center,ydelta=0pt,width=2cm]{80}}\\end{center}%\n'
            #
            text = text.replace(templatePattern, repText)




        # eliminate double line separators
        text = text.replace('\n\hrulefill\n\hrulefill\n','\n\hrulefill\n')
        text = text.replace('\n\hrulefill\n\n\hrulefill\n','\n\hrulefill\n')
        text = text.replace('\n<hr/>\n</hr>\n','\n</hr>\n')
        text = text.replace('\n---\n---\n','\n---\n')

        #
        return text


    def genLatexSymbolStop(self):
        return '{\\Huge \\color{red} \\faExclamationTriangle}\\hspace{0.1cm}'


    def addOptionStatMarkdown(self, optionVar):
        info = self.getOptionValThrowException('info')
        optionVal = jrfuncs.getDictValueOrDefault(info, optionVar, None)
        if (optionVal is None):
            optionVal = jrfuncs.getDictValueOrDefault(info, optionVar.lower(), None)
        if (optionVal is None):
            return ''
        retv = '* {}: {}.\n'.format(optionVar, optionVal)
        return retv


    def wrapPercentString(self, text, renderFormat):
        if (renderFormat=='html'):
            return '%'+text+'%'
        elif (renderFormat=='latex'):
            return '\%' + text + '\%'


    def calcCoverInfoText(self, renderFormat, flagBreakPage):
        info = self.getOptionValThrowException('info')
        #
        namestr = jrfuncs.getDictValueOrDefault(info, 'name', None)
        titlestr = jrfuncs.getDictValueOrDefault(info, 'title', None)
        subtitlestr = jrfuncs.getDictValueOrDefault(info, 'subtitle', None)
        authorstr = jrfuncs.getDictValueOrDefault(info, 'authors', None)
        versionstr = jrfuncs.getDictValueOrDefault(info, 'version', None)
        datestr =  jrfuncs.getDictValueOrDefault(info, 'versionDate', None)
        repText = ''
        if (renderFormat=='html'):
            if (flagBreakPage):
                repText += '<div class="coverpage">'
            repText += '<div class ="coverTitle">{}</div>\n<div class="coverAuthor">by {}</div>\n<div class="coverDateVersion"><span class="coverVersion">{}</span> - <span class="coverDate">{}</span></div>\n'.format(titlestr, authorstr, versionstr, datestr)
        elif (renderFormat=='latex'):
            if (flagBreakPage):
                repText += '\\begin{titlepage}\n'
            #reptext += '\\cleardoublepage\\phantomsection\\addcontentsline{toc}{section}{~~Cover Page}\n'
            # add cover page to table of contents
            repText += '\\addcontentsline{toc}{section}{~~Cover Page}\n'
            #
            repText += '\\centering\n\\vspace*{-0.25in} \\begin{Huge}\\bfseries \\textbf{' + self.hlMarkdown.escapeLatex(titlestr) + '}\n\\par\\end{Huge}\n'
            if (subtitlestr is not None) and (subtitlestr!=''):
                repText += '\\centering\n\\vspace*{0in} \\begin{LARGE}\\bfseries \\textbf{' + self.hlMarkdown.escapeLatex(subtitlestr) + '}\n\\par\\end{LARGE}\n'
            repText += '\\vspace{0.0in}\\begin{Large}\\bfseries by ' + self.hlMarkdown.escapeLatex(authorstr) + '\n\\par\\end{Large}\n'
            repText += '\\vspace{0.0in} ' + self.hlMarkdown.escapeLatex(versionstr) + ' - ' + self.hlMarkdown.escapeLatex(datestr) + '\\par\\vspace{0.5in}\\par\n'
            # repText += '\\flushleft\n'
        #
        return repText
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
    def renderEscapeForSafeMarkdown(self, text):
        # escape text for latext markdown
        return self.hlMarkdown.escapeForSafeMarkdown(text)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def addReportLogicLinks(self):
        # add debug info to report texts for leads based on any logic links between leads
        leadAddedDebugList = []
        nodes = self.mindMap.getNodes()
        for nodeName, node in nodes.items():
            id = node['id']
            nodeProps = node['props']
            mtype = nodeProps['mtype']
            if ('to' not in node):
                continue
            linksTo = node['to']
            for link in linksTo:
                toNode = link['to']
                toNodeProps = toNode['props']
                # ok we have FROM, TO, and LINK
                #fromLeadId = nodeProps['lead'] if ('lead' in nodeProps) else None
                #toLeadId = toNodeProps['lead'] if ('lead' in toNodeProps) else None
                fromLead = nodeProps['lead'] if ('lead') in nodeProps else None
                toLead = toNodeProps['lead'] if ('lead') in toNodeProps else None
                fromLink = self.makeFlexLinkToLead(fromLead, True, node['id'])
                toLink = self.makeFlexLinkToLead(toLead, True, toNode['id'])
                #
                #
                linkProps = link['props']
                mtype = linkProps['mtype']
                # some links we dont bother with
                if (mtype in ['goto','provides']):
                    continue
                #
                if (linkProps['label'] is None) or (linkProps['mtype'] == linkProps['label']):
                    linkLabel = linkProps['mtype']
                else:
                    linkLabel = linkProps['mtype'] + '.' + linkProps['label']
                # prettify
                if (linkLabel=='informs'):
                    linkLabel = 'is checked by'
                # now add annotation to BOTH nodes
                nodeReportTextFrom = '\n**DEBUG:** This lead "{}" {}\n'.format(linkLabel, toLink)
                nodeReportTextTo = '\n**DEBUG:** {} "{}" this lead.\n'.format(fromLink, linkLabel)
                if (fromLead is not None):
                    if (fromLead['reportText'] is None):
                        fromLead['reportText'] = ''
                    leadId = fromLead['id']
                    if (leadId not in leadAddedDebugList):
                        leadAddedDebugList.append(leadId)
                        fromLead['reportText'] += '\n---\n'
                    fromLead['reportText'] += nodeReportTextFrom
                if (toLead is not None):
                    if (toLead['reportText'] is None):
                        toLead['reportText'] = ''
                    leadId = toLead['id']
                    if (leadId not in leadAddedDebugList):
                        leadAddedDebugList.append(leadId)
                        toLead['reportText'] += '\n---\n'
                    toLead['reportText'] += nodeReportTextTo
        pass
# ---------------------------------------------------------------------------

































# ---------------------------------------------------------------------------
    def databaseDebugLead(self, lead):
        # this function is designed to identify problems where a lead # is used but it doesnt match the directory database
        hlapi = self.getHlApi()
        hlapiPrev = self.getHlApiPrev()
        #
        manualLeadIgnoreList = ['0-0000', '9-9999']
        leadProprties = lead['properties']
        #
        leadId = lead['id']
        label = leadProprties['label'] if ('label' in leadProprties) else None
        autoid = leadProprties['autoid'] if ('autoid' in leadProprties) else False
        map = leadProprties['map'] if ('map' in leadProprties) else False
        #
        # lookup database row in main dbs
        [existingLeadRow, existingRowSourceKey] = hlapi.findLeadRowByLeadId(leadId)
        if (existingLeadRow is not None):
            existingLeadRowLabel = existingLeadRow['properties']['dName']
            existingLeadRowAddress = existingLeadRow['properties']['address']
            existingLeadRowSmartLabel = self.calcLeadLabelForLeadRow(existingLeadRow)
            if (not self.isDbValNoneOrBlank(existingLeadRow['properties']['apt'])):
                existingLeadRowAddress += ' apt.'+existingLeadRow['properties']['apt']
        else:
            existingLeadRowLabel = ''
            existingLeadRowAddress = ''
            existingLeadRowSmartLabel = ''
        
        # lookup in PREV db, if a prev DB is set; this is to help us migrate from one directory db to a new one
        existingLeadRowLabelPrev = ''
        existingLeadRowAddressPrev = ''
        existingLeadRowSmartLabelPrev = ''
        if (hlapiPrev is not None):
            [existingLeadRowPrev, existingRowSourceKeyPrev] = hlapiPrev.findLeadRowByLeadId(leadId)
            if (existingLeadRowPrev is not None):
                existingLeadRowLabelPrev = existingLeadRowPrev['properties']['dName']
                existingLeadRowAddressPrev = existingLeadRowPrev['properties']['address']
                if (not self.isDbValNoneOrBlank(existingLeadRowPrev['properties']['apt'])):
                    existingLeadRowAddressPrev += ' apt.'+existingLeadRowPrev['properties']['apt']
                existingLeadRowSmartLabelPrev = self.calcLeadLabelForLeadRow(existingLeadRowPrev)
            else:
                if (False):
                    if (not autoid) and (existingLeadRowLabel!=''):
                        existingLeadRowLabelPrev = '[MISSING]'
                        existingLeadRowAddressPrev = '[MISSING]'
                        existingLeadRowSmartLabelPrev = '[MISSING]'


        # label for display
        if (label is None) or (label == '.') or (label=="blank"):
            # shorthand for make blank
            label = 'n/a'

        # we will build debug messages here
        debugMsgs = []

        # first check for high-level errors
        needsCompare = False
        if (autoid):
            # this should NOT match anything, because autoid means use an UNUSED lead #
            if (existingLeadRow is not None):
                msg = '! An autoid lead should not match an existing lead in the database, but it does match: {} at {} from {}'.format(existingLeadRow['properties']['dName'], existingLeadRow['properties']['address'], existingRowSourceKey)
                self.appendWarningLead(msg, lead)
                debugMsgs.append(msg)
                needsCompare = True
        else:
            # not an autoid so we expect to match it
            if (not self.isLeadStandardNumeric(leadId)) or (leadId in manualLeadIgnoreList):
                # it doesnt start with a number so we dont expect it to match
                if (existingLeadRow is not None):
                    msg = '! WARNING: A lead starting with a letter should not match an existing lead in the database, but it does: {} at {} from {}.'.format(existingLeadRow['properties']['dName'], existingLeadRow['properties']['address'], existingRowSourceKey)
                    self.appendWarningLead(msg, lead)
                    debugMsgs.append(msg)
                    needsCompare = True
            else:
                # a number lead should match, the fact that it doesnt is a problem
                if (existingLeadRow is None):
                    msg = '! WARNING: A standard numbered lead # ({}) is expected to match an entry in the database, but it does not.'.format(leadId)
                    self.appendWarningLead(msg, lead)
                    debugMsgs.append(msg)
                    needsCompare = True


        # and now try to compare names and addresses to find mismatches
        if (needsCompare) or (existingLeadRow is not None):
            msg = ''
            # if an error triggered a compare OR if we found an existing row
            if (existingLeadRow is None):
                # could not find an existing one, let's try to guess
                if (label==''):
                    labelCompareStr = ''
                else:
                    labelCompareStr = '[{}]'.format(label)
                if (needsCompare):
                    searchFor = label if (label!='') else leadId
                    [guessLead, guessSource] = hlapi.findLeadRowByNameOrAddress(searchFor)
                    if (guessLead is None):
                        # let's try a SLOWER metric search
                        [guessLead, guessSource, dist] = hlapi.findLeadRowSimilarByNameOrAddress(searchFor)
                    else:
                        dist = 0
                    #
                    if (guessLead is None):
                        msg = '! Could not find a similar lead in primary database.'
                    else:
                        msg = '! Primary database search found similar entry: #{} "{}" @ [{}] from {}? (dist {:.2f})].'.format(guessLead['properties']['lead'], guessLead['properties']['dName'], guessLead['properties']['address'], guessSource, dist)
            elif (label == existingLeadRowLabel):
                # found a match
                msg = 'Primary database match, identical label, address = [{}]'.format(existingLeadRowAddress)
            elif (jrfuncs.semiMatchStringsNoPunctuation(label, existingLeadRowLabel)):
                msg = 'Primary database label semi-match vs "{}" at db address [{}].'.format(existingLeadRowLabel, existingLeadRowAddress)
            else:
                msg = '! Primary database hit but possibly conflicting label vs "{}" at db address [{}].'.format(existingLeadRowLabel, existingLeadRowAddress)
            #
            if (msg!=''):
                debugMsgs.append(msg)
                #self.appendWarningLead(msg, lead)
        
        # new compare with old PREVIOUS database
        if (existingLeadRowLabelPrev != ''):
            if (existingLeadRowLabelPrev != existingLeadRowLabel):
                if (autoid):
                    msg = '* Previous ver. db hit on an autoid lead: "{}" @ [{}].'.format(existingLeadRowLabelPrev, existingLeadRowAddressPrev)   
                elif (label == existingLeadRowLabelPrev):
                    msg = ' Previous ver. db match, identical label, address = [{}].'.format(existingLeadRowAddressPrev)
                elif (jrfuncs.semiMatchStringsNoPunctuation(label, existingLeadRowLabelPrev)):
                    msg = '* Previous ver. db semi-match: "{}" @ [{}].'.format(existingLeadRowLabelPrev, existingLeadRowAddressPrev)
                else:
                    msg = '! Previous ver. db hit differs: "{}" @ [{}].'.format(existingLeadRowLabelPrev, existingLeadRowAddressPrev)                                        
                debugMsgs.append(msg)
        else:
            # no hit in previous
            if (hlapiPrev is not None):
                # we have a prev db
                if (existingLeadRow is not None):
                    # we matched in primary db, so throw up a warning
                    msg = '! Previous ver. db did not have a hit.'                                        
                    debugMsgs.append(msg)        

        # display
        if (len(debugMsgs)>0):
            jrprint('')
        debugLine = 'Debugging {:.<30}... {}     | from {} at line #{}'.format(leadId, label, lead['sourceLabel'], lead['lineNumber'])
        jrprint(debugLine)
        for msg in debugMsgs:
            jrprint(' {}'.format(msg))
        if (len(debugMsgs)>0):
            jrprint('')

        # store info
        debugInfo = '; '.join(debugMsgs)
        lead['debugInfo'] = debugInfo
        # lets store the existing lead row in hl data
        lead['existingLeadRow'] = existingLeadRow


    def isDbValNoneOrBlank(self, val):
        if (val is None):
            return True
        if (val==''):
            return True
        if (str(val)=='nan'):
            return True
        return False
# ---------------------------------------------------------------------------



















































# ---------------------------------------------------------------------------
    def doGainTag(self, args, lead, block, leadInfoText, leadInfoMText, textPositionStyle):
        # we now use generic tags that can be used for DOCUMENTS or CONDITIONS or other things
        tagId = args['id']
        isDefine = jrfuncs.getDictValueFromTrueFalse(args,'define',False)
        tagDict = self.findTag(tagId, lead, block, True, isDefine)

        # track use
        if (lead is not None):
            tagDict['useCount'] += 1
            msg = 'Gained {}'.format(tagDict['tagType'])
            self.appendUseNoteToTagDict(tagDict, msg, leadInfoText, leadInfoMText, block)
            tagDict['gainLeads'].append(lead)

        tagType = tagDict['tagType']
        if (tagType == 'task') and (self.getOptionDisableTaskTags()):
            return ['', '']
        else:
            # use it
            resultText = tagDict['gainTextPlayer']
            reportText = tagDict['gainTextReport']
            #
            if (tagDict['tagType']=='doc'):
                symbolName = 'Symbol.Doc'
            else:
                symbolName = 'Symbol.Mark'
            #
            resultText = self.getText(symbolName) + resultText
            reportText = self.getText(symbolName) + reportText
            #         
            resultText = self.modifyTextToSuitTextPositionStyle(resultText, textPositionStyle, '', True, True, False)
            reportText = self.modifyTextToSuitTextPositionStyle(reportText, textPositionStyle, '', True, True, False)

            # mindmap
            self.createMindMapLinkLeadProvidesTag(lead, tagDict)
            return [resultText, reportText]
# ---------------------------------------------------------------------------








# ---------------------------------------------------------------------------
    def doUseTag(self, args, behalfLead, funcName, codeResult, context, block, leadInfoText, leadInfoMText, textPositionStyle):
        # this is an AND for all tags
        tagIdAll = args['id']
        tagIds = tagIdAll.split(',')
        displayTagIds = []
        tagLabels = []
        tagLabelsReport = []
        conditionTagsAsLetters = self.getConditionTagsAsLetters()

        if (funcName in ['mentiontags']):
            addGainedText = False
        else:
            addGainedText = True

        for tagId in tagIds:
            tagId = tagId.strip()
            displayTagId = tagId
            if (displayTagId.startswith('check.') or displayTagId.startswith('cond.')):
                parts = tagId.split('.')
                displayTagId = parts[len(parts)-1]
            displayTagIds.append(displayTagId)
            #
            tagDict = self.findTag(tagId, behalfLead, block, True, False)
            # track use
            if (behalfLead is not None):
                tagDict['useCount'] += 1
                msg = 'Checking user {}'.format(funcName)
                self.appendUseNoteToTagDict(tagDict, msg, leadInfoText, leadInfoMText, block)
            # tagLabelTyped
            if (addGainedText):
                tagLabelTyped = tagDict['labelTyped']
                tagLabelTypedReport = tagDict['labelFullReport']
            else:
                tagLabelTyped = tagDict['labelExtended']
                tagLabelTypedReport = tagDict['labelTypedReport']
            #
            tagLabels.append(tagLabelTyped)
            tagLabelsReport.append(tagLabelTypedReport)
            # mindmap
            self.createMindMapLinkLeadChecksTag(behalfLead, tagDict)
        #
        if (funcName in ['hasanytag', 'requireanytags','missinganytags']):
            comboWord = 'or'
        else:
            comboWord = 'and'
        numTags = len(tagIds)
        tagLabelsStr = jrfuncs.makeNiceCommaAndOrList(tagLabels, comboWord)
        tagLabelsStrForDebug = jrfuncs.makeNiceCommaAndOrList(tagLabelsReport, comboWord)

        # remember tags for a future mindmap
        context['lastTest'] = {'block': block}
        if (numTags==1):
            context['lastTest']['text'] = displayTagIds[0]
        else:
            context['lastTest']['text'] = '{}({})'.format(comboWord, ','.join(displayTagIds))

        #
        if (funcName in ['requiretag', 'requirealltags', 'requireanytags']):
            # require tells people to go away unless they have something
            markType = jrfuncs.getDictValueOrDefault(args,'type',None)
            amount = int(args['amount']) if ('amount' in args) else 1
            if (markType is None):
                extraInstructions = ''
            else:
                self.updateMarkBoxTracker(markType, amount, behalfLead)
                extraInstructions = ' In addition, {} now.'.format(self.calcMarkInstructions(markType, amount))
            baseText = 'If you have *NOT* {},  stop reading now, and return here when you have.' + extraInstructions + '\n * Otherwise, '
            codeResult['action'] = 'inline'
            codeResult['args'] = {}
            if ('time' in args):
                codeResult['args']['time'] = args['time']
            #
        elif (funcName in ['missingtag','missinganytags','missingalltags']):
            baseText = 'If you have *NOT* {}'                
        elif (funcName in ['mentiontags']):
            baseText = '{}'   
        else:
            baseText = 'If you have {}'
        #
        baseText = self.modifyTextToSuitTextPositionStyle(baseText, textPositionStyle, '* ', True, False, False)
        resultText = baseText.format(tagLabelsStr)
        reportText = baseText.format(tagLabelsStrForDebug)

        return [resultText, reportText]
# ---------------------------------------------------------------------------









# ---------------------------------------------------------------------------
    def parseExtendedTagId(self, tagIdExtended, lead, block):
        matches = re.match(r'^([^\.]+)\.(.*)$', tagIdExtended)
        if (matches is None):
            msg = 'Bad syntax for tag, it must be of the form TAGTYPE.TAGID but got "{}"'.format(tagIdExtended)
            self.raiseBlockException(block, 0, msg)
        tagType = matches.group(1).strip()
        tagId = matches.group(2).strip()

        if (tagType not in ['cond','doc','day','check','trophy','decoy']):
            msg = "Bad tag type for tag ({}), should be from ['cond','doc','day','check','trophy','decoy'].".format(tagIdExtended)
            self.raiseBlockException(block, 0, msg)
        #
        return [tagType, tagId]
# ---------------------------------------------------------------------------
        


# ---------------------------------------------------------------------------
    def findTag(self, tagIdExtended, lead, block, flagMustExist, flagDefineIfNew):
        if (tagIdExtended in self.tagMap):
            tagDict = self.tagMap[tagIdExtended]
            return tagDict
        # not found
        if (flagDefineIfNew):
            args = {'id': tagIdExtended}
            tagDict = self.doDefineTag(tagIdExtended, args, lead, None, block)
            return tagDict
        if (flagMustExist):
            msg = 'Could not find tag with extended id "{}".'.format(tagIdExtended)
            self.raiseBlockException(block, 0, msg)
        return None


# ---------------------------------------------------------------------------
    def moveTagToEnd(self, tagIdExtended):
        if (tagIdExtended not in self.tagMap):
            return None
        tagDict = self.tagMap[tagIdExtended]
        del self.tagMap[tagIdExtended]
        self.tagMap[tagIdExtended] = tagDict
        return tagDict
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def makeTagLabelForCondition(self, tagId, flagConverToLetterIfEnabled):
        #
        conditionTagsAsLetters = self.getConditionTagsAsLetters()

        # use random letters as tags
        if (conditionTagsAsLetters) and (flagConverToLetterIfEnabled):
            # initialize list if empty
            if (len(self.tagConditionLabelsAvailable)==0):
                # refresh it
                self.tagConditionLabelStage += 1
                if (self.tagConditionLabelStage == 1):
                    suffix = ''
                else:
                    suffix = str(self.tagConditionLabelStage)
                #self.tagConditionLabelsAvailable = list([chr(item)+suffix for item in range(ord("A"), ord("Z") + 1)])
                self.tagConditionLabelsAvailable = list([item+suffix for item in 'ABCDEFGHJKLMNOPQRSTUVWXYZ'])
                # no more randomizing
                #random.shuffle(self.tagConditionLabelsAvailable)
            # try to use first letter of tag
            firstLetter = tagId[0].upper()
            if (firstLetter in self.tagConditionLabelsAvailable):
                chosenLetter = firstLetter
            else:
                # find nearest one HIGHER than it (wrapping around if needed)
                chosenLetter = None
                for c in self.tagConditionLabelsAvailable:
                    if (c>firstLetter):
                        # got it
                        chosenLetter = c
                        break
                if (chosenLetter is None):
                    # we warp around
                    chosenLetter = self.tagConditionLabelsAvailable[0]
            self.tagConditionLabelsAvailable.remove(chosenLetter)
            label = chosenLetter
        else:
            label = tagId
        #
        return label



    def getConditionTagsAsLetters(self):
        return self.getOptionVal('conditionTagsAsLetters', False)

    def getOptionDisableTaskTags(self):
        return self.getOptionVal('disableTaskTags', False)      
# ---------------------------------------------------------------------------







# ---------------------------------------------------------------------------
    def doCreateOrFindTagForLead(self, lead, tagType):
        leadId = lead['id']
        block = lead['block']
        lead['properties']['leadTagType'] = tagType
        tagIdExtended = leadId
        tagDict = self.findTag(tagIdExtended, lead, block, False, False)
        tagLead = None
        if (tagDict is not None):
            tagLead = tagDict['lead']
            # drop down
        else:
            if (not leadId.startswith(tagType + '.')):
                tagIdExtended = tagType + '.' + leadId
            else:
                tagIdExtended = leadId
            tagDict = self.findTag(tagIdExtended, lead, block, False, False)
            if (tagDict is not None):
                tagLead = tagDict['lead']
                # drop down
        if (tagLead is None):
            # create
            args = lead['properties']
            tagDict  = self.doDefineTag('', args, lead, None, block)
            tagLead = lead
        else:
            # force this man lad
            tagDict['lead'] = lead

        return tagDict


    def doCreateTagForHintLead(self, lead):
        # this is called on a NEW hint lead being processed
        leadId = lead['id']
        block = lead['block']
        hintProperties = lead['properties']
        lead['properties']['leadTagType'] = 'hint'
        # the lead will be called hint.cond.name or hint.doc.name etc.
        matches = re.match('^hint\.([^.]*)\.(.*)$', leadId)
        if (matches is None):
            self.raiseLeadException(lead,0,'Syntax error in lead name ({}), expected to start with "hint."'.format(leadId))
        tagType = matches.group(1)
        tagName = matches.group(2)
        tagIdExtended = tagType + '.' + tagName
        tagDict = self.findTag(tagIdExtended, lead, block, False, False)
        if (tagDict is not None):
            # the underlying tag has already been defined, so dont create a new one
            # this would be common for a DOC which is defined by its OWN lead
            # now as a kludge for hint order we REMOVE it and reinsert it
            tagDict = self.moveTagToEnd(tagIdExtended)
            tagLead = tagDict['lead']
            # drop down
        else:
            # being created here
            #tagDict  = self.doDefineTag(tagIdExtended, hintProperties, lead, lead, block)
            tagDict  = self.doDefineTag(tagIdExtended, hintProperties, lead, None, block)
            tagLead = lead
            # drop down

        # any other hint properties that should add to existing tag?
        targetHintLabel = tagDict['labelFull']
        hintProperties['renderId'] = 'Hint for ' + targetHintLabel
        hintProperties['reportExtra'] = tagIdExtended
        if ('deadline' in hintProperties):
            tagDict['deadline'] = hintProperties['deadline']
        tagDict['hintLead'] = lead

        # make a link from the TAG to the HINT
        self.createMindMapLinkBetweenTagAndHint(tagDict, lead)

        return tagDict
# ---------------------------------------------------------------------------




    
# ---------------------------------------------------------------------------
    def doDefineTag(self, tagIdExtended, args, lead, tagLead, block):
        # our new system has all tags being defined explicitly before they are used; this is to flag any spelling errors early, and to allow us to provide extra info about tags
        # all tags are now in the form of TAGTYPE.TAGID
        # where TAGTYPE is currently from [day, cond, doc]
        # cond tags are user defined conditions that are referred to by unique obfuscated single letters that are assigned and checked
        # doc tags refer to Documents by Number, at end of book
        # day tags refer to the current day and are somewhat automatically assigned
        flagErrorIfExists = True
        #
        if (tagIdExtended==''):
            tagIdExtended = args['id']

        # error if it already exists
        tagDict = self.findTag(tagIdExtended, lead, block, False, False)
        if (tagDict is not None):
            if (flagErrorIfExists):
                msg = 'ERROR: Trying to define tag with extended id "{}", but it already exists.'.format(tagIdExtended)
                self.raiseBlockException(block, 0, msg)
            # no error just return it
            return tagDict

        # ok first NEW thing we do is we split up tagId which should be of the form TYPE.ID, and validate type
        [tagType, tagId] = self.parseExtendedTagId(tagIdExtended, lead, block)

        # now create entry generic
        tagComment = jrfuncs.getDictValueOrDefault(args,'comment','')
        tagDict = {'idExtended': tagIdExtended, 'tagType': tagType, 'id': tagId, 'useCount': 0, 'useNotes': [], 'comment': tagComment, 'gainLeads': []}
        if ('deadline' in args):
            tagDict['deadline'] = args['deadline']

        # tag type specific stuff
        # we need to set label, and gainText, which is used when the player GAINS this tag
        if (tagType=='day'):
            # day tags are automatic and not created?
            # ATTN: unfinished
            day = args['day']
            relation = args['relation']
            #
            label = 'Day ' + tagId
            tagDict['label'] = label
            tagDict['mindMapLabel'] = tagId
            tagDict['labelExtended'] = label
            tagDict['labelFull'] = label
            tagDict['labelFullReport'] = label
            # use it
            if (relation == 'beforeday'):
                coreText = 'before day'
            elif (relation == 'afterday'):
                coreText = 'after day'
            elif (relation == 'onday'):
                coreText = 'day'
            #
            baseText = 'If it is {} {}'.format(coreText, day)
            tagDict['testText'] = baseText



        elif (tagType in ['cond','check','trophy','decoy']):
            # generate a letter-based label for this condition
            if (tagLead is None):
                tagLead = self.findLeadById(tagIdExtended, True)
                if (tagLead is None):
                    # this is not an error
                    pass
            tagDict['lead'] = tagLead
            
            conditionTagsAsLetters = self.getConditionTagsAsLetters()

            label = self.makeTagLabelForCondition(tagId, True)
            
            # labels
            tagDict['label'] = label
            labelForDisplay = '[**' + tagDict['label'] + '**]'
            tagDict['labelForDisplay'] = labelForDisplay
            if (conditionTagsAsLetters):
                tagDict['labelForReport'] = '[**' + tagDict['label'] + ' = ' + tagId + '**]'
            else:
                tagDict['labelForReport'] = tagDict['labelForDisplay']
            tagDict['labelWithLink'] = labelForDisplay
            tagDict['labelTyped'] = 'gained {} {}'.format(self.getText('condition'),labelForDisplay)
            tagDict['labelTypedReport'] = 'gained {} {}'.format(self.getText('condition'), tagDict['labelForReport'])

            #tagDict['labelExtended'] = '{} '.format(jrfuncs.uppercaseFirstLetter(self.getText('condition'))) + labelForDisplay
            #tagDict['labelFull'] = '{} '.format(jrfuncs.uppercaseFirstLetter(self.getText('condition'))) + label
            tagDict['labelExtended'] = '{} '.format(jrfuncs.uppercaseFirstLetter(self.getText('condition'))) + labelForDisplay
            tagDict['labelFull'] = '{} '.format(jrfuncs.uppercaseFirstLetter(self.getText('condition'))) + label
            tagDict['labelFullReport'] = '{} '.format(jrfuncs.uppercaseFirstLetter(self.getText('condition'))) + label + '({})'.format(tagId)
            #
            conditionTagsAsLetters = self.getConditionTagsAsLetters()
            if (conditionTagsAsLetters):
                gainText = 'You have now gained the {} {{}}; please circle this letter in your case log (if it\'s not already circled).'.format(self.getText('condition'))
            else:
                gainText = 'You have now gained the {} keyword {{}}; please note this keyword in your case log (if you haven\'t done so already).'.format(self.getText('condition'))
            #
            tagDict['gainTextPlayer'] = gainText.format(tagDict['labelForDisplay'])
            tagDict['gainTextReport'] = gainText.format(tagDict['labelForReport'])
            #
            tagDict['mindMapLabel'] = tagId
            #
            # lead info
            if (tagLead is not None):
                tagLeadProps = tagLead['properties']
                # force render id to be the label
                tagLeadProps['renderId'] = '{} ['.format(jrfuncs.uppercaseFirstLetter(self.getText('condition'))) + label + ']'

            #
            if (lead is not None):
                mainLeadProps = lead['properties']
                if ('deadline' in mainLeadProps):
                    # kludge to add deadline to label if we are in a hint for a check lead
                    tagDict['mindMapLabel'] += '\n(deadline day {})'.format(mainLeadProps['deadline'])



        elif (tagType=='doc'):
            # find the lead being referred to by this document tag
            #lead = self.findLeadById(tagId, True)
            if (tagLead is None):
                tagLead = self.findLeadById(tagIdExtended, True)
                if (tagLead is None):
                    msg = 'ERROR: Trying to define doc tag but lead id referrenced ({}) could not be found.'.format(tagId)
                    self.raiseBlockException(block, 0, msg)
            #
            tagDict['lead'] = tagLead
            # generate a label which is the document unique NUMBER (documents are referred to by #)
            docIndex = self.tagDocumentIndex
            tagDict['docIndex'] = docIndex
            self.tagDocumentIndex += 1
            label = 'Document {}'.format(docIndex+1)
            labelNoInfo = '**' + label + '**'
            tagDict['label'] = label
            tagDict['labelFullReport'] = tagIdExtended
            #
            tagLeadProps = tagLead['properties']
            # add info to label
            leadLabel = jrfuncs.getDictValueOrDefault(tagLeadProps, 'label', '')

            info = jrfuncs.getDictValueOrDefault(tagLeadProps, 'info', leadLabel)
            if (info!=''):
                label += ' ({})'.format(info)
            #
            tagDict['labelForDisplay'] = '**' + label + '**'
            tagDict['labelForReport'] = tagDict['labelForDisplay']
            tagDict['labelTyped'] = 'gained access to {}'.format(labelNoInfo)
            tagDict['labelTypedReport'] = 'gained access to {}'.format(label)
            tagDict['labelExtended'] = 'Document **{}**'.format(docIndex+1)
            tagDict['labelFull'] = 'Document {}'.format(docIndex+1)

            # important -- force the renderId of the lead; this is important because it is used as target of link generated below
            tagLeadProps['renderId'] = tagDict['label']
            tagLeadProps['reportExtra'] = tagIdExtended

            # label for mindmap; it's important that this matches the lead label as that is what is used for mindmap node creation in other places
            # ATTN: THIS DOES NOT GET USED CURRENTLY BECAUSE THE LEAD ALREADY CREATES THE MINDMAP NODE FOR THIS DOCUMENT TAG
            #tagDict['mindMapLabel'] = leadLabel if (leadLabel != '') else label
            tagDict['mindMapLabel'] = '{}: {}'.format(tagIdExtended, leadLabel) if (leadLabel != '') else tagIdExtended

            documentLocation = jrfuncs.getDictValueOrDefault(tagLeadProps, 'location', None)
            if ((documentLocation is None) or (documentLocation == 'book') or (documentLocation=='')):
                locationText = 'the back of this book'
                labelWithLink = self.makeTextLinkToLead(tagLead, label, False, '+p')
            else:
                # external documents
                locationText = documentLocation
                labelWithLink = label
            #
            tagDict['labelWithLink'] = labelWithLink
            #
            gainText = 'You may now access {} from {}; record this fact in your case log (unless you had gained access earlier).'.format(labelWithLink, locationText)
            tagDict['gainTextPlayer'] = gainText
            tagDict['gainTextReport'] = gainText





        # store it
        self.tagMap[tagIdExtended] = tagDict

        # mindmap
        if (True):
            self.creatMindMapNodeForTag(tagDict, lead)

        # return it
        return tagDict
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def calcTaskInstructions(self):
        # generate markdown text instructions for tasks
        if (self.getOptionDisableTaskTags()):
            return ''
        mtext = '\n\n## Instructions for Event Grid:\n'
        mtext += 'Before starting the case, locate the Event Grid on your case log sheet, and draw a line through the cells on each row that are to the right of those shown below, as they are unused.\nDuring play you will be told to mark when you have completed a task. Only when you finsish all the tasks on a row corresponding to your current day can you end your day and proceed to the end-of-shift briefing. Also note that it is completely normal to complete tasks on rows past your current day\'s row.\n'
        self.taskDays = jrfuncs.sortDictByKeys(self.taskDays)
        for taskDayIndex, taskDay in self.taskDays.items():
            line = ''
            line = '**{}**:  '.format(taskDayIndex)
            for k,v in taskDay.items():
                index = v['index']
                line += ' [{}] '.format(chr(65+index))
            mtext += line + '\n'
        return mtext
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
    def doDeadlineInfo(self, args):
        flagBorder = True
        day = args['day']
        stage = jrfuncs.getDictValueOrDefault(args, 'stage', '')
        limit = jrfuncs.getDictValueOrDefault(args, 'limit', '')
        stage = jrfuncs.getDictValueOrDefault(args, 'stage', '')
        startLimit = jrfuncs.getDictValueOrDefault(args, 'start', '')
        endLimit = jrfuncs.getDictValueOrDefault(args, 'end', '')
        isClockModeEnabled = self.getOptionClockMode()
        lastDay = jrfuncs.getDictValueFromTrueFalse(args, 'last', False)
        flagShowHint = (stage not in ['pre'])

        # build up a list of things they must find before the end of the passed day
        lines = []
        for tagId, tagDict in self.tagMap.items():
            if ('deadline' in tagDict):
                deadline = tagDict['deadline']
                if (deadline == day):
                    line = ' * {}'.format(tagDict['labelExtended'])
                    hintLead = jrfuncs.getDictValueOrDefault(tagDict,'hintLead',None)
                    if (hintLead is not None):
                        # add link to hint lead
                        if (flagShowHint):
                            hintLinkText = self.makeTextLinkToLead(hintLead, 'hint', False, '+onpagelink')
                            line += ' ({})\n'.format(hintLinkText)
                    # add line to lines list
                    lines.append(line)

        requiredItemCount = len(lines)





        resultText = '%Symbol.Mark% '
        if (requiredItemCount==0):
            # no items that must be found
            resultText = 'There are no items that must be found before the end of **day {}**.\n'.format(itemsText, day)
        else:
            # there are rquired items

            #
            itemsText = '**{}** item{}'.format(requiredItemCount, jrfuncs.plurals(requiredItemCount,'s'))
            if (stage=='pre'):
                if (int(day)>1):
                    alreadyText = ' (if you haven\'t found them already)'
                else:
                    alreadyText = ''
                resultText += 'The following {} must be found before you may end **day {}**{}.  You should note this on your case log in some way to avoid having to consult this list while playing.\n'.format(itemsText, day,alreadyText)
            elif (stage=='post'):
                resultText += 'You should have found the following {} before you ended **day {}**.  If you have missed one or more, return to searching for leads until you find all of them.  If you are stuck you may consult the hints, in order from top to bottom:\n'.format(itemsText, day)
            else:
                resultText += 'The following {} must be found before you may end **day {}**:\n'.format(itemsText, day)
            #
            resultText += '\n'.join(lines)

        # clock

        if (limit!='') or (startLimit!=''):
            resultText += '\n~\n%Symbol.Clock% THE CLOCK IS TICKING! '
            if (isClockModeEnabled):
                # TIME LIMIT MODE
                # calculate start and end time
                if (startLimit!=''):
                    startTimeHour = int(startLimit)
                    endTimeHour = int(endLimit)
                else:
                    if (limit=='none'):
                        durationMinutes = 60 * 14
                    else:
                        durationMinutes = int(limit) * self.getOptionClockTimeDefaultLead()
                        # add a bit for unfound leads
                        durationMinutes += (int(limit) * 5) / 2
                    durationHours = math.ceil(durationMinutes/60)
                    startTimeHour = 6
                    endTimeHour = startTimeHour + durationHours
                    maxEnd = 20
                    minEnd = 17
                    if (endTimeHour > maxEnd):
                        delta = -1 * (endTimeHour-maxEnd)
                    elif (endTimeHour < minEnd):
                        delta = minEnd-endTimeHour
                    else:
                        delta = 0
                    startTimeHour += delta
                    endTimeHour += delta
                #
                if (endTimeHour>=12):
                    endTime = '{}pm'.format(endTimeHour-12)
                else:
                    endTime = '{}am'.format(endTimeHour)
                if (startTimeHour>=12):
                    startTime = '{}pm'.format(startTimeHour-12)
                else:
                    startTime = '{}am'.format(startTimeHour)
                #
                if (stage=='post'):
                    resultText += 'You should have recorded on your case log that '
                else:
                    resultText += 'Record on your case log that '
                #
                if (False):
                    if (lastDay):
                        instructionMsg = ' See the special instructions at the front of this storybook for rules regarding overtime on the last day of the case.'
                    else:
                        instructionMsg = ' See the instructions at the front of this storybook for rules regarding overtime and ending your day early.'
                else:
                    instructionMsg = ''
                #
                resultText += 'your current day starts at **{}** and ends at **{}**.'.format(startTime, endTime)
                if (requiredItemCount>0):
                    resultText += ' If you have *not* found all of the required items above by **{}**, you enter overtime. In overtime there is no limit to how many leads you may visit, time does not advance, and your day ends once you find all of the required items.'.format(endTime)
                else:
                    resultText += ' Keep track of what time you visit each lead, until you reach **{}**, after which your day ends.{}'.format(endTime, instructionMsg)

#                if (stage=='post'):
#                    wishTo = ''
#                else:
#                    wishTo = 'wish to '
#                if (not lastDay):
#                    resultText += ' If you find all of the items and {}end your day early (before **{}**), calculate the number of whole hours remaining in the day (rounded down), and start your next day that many hours earlier. Ending your day before overtime begins will improve your final score and may occasionally have other minor benefits.'.format(wishTo, endTime)

                # this is now combined with other reminder about tipes
                if (requiredItemCount>0) and (False) and (stage=='pre'):
                    resultText += ' There are hints available for each of the items above (see index).'

                resultText += '\n'
            else:
                # LEAD LIMIT COUNT MODE
                if (requiredItemCount==0):
                    resultText += 'You may visit up to **[{}]** leads on **day {}**'.format(limit,day)
                if (limit=='none'):
                    resultText += '\nNOTE: After you find all of these items, you may visit as many additional leads as you wish, and may end the case when you are ready.\n'.format(limit, day)
                else:
                    if (int(day)>1) and (not isClockModeEnabled):
                        leftoverText = ' (plus any remaining from previous days ended early)'
                    else:
                        leftoverText = ''
                    resultText += 'You may visit up to **[{}]** leads on **day {}**{} in which to find all of these items; you cannot end the day until you find all of them.  If you find them all before that limit, count the number of leads you have remaining and record that as a bonus to your final score.  Once you find all of the items you *may* choose to end the day, banking HALF your remaining leads for use tomorrow. If you fail to find all items within the limit, keep playing and mark +1 overtime for each additional lead visited beyond the limit, until you find all items.  Do not count leads that have no entry.'.format(limit, day, leftoverText)
                    if (stage=='pre'):
                        resultText += ' There are specific hints available for each of the items above.  Note also that finishing your day on time (or early) may occasionally have other future benefits.'
                #
                resultText += '\n'

            if (lastDay):
                if (False):
                    resultText += '%Symbol.Exclamation% **Note: This is the final day of the case.**  See the instructions at the front of this storybook for how overtime differs on the final day.\n'

        if (flagBorder):
            #resultText = '\n~\n~\n---\n\n' + resultText + '---'
            resultText = '\n~\n%boxstart%\n' + resultText + '%boxend%\n'
        return [resultText, None]
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def buildHintLeadListForTag(self, lead, block):
        leadId = lead['id']
        lines = []
        # we want to find all leads where the player can GAIN the tag specified in the hint
        matches = re.match(r'^hint\.(.*)$', leadId)
        if (matches is None):
            # not found
            return lines
        tagIdExtended = matches.group(1)
        tagDict = self.findTag(tagIdExtended, lead, block, False, False)
        if (tagDict is None):
            # not found
            return lines
        #
        gainLeads = tagDict['gainLeads']
        if (len(gainLeads)==0):
            # no leads gain it
            return lines
        for gainLead in gainLeads:
            line = self.makeTextLinkToLead(gainLead,None,False,True)
            lines.append(line)
        return lines
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def includeUserFile(self, filePath):
        jrprint('WARNING: includeUserFile1 for "{}" is not safe or secure.'.format(filePath))
        filePath = self.resolveTemplateVars(filePath)
        jrprint('WARNING: includeUserFile2 for "{}" is not safe or secure.'.format(filePath))
        encoding = self.getOptionValThrowException('storyFileEncoding')
        text = jrfuncs.loadTxtFromFile(filePath, True, encoding)
        return text
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
    def safelyResolveImageSource(self, filePath):
        flagThrowException = True
        #
        if (filePath.startswith("images/")):
            imageFilePath = filePath[7:]
        else:
            imageFilePath = filePath
        #
        filePathResolvedList = self.gameFileManager.findImagesForName(imageFilePath, True, True)
        #filePathResolvedList = self.imageFileFinder.findImagesForName(imageFilePath, True, True)
        #
        if (filePathResolvedList is None):
            if (flagThrowException):
                raise Exception("Failed to safely resolve referenced image file '{}'; check that you have uploaded a file with this name.".format(filePath))
            else:
                filePathResolved = 'IMAGE_FILE_NOT_FOUND:' + pylatex.escape_latex(filePath)
        else:
            filePathResolved = filePathResolvedList[0]
            filePathResolved = filePathResolved.replace('\\','/')
        return filePathResolved
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def scanImages(self):
        # dirs for scanning for images
        raise Exception("Scan images no longer used.")
    
        defaultSaveDir = self.getOptionValThrowException('savedir')
        saveDir = self.getOptionVal('chapterSaveDir', defaultSaveDir)
        saveDir = self.resolveTemplateVars(saveDir)

        # image file helper
        imageDir = self.getOptionVal('imagedir', saveDir + '/images')
        imageDir = self.resolveTemplateVars(imageDir)
        self.imageFileFinder.setDirectoryList([{'prefix':'', 'path': imageDir,},])
        self.imageFileFinder.scanDirs(False)
# ---------------------------------------------------------------------------
























# ---------------------------------------------------------------------------
    def runAll(self):
        self.loadStoryFilesIntoBlocks()
        #
        self.runAllSteps()
    
    def runAllSteps(self):
        flagCleanAfter = "none"
        #
        self.processHeadBlocks()
        self.addZeroLeadWarning()
        self.createCommonMindMapNodes()
        self.processLeads()
        #
        self.runDebugExtraStepsIfNeeded()
        #
        self.saveLeads()
        #self.scanImages()
        self.renderLeadsDual(flagCleanAfter)
        #
        self.saveAllManualLeads()
        #
        self.saveAltStoryFilesAddLeads()
        #
        self.saveMindMapStuff(False)
        #
        #self.debug()
        self.reportNotes()
        self.reportWarnings()
        self.reportSummary()


    def runDebugExtraStepsIfNeeded(self):
        if (self.didRunDebugExtraSteps):
            return
        self.didRunDebugExtraSteps = True
        #
        self.databaseDebugLeads()
        self.postProcessMindMap()
        self.addReportLogicLinks()
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
    def runPreBuildSteps(self):
        self.processHeadBlocks()
        self.addZeroLeadWarning()
        self.createCommonMindMapNodes()
        self.processLeads()
        #self.scanImages()


    def runBuildList(self, flagCleanAfter):
        # new build list generator
        self.runPreBuildSteps()
        #
        self.clearBuildLog()
        #
        # clean all files in prep for running (we no longer do this, we hope our caller does)
        if (False):
            self.cleanBuildList()
        #
        #
        buildList = self.getOptionValThrowException('buildList')
        skipCount = 0
        for build in buildList:
            success = self.runBuild(build, flagCleanAfter)
            if (success=="skip"):
                self.addBuildLog("Skipped build '{}' due to incompatible options (page size vs. column count?)".format(build["label"]), False)
                skipCount += 1
            elif (not success):
                break
        #
        # error if all skipped
        if (skipCount == len(buildList)):
            self.addBuildLog("All builds skipped due to incompatible options (page size vs. column count?)", True)
        #
        return (not self.getBuildErrorStatus())


    def cleanBuildList(self):
        # new build list generator
        buildList = self.getOptionValThrowException('buildList')
        for build in buildList:
            retv = self.cleanBuild(build)

    def cleanBuild(self, build):
        label = build["label"]
        #jrprint("Cleaning build: {}".format(label))
        # BUILD
        suffix = build["suffix"]
        #
        info = self.getOptionValThrowException('info')
        chapterName = self.getChapterName()
        baseOutputFileName = chapterName + suffix
        defaultSaveDir = self.getSaveDir()
        saveDir = self.getOptionVal('chapterSaveDir', defaultSaveDir)
        saveDir = self.resolveTemplateVars(saveDir)
        jrfuncs.createDirIfMissing(saveDir)
        renderFormat = build['format']
        #
        deleteFileExtensions = []
        if (renderFormat=='latex') or (renderFormat=='pdf'):
            deleteFileExtensions = ['aux', 'latex', 'pdf', 'log', 'out', 'toc']
        elif (renderFormat=='html'):
            deleteFileExtensions = ['html', 'pdf']
        else:
            raise Exception('Unknown build form: "{}".'.format(renderFormat))
        #
        self.deleteExtensionFilesIfExists(saveDir, baseOutputFileName, deleteFileExtensions)
        self.deleteSaveDirFileIfExists(saveDir, 'texput.log')










    def runBuild(self, build, flagCleanAfter):
        errorCounterPreRun = self.getBuildErrorCount()
        label = build["label"]
        jrprint("Building: {}".format(label))
        #format = build["format"]
        #paperSize = build["paperSize"]
        layout = build["layout"]
        buildVariant = build["variant"]
        gamefileType = build["gameFileType"]
        gameName = build["gameName"]
        #
        optionAddVersionToZipFileName = True
        optionAddDateToZipFileName = True

        # set save dir from gamefilemanager and gamefiletype
        self.setSaveDirFromGameFileType(gamefileType)

        if (buildVariant=="zip"):
            # special zip instruction
            generatedFileList = self.getGeneratedFileListForZip()
            optionZipOutDir = self.getSaveDir()
            optionZipSuffix = '_' + gamefileType
            if (optionAddVersionToZipFileName):
                info = self.getOptionValThrowException('info')
                versionstr = jrfuncs.getDictValueOrDefault(info, 'version', '')
                if (versionstr!=''):
                    versionStrSafe = "_v"+jrfuncs.safeCharsForFilename(versionstr)
                    optionZipSuffix += versionStrSafe
            if (optionAddDateToZipFileName):
                nowTime = datetime.datetime.now()
                optionZipSuffix += nowTime.strftime('_%Y%m%d')
            if (len(generatedFileList)>0):
                zipFilePath = jrfuncs.makeZipFile(generatedFileList, optionZipOutDir, gameName + optionZipSuffix)
                jrprint("Zipped {} files to '{}'.".format(len(generatedFileList), zipFilePath))
                self.addGeneratedFile(zipFilePath, False)
            self.clearGeneratedFileListForZip()
            return True

        # sanity check
        if (buildVariant not in ['normal', 'debug', 'summary']):
            raise Exception("Unknown build variant in runbuild: '{}'.".format(buildVariant))

        #
        fontSize = build['fontSize']
        paperSizeLatex = build['paperSizeLatex']
        doubleSided = build['doubleSided']
        columns = build['columns']
        solo = build['solo']
        suffix = build['suffix']
        #
        #
        buildVariantToMode = {'normal': 'normal', 'debug':'report', 'summary': 'normal'}
        buildVariantToLeadList = {'normal': None, 'debug': None, 'summary': ['summary|cover']}

        #
        if (buildVariant=="debug"):
            self.runDebugExtraStepsIfNeeded()
        elif (buildVariant=="normal"):
            pass
        elif (buildVariant=="summary"):
            pass
        else:
            raise Exception("Variant mode '{}' not understood in runBuildList for label '{}'".format(buildVariant, label))


        # set chapter name which is used for saving files

        self.setChapterName(gameName)

        # BUILD

        options = {'suffix':suffix, 'layout': layout, 'paperSize': paperSizeLatex, 'fontSize': fontSize, 'doubleSided': doubleSided, 'columns': columns, 'solo': solo, 'mode': buildVariantToMode[buildVariant], 'leadList': buildVariantToLeadList[buildVariant]}
        self.renderLeads(options, flagCleanAfter)


        # debug extra steps
        if (buildVariant=="debug"):
            # extra things we do in debug mode?
            self.saveLeads()
            self.saveAllManualLeads()
            if (len(self.storyFileList)>0):
                self.saveAltStoryFilesAddLeads()
            else:
                self.saveAltStoryTextDefault()
            #
            self.saveMindMapStuff(True)
            self.reportNotes()
            self.reportWarnings()
            self.reportSummary()
            #
            # just to make a file copy
            self.saveTextLeads()

        errorCounterPostRun = self.getBuildErrorCount()
        success = (errorCounterPostRun <= errorCounterPreRun)
        return success

# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
    def setSaveDirFromGameFileType(self, gamefileType):
        saveDir = self.gameFileManager.getDirectoryPathForGameType(gamefileType)
        self.setOption("savedir", saveDir)
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
    def recalcRenderOptions(self, overrideRenderOptions):
        self.calculatedRenderOptions = jrfuncs.deepCopyListDict(self.getOptionValThrowException('renderOptions'))
        jrfuncs.deepMergeOverwriteA(self.calculatedRenderOptions, overrideRenderOptions)
        return self.calculatedRenderOptions

    def getComputedRenderOptions(self):
        if (self.calculatedRenderOptions is None):
            self.recalcRenderOptions({})
        return self.calculatedRenderOptions
# ---------------------------------------------------------------------------




























