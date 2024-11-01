# generic helper functions

# imports
import os
import shutil
import re
import csv
import copy
import time
import html
import io
import datetime
import zipfile
from functools import reduce
import random
import json
import math
import traceback
import glob
from pathlib import Path




#---------------------------------------------------------------------------
LogFilePath = 'logs'
moduleLogFile = None
moduleErrorPrintCount = 0

def setLogFileDir(path):
    global LogFilePath
    LogFilePath = path

def calcLogFilePath():
    global LogFilePath

    # do this ourselves to avoid recurrent loop of log messages when creating missing dir
    if (True):
        dirPath = LogFilePath
        dirExists = os.path.exists(dirPath)
        if not dirExists:
            print('creating directory: ' + dirPath)
            os.makedirs(dirPath)
    else:
        createDirIfMissing(LogFilePath)

    filePath = LogFilePath + '/log_' + time.strftime('%Y%m%d_%H%M%S') + '.txt'
    return filePath

def openLogFile():
    global moduleLogFile
    filePath = calcLogFilePath()
    encoding = 'utf-8'
    moduleLogFile = open(filePath, 'a+', encoding=encoding)
    print('\n\n>LOGGING TO: {}..'.format(filePath)+'\n')
    return moduleLogFile

def getOpenLogFile():
    global moduleLogFile
    if (not moduleLogFile):
        moduleLogFile = openLogFile()
    return moduleLogFile

def incLogErrorPrintCount():
    global moduleErrorPrintCount
    moduleErrorPrintCount += 1
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def mylog(str):
    jrprint('[jrfuncs] ' + str)
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
# utilities
def createDirIfMissing(dirPath):
    dirExists = os.path.exists(dirPath)
    if not dirExists:
       mylog('creating directory: ' + dirPath)
       os.makedirs(dirPath)


def createDirForFullFilePathIfMissing(filePath):
    dirPath = os.path.dirname(filePath)
    dirExists = os.path.exists(dirPath)
    if not dirExists:
       mylog('creating directory: ' + dirPath)
       os.makedirs(dirPath)



def pathExists(path):
    pathExists = os.path.exists(path)
    return pathExists


def directoryExists(path):
    pathExists = os.path.exists(path)
    if (not pathExists):
        return False
    return (not os.path.isfile(path))



def copyFile(sourcePath, destPath, fname):
    jrprint('Asked to copy "{}" from "{}" to "{}".'.format(fname, sourcePath, destPath))
    srcFile = sourcePath + '/' + fname
    if (not pathExists(srcFile)):
        jrprint('Error: cannot copy from "{}" to "{}" because source file does not exist.'.format(sourcePath, destPath))
        return False
    createDirIfMissing(destPath)
    shutil.copy2(sourcePath+'/'+fname, destPath)
    return True

def copyFilePath(sourcePath, destPath):
    #jrprint('Asked to copy file from "{}" to "{}".'.format(sourcePath, destPath))
    shutil.copy2(sourcePath, destPath)
    return True

def renameFile(sourcePath, destPath):
    shutil.move(sourcePath, destPath)


def deleteFilePathIfExists(filePath):
    if (pathExists(filePath)):
        os.remove(filePath)


def deleteDirPathIfExists(dirPath):
    if (not dirPath.endswith("/")):
        dirPath += "/"
    if (pathExists(dirPath)):
        shutil.rmtree(dirPath + "/")
        return True
    return False



def deleteExtensionFilesIfExists(baseDir, baseFileName, extensionList):
    for extension in extensionList:
        filePath = '{}/{}.{}'.format(baseDir, baseFileName, extension)
        deleteFilePathIfExists(filePath)

def deleteSaveDirFileIfExists(baseDir, fileName):
    filePath = '{}/{}'.format(baseDir, fileName)
    deleteFilePathIfExists(filePath)


def renameDirPath(dirPath, newDirPath, flagUniquify):
    if (not dirPath.endswith("/")):
        dirPath += "/"
    if (not pathExists(dirPath)):
        return False
    if (pathExists(newDirPath)) and (not flagUniquify):
        return False
    # give it unique destination pathname if needed
    if (pathExists(newDirPath)):
        newDirPathBase = newDirPath
        suffixIndex = 1
        while (pathExists(newDirPath)):
            suffixIndex += 1
            newDirPath = newDirPathBase + str(suffixIndex)
    # move it
    retv = shutil.move(dirPath, newDirPath)
    # return path moved to
    return newDirPath


def deleteFilePattern(baseDir, filePattern):
    # delete all files with the given pattern in the given directory
    for filePath in glob.glob(baseDir + "/" + filePattern):
        #jrprint("Would delete {}.".format(filePath))
        os.unlink(filePath)
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def removeLeadingZeros(val):
    if (val==''):
        return val
    val = re.sub('^0+', '', val)
    if (val==''):
        val = '0'
    return val


def zeropadIfNumber(text,digits):
    if (text==''):
        return text
    matches = re.match(r'^(\d+)(.*)$', text)
    if (matches is None):
        return text
    text = '{num:0{width}}{late}'.format(num=int(matches[1]), width = digits, late=matches[2])
    return text




def zeroPadNumbersAnywhereInString(text, digits):
    matches = re.match(r'^([^\d]*)(\d+)(.*)$', text)
    if (matches is None):
        return text
    text = '{early}{num:0{width}}{late}'.format(early=matches[1], num=int(matches[2]), width = digits, late=matches[3])
    return text


def zeroPadNumbersAnywhereInStringAllRepFunc(matches, digits):
    rep = '{early}{num:0{width}}'.format(early=matches[1], num=int(matches[2]), width = digits)
    return rep

def zeroPadNumbersAnywhereInStringAll(text, digits):
    text = re.sub(r'([^\d]*)(\d+)', lambda m: zeroPadNumbersAnywhereInStringAllRepFunc(m, digits), text)
    return text




def removeZeroPaddedNumberAnywhere(text):
    while (True):
        matched = False
        matches = re.match(r'^0+(\d+)(.*)$', text)
        if (matches is not None):
            text = '{num}{late}'.format(num=int(matches[1]), late=matches[2])
            matched = True
        #
        matches = re.match(r'^(.*[\s\-\:\#])0+(\d+)(.*)$', text)
        if (matches is not None):
            text = '{early}{num}{late}'.format(early=matches[1], num=int(matches[2]), late=matches[3])
            matched = True
        if (matched == False):
            break
    return text


def removeZeroPaddedSingleLetterNumbersAnywhere(text):
    while (True):
        matched = False
        matches = re.match(r'^0+(\d+)(.*)$', text)
        if (matches is not None):
            text = '{num}{late}'.format(num=int(matches[1]), late=matches[2])
            matched = True
        #
        matches = re.match(r'^(.*[\s\-\:\#A-Z])0+(\d+)(.*)$', text)
        if (matches is not None):
            text = '{early}{num}{late}'.format(early=matches[1], num=int(matches[2]), late=matches[3])
            matched = True
        #
        if (matched == False):
            break
    return text
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def replaceAbbreviations(text, abbreviationList):
    # replace abbreviations
    for srpair in abbreviationList:
        osearchStr = srpair[0]
        oreplaceStr = srpair[1]
        searchStr = r'(\b)' + osearchStr + r'(\b)'
        replaceStr = r'\1' + oreplaceStr + r'\2'
        text = re.sub(searchStr, replaceStr, text, flags=re.IGNORECASE)
    return text

def replaceAbbreviationsWithPeriods(text, abbreviationList):
    # replace abbreviations
    for srpair in abbreviationList:
        osearchStr = srpair[0]
        oreplaceStr = srpair[1]
        searchStr = r'\s' + osearchStr + r'\s'
        replaceStr = ' ' + oreplaceStr + ' '
        text = re.sub(searchStr, replaceStr, text, flags=re.IGNORECASE)
        searchStr = r'^' + osearchStr + r'\s'
        replaceStr = oreplaceStr + ' '
        text = re.sub(searchStr, replaceStr, text, flags=re.IGNORECASE)
        searchStr = r'\s' + osearchStr + r'$'
        replaceStr = ' ' + oreplaceStr
        text = re.sub(searchStr, replaceStr, text, flags=re.IGNORECASE)
    return text


def addANumberSuffix(match):
    pre = match[1]
    num = match[2]
    post = match[3]+match[4]
    return pre + addSuffixForNumber(num) + post

def addNumberSuffixes(text):
    # untested
    text = re.sub(r'(\b)([\d]+)\s(st|street)(\b)', addANumberSuffix(), flags=re.IGNORECASE)
    return text


def lowercaseWholeWords(text, wordList):
    for word in wordList:
        searchStr = r'\s' + word + r'(\b)'
        replaceStr = r' ' + word.lower() + r'\1'
        text = re.sub(searchStr, replaceStr, text, flags=re.IGNORECASE)
    return text

def forceSeparateText(text, wordList, flagBefore, flagAfter):
    for word in wordList:
        if (flagBefore):
            searchStr = r'([a-zA-Z0-9\.])' + word
            replaceStr = r'\1 ' + word
            text = re.sub(searchStr, replaceStr, text, flags=re.IGNORECASE)
        if (flagAfter):
            searchStr = word + r'([a-zA-Z0-9\.])'
            replaceStr = word + r' \1'
            text = re.sub(searchStr, replaceStr, text, flags=re.IGNORECASE)
    return text
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def loadTxtFromFile(filePath, flagErrorIfNotFound, encoding):
    #jrprint('In loadTxtFromFile trying to load {}.'.format(filePath))
    if (not pathExists(filePath)):
        if (flagErrorIfNotFound):
            raise Exception('ERROR: could not loadTxtFromFile for "{}".'.format(filePath))
        #jrprint('In loadTxtFromFile failed to find {}.'.format(filePath))
        return None
    if (encoding is not None):
        try:
            with open(filePath, 'r', encoding=encoding) as f:
                txt = f.read()
                return txt
        except Exception as e:
            # drop down and try without encoding; this is secret to handling utf8 hell
            pass    
    with open(filePath, 'r') as f:
        txt = f.read()
        return txt



def saveTxtToFile(filePath, text, encoding):
    if (encoding is not None):
        try:
            with open(filePath, 'w', encoding=encoding) as f:
                f.write(text)
                return
        except Exception as e:
            # drop down and try without encoding; this is secret to handling utf8 hell
            pass         
    with open(filePath, 'w') as f:
        f.write(text)



def loadJsonFromFile(filePath, flagErrorIfNotFound, encoding):
    txt = loadTxtFromFile(filePath, flagErrorIfNotFound, encoding)
    data = json.loads(txt)
    return data
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def splitCommaPipeText(text):
    # split string by pipes, or commas if no pipe; skip if in double quotes
    # note that this does not properly handle double quoted items broken by commas
    pieces = text.split('|')
    if (len(pieces)>1):
        # it's pipe separated
        return pieces
    # otherwise its comma separated with possible double quote protection of commas
    # see https://stackoverflow.com/questions/8069975/split-string-on-commas-but-ignore-commas-within-double-quotes
    csvResults = csv.reader([text])
    pieces = next(csvResults)
    return pieces
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def isSimpleNameValid(name):
    if (not isSafeAscii(name)):
        return False
    if ('_' in name):
        return False
    if (',' in name):
        return False
    if ('?' in name):
        return False
    if ('+' in name):
        return False
    if ('--' in name):
        return False
    if ('[' in name) or (']' in name):
        return False
    if ('*' in name):
        return False
    if ('"' in name):
        return False
    if (name.startswith("'") or name.startswith('"')):
        return False
    if (name == 'UNKNOWN'):
        return False
    return True


def isSafeAscii(text):
    if (not text.isascii()):
        return False
    # alternative?
    try:
        if (text!=''):
            text.encode("ascii")
    except:
        # not good ascii
        return False
    return True
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------'
# stupidity; which is good

def removeDoubleSpaces(text):
    text = re.sub(r"\s\s+" , " ", text)
    return text

def removeDoubleSpacesOld(text):
    # c
    ' '.join(text.split())
    text = text.strip()
    return text
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
# see https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries
# note that this mutates a - t
def deepMerge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                deepMerge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                # jr mod to merge lists
                a[key] = a[key] + b[key]
            else:
                jrprint('WARNING: attmempting to merge dictionaries but got conflicting values at key {}; merging {} and {}.'.format(key, a, b))
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


def deepMergeMissingKeysFromBIntoA(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                deepMergeMissingKeysFromBIntoA(a[key], b[key], path + [str(key)])
            # do nothing
            pass
        else:
            a[key] = b[key]
    return a


def deepCopyListDict(a):
    return copy.deepcopy(a)



def combineListsToNewList(lista, listb):
    retlist = deepCopyListDict(lista)
    for item in listb:
        if (item not in retlist):
            retlist.append(item)
    return retlist


def setDictValuesIfMissing(pdict, defaultDictFields):
    for key in defaultDictFields:
        if (key not in pdict):
            pdict[key] = defaultDictFields[key]
    return pdict



def deepMergeOverwriteA(a, b, path=None):
    "merges b into a and overrides a when conflict"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                deepMerge(a[key], b[key], path + [str(key)])
            else:
                # replace a with b
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def getDictValue(thedict, key):
    return thedict[key] if key in thedict else None

def getDictValueOrDefault(thedict, key, defaultVal):
    return thedict[key] if ((thedict is not None) and (key in thedict)) else defaultVal

def getDictValueFromList(thedict, key, inList, defaultVal=None):
    if (key in thedict):
        val = thedict[key]
    else:
        val = defaultVal
    if (val not in inList):
        if (val is None):
            raise Exception('Value for field "{}" not found.'.format(key))
        else:
            raise Exception('Value for field "{}" not in allowed list: {}.'.format(key, inList))
    return val

def getDictValueFromTrueFalse(thedict, key, defaultVal):
    val = getDictValueFromList(thedict, key, ['true', 'false', None], None)
    if (val==None):
        if (defaultVal is None):
           raise Exception('Value for field "{}" not found and should be from [true,false] but found: "{}".'.format(key, val)) 
        return defaultVal
    if (val=='true'):
        return True
    if (val=='false'):
        return False
    raise Exception('Bad code path should not happen.') 
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def parseStreetAddressIntoHouseNumberAndStreetName(streetAddress):
    houseNumber = ''
    streetName = ''
    #matches = re.match(r'^([\dA-Za-z\-\/]+)\s+(.*)$', streetAddress)
    matches = re.match(r'^([\dA-Za-z\-\/]+)\s+(.*)$', streetAddress)
    if (matches is None):
        matches =re.match(r'^(.*)\s*(\&|\sand\s|\soff\s|\sat\s|\snear\s)(.*)$', streetAddress, re.IGNORECASE)
        if (matches is not None):
            streetName = matches[1]
        else:
            matches = re.match(r'^\s*([^\s]+)\s+(.*)$', streetAddress)
            if (matches is not None):
                streetName = matches[1]
    else:
        houseNumber = matches[1]
        streetName = matches[2]

    return [houseNumber, streetName]


def parseFullName(fullName):
    matches = re.match(r'^([^,]*)\s*\,\s*(.*)$', fullName)
    if (matches is not None):
        lastName = matches[1].strip()
        firstName = matches[2].strip()
        return [lastName, firstName]
    return [fullName, None]

def simplifySingleLastName(lastName):
    # remove anything before a space or comma
    matches = re.match(r'(^[^\s,\-]+)(.*)$', lastName)
    if (matches is None):
        return lastName.strip()
    return matches[1].strip()
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def replaceSimpleTempatedParams(text, vdict):
    #text = re.sub('\[([^\[\]]*)\]', lambda m: vdict[m.group(1)] if m.group(1) in vdict else 'UNKNOWN FIELD:' + m.group(1), text)
    text = re.sub(r'\[([^\[\]]*)\]', lambda m: vdict[m.group(1)] , text)
    return text
#---------------------------------------------------------------------------





#---------------------------------------------------------------------------
def kludgeFixWeirdBusinessNames(name):
    # little kludge to avoid having fictional automatic business names starting with a number; this can happen when we use a template for example and we miss parse a street name?
    if (False):
        # add something to start of number names
        matches = re.match(r'^(the )?([^a-zA-Z].*)$', name, re.IGNORECASE)
        if (matches is not None):
            name = 'The original ' + matches[1]
    return name
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def splitStringIntoList(text, separator):
    if (type(text) is not str):
        return text
    textList = text.split(separator)
    textList = [f for f in textList if (f!='')]
    return textList
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def lowercaseWholeMiddleWords(txt, wordList):
    # wherever we find wordlist words as long as its not start of text, convert to lowercase
    txtAsWords = txt.split(' ')
    for i, word in enumerate(txtAsWords):
        if (i==0):
            continue
        if (word.lower() in wordList):
            index = wordList.index(word.lower())
            txtAsWords[i] = wordList[index]

    # now reassemble
    txt = ' '.join(txtAsWords)
    return txt

#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def calcTrueOnProbability(prob):
    # return True if under probability
    if (random.random() < prob):
        return True
    return False
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
def addPrefixIfNonBlank(name, prefix):
    if (prefix==''):
        return name
    return prefix + ' ' + name
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
def addDisplayNameFromParts(pdict):
    firstName = pdict['firstName']
    lastName = pdict['lastName']
    prefix = pdict['prefix'] if 'prefix' in pdict else ''

    if (firstName == ''):
        displayName = lastName
    else:
        displayName = lastName + ', ' + firstName
    #
    if (prefix!=''):
        displayName += ' ' + prefix

    pdict['dName'] = displayName
    return pdict
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def reverseCommaParts(text, joinstr):
    parts = text.split(',')
    parts = [part.strip() for part in parts]
    parts.reverse()
    retText = joinstr.join(parts)
    retText = removeDoubleSpaces(retText)
    return retText
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
def removeQuotesAround(text):
    text = text.strip()
    textlen = len(text)
    if (textlen<2):
        return text
    if ((text[0]=='"') or (text[0]=="'")) and ((text[textlen-1]=='"') or (text[textlen-1]=="'")):
        text = text[1:textlen-2]
    return text
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def parseOptionalWeightedString(text):
    # parse something like "apples:0.5" into ["apples",0.5]
    # if no weight passed just return 1.0
    matches = re.match(r'^(.*)\s*\:\s*([\d\.]*)$', text)
    if (matches is None):
        txt = text
        weightVal = 1.0
    else:
        txt = matches[1]
        weightVal = float(matches[2])
    txt = txt.strip()
    return [txt, weightVal]
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def formatCaseLastName(name):
    name = name.strip()
    name = name.title()
    # now we want to fix up any name ending in I Ii Iii or Iv to be capitalized
    name = caseFixEndingRomanNumerals(name)
    return name

def formatCaseFirstName(name):
    name = name.strip()
    name = name.title()
    name = caseFixEndingRomanNumerals(name)
    return name


def caseFixEndingRomanNumerals(name):
    name = re.sub(r' Ii$', ' II', name)
    name = re.sub(r' Iii$', ' III', name)
    name = re.sub(r' Iv$', ' IV', name)
    return name


def containsHonorific(name):
    honorificList = ['sir', 'lady', 'lord', 'prince', 'king', 'queen', 'mr', 'mrs', 'ms', 'miss']
    for honorific in honorificList:
        rexp = r'\b' + honorific + r'\b'
        if (re.match(rexp,name)):
            return True
    return False
#---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def formatLocLabel(locLabel):
    try:
        locLabelInt = int(locLabel)
        locLabelFormatted = '{:03}'.format(locLabelInt)
    except Exception as e:
        if (locLabel==''):
            return('n/a')
        return locLabel
    return locLabelFormatted
    # ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
#
def jrprint(*args, **kwargs):
    # replacement for print function that will allow logging
    global moduleErrorPrintCount

    # create log file if needed
    logFile = getOpenLogFile()

    # check for any presence of the word error (this is just for end run reporting, its ok if its not precise)

    textLine = jrSprintf(args,kwargs).upper()
    if ('ERROR' in textLine) or ('EXCEPTION' in textLine):
        moduleErrorPrintCount += 1

    # log
    try:
        print(*args, file=logFile, **kwargs)
    except Exception as e:
        incLogErrorPrintCount()
        print('EXCEPTION1 WHILE TRYING TO PRINT TO FILE: {}'.format(e))
        # invoke normal print
        print(*args, **kwargs)
        return

    # invoke normal print
    return print(*args, **kwargs)


def jrlog(*args, **kwargs):
    # replacement for print function that will allow logging
    global moduleErrorPrintCount

    # create log file if needed
    logFile = getOpenLogFile()

    # log
    try:
        print(*args, file=logFile, **kwargs)
    except Exception as e:
        incLogErrorPrintCount()
        print('EXCEPTION2 WHILE TRYING TO PRINT TO FILE: {}'.format(e))
        return


# see https://stackoverflow.com/questions/5309978/sprintf-like-functionality-in-python
def jrSprintf(*args, **kwargs):
    sio = io.StringIO()
    print(*args, **kwargs, file=sio)
    return sio.getvalue()


def getJrPrintErrorCount():
    global moduleErrorPrintCount
    return moduleErrorPrintCount


def jrException(msg):
    textLine = 'EXCEPTION: ' + msg
    jrprint(textLine)
     
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def addSuffixForNumber(numberString):
    # see https://stackoverflow.com/questions/9647202/ordinal-numbers-replacement
    # add suffix for number
    n = int(numberString)
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(numberString) + suffix


def addSuffixForNumberedStreetAves(address):
    addressOrig = address
    #address = re.sub(r'\b([\d]+)[\s]+(street|st\.|st)\b', lambda m: addSuffixForNumber(m[1])+' '+m[2], address, flags=re.IGNORECASE)

    address = re.sub(r'(\b)([\d]+)[\s]+(street|st\.|st)(\b)(.*&)', lambda m: m[1]+addSuffixForNumber(m[2])+' '+m[3]+m[4]+m[5], address, flags=re.IGNORECASE)
    address = re.sub(r'([a-zA-Z0-9]+\b\s*)([\d]+)[\s]+(street|st\.|st)(\b)', lambda m: m[1]+addSuffixForNumber(m[2])+' '+m[3]+m[4], address, flags=re.IGNORECASE)


    #address = re.sub(r'\b([\d]+)[\s]+(avenue|ave\.|ave)\b', lambda m: addSuffixForNumber(m[1])+' '+m[2], address, flags=re.IGNORECASE)
    #address = re.sub(r'(\b)([\d]+)[\s]+(avenue|ave\.|ave)(\b)', lambda m: m[1]+addSuffixForNumber(m[2])+' '+m[3]+m[4]+m[5], address, flags=re.IGNORECASE)

    address = re.sub(r'(\b)([\d]+)[\s]+(avenue|ave\.|ave)(\b)(.*&)', lambda m: m[1]+addSuffixForNumber(m[2])+' '+m[3]+m[4]+m[5], address, flags=re.IGNORECASE)
    address = re.sub(r'([a-zA-Z0-9]+\b\s*)([\d]+)[\s]+(avenue|ave\.|ave)(\b)', lambda m: m[1]+addSuffixForNumber(m[2])+' '+m[3]+m[4], address, flags=re.IGNORECASE)

#    if (address != addressOrig):
#        print('addSuffixForNumberedStreetAves changed {} to {}'.format(addressOrig,address))
    return address


def addDotAfterDirectionLetter(address):
    #addressNew = re.sub(r'(\b)(N|S|W|E)(\z|\s+|\,)', lambda m: m[1]+m[2]+'. '+m[3], address)
    addressNew = re.sub(r'(\b)(N|S|W|E)(\Z|\s+|\,)', lambda m: m[1]+m[2]+'. '+m[3], address)
    #print('{} vs {}'.format(address,addressNew))
    return addressNew
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
def truncateElipses(txt, maxlen):
    if (len(txt)<=maxlen):
        return txt
    txt = txt[0:maxlen-3] + '...'
    return txt
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def findListRowWithDictFieldValue(listOfDicts, varname, varval):
    for li in listOfDicts:
        if (li[varname]==varval):
            return li
    # not found
    return None
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def calcTimestampForData():
    return time.time()
def calcTimestampForDataZero():
    return 0
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
def calcFileListInFolder(baseDir, fileExtension):
    # make a lst of all files in filePath matching mask
    # each item should be dict with 'name' and 'path' keys
    flist = []
    for fileName in os.listdir(baseDir):
        if (fileExtension is None) or (fileName.endswith(fileExtension)):
            filePath = os.path.join(baseDir, fileName)
            flist.append({'name': fileName, 'path': filePath})
    return flist
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def makeBakFilePath(filePath, flagAddDate):
    filePathBak = filePath
    if (flagAddDate):
        bakSuffix = '_bak' + time.strftime('%Y%m%d_%H%M%S')
    else:
        bakSuffix = '_bak'
    filePathBak = re.sub(r'\.([^\.]*)$', bakSuffix+r'.\1', filePathBak)
    if (filePathBak == filePath):
        filePathBak += bakSuffix
    return filePathBak
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def addSeparatedItemToText(text, newpart, sep):
    if (newpart=='') or (newpart is None):
        return text
    if (text==''):
        return newpart
    return text + sep + ' ' + newpart
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def dictsDifferAtKey(d1,d2, key):
    ind1 = key in d1
    ind2 = key in d2
    if (ind1 != ind2):
        return True
    if (d1[key] != d2[key]):
        return True
    return False
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def fixExtraNewlinesInLists(text):
    text = re.sub(r'\r?\n\s*\r?\n\s*(\d+)',r'\n\1', text)
    return text
# ---------------------------------------------------------------------------





















# ---------------------------------------------------------------------------
LATIN_1_CHARS = (
    ('\xe2\x80\x99', "'"),
    ('\xc3\xa9', 'e'),
    ('\xe2\x80\x90', '-'),
    ('\xe2\x80\x91', '-'),
    ('\xe2\x80\x92', '-'),
    ('\xe2\x80\x93', '-'),
    ('\xe2\x80\x94', '-'),
    ('\xe2\x80\x94', '-'),
    ('\xe2\x80\x98', "'"),
    ('\xe2\x80\x9b', "'"),
    ('\xe2\x80\x9c', '"'),
    ('\xe2\x80\x9c', '"'),
    ('\xe2\x80\x9d', '"'),
    ('\xe2\x80\x9e', '"'),
    ('\xe2\x80\x9f', '"'),
    ('\xe2\x80\xa6', '...'),
    ('\xe2\x80\xb2', "'"),
    ('\xe2\x80\xb3', "'"),
    ('\xe2\x80\xb4', "'"),
    ('\xe2\x80\xb5', "'"),
    ('\xe2\x80\xb6', "'"),
    ('\xe2\x80\xb7', "'"),
    ('\xe2\x81\xba', "+"),
    ('\xe2\x81\xbb', "-"),
    ('\xe2\x81\xbc', "="),
    ('\xe2\x81\xbd', "("),
    ('\xe2\x81\xbe', ")")
)


def clean_latin1(data):
    try:
        return data.encode('utf-8')
    except UnicodeDecodeError:
        data = data.decode('iso-8859-1')
        for _hex, _char in LATIN_1_CHARS:
            data = data.replace(_hex, _char)
        return data.encode('utf8')

def unicodetoascii(text):

    TEXT = (text.
    		replace('\\xe2\\x80\\x99', "'").
            replace('\\xc3\\xa9', 'e').
            replace('\\xe2\\x80\\x90', '-').
            replace('\\xe2\\x80\\x91', '-').
            replace('\\xe2\\x80\\x92', '-').
            replace('\\xe2\\x80\\x93', '-').
            replace('\\xe2\\x80\\x94', '-').
            replace('\\xe2\\x80\\x94', '-').
            replace('\\xe2\\x80\\x98', "'").
            replace('\\xe2\\x80\\x9b', "'").
            replace('\\xe2\\x80\\x9c', '"').
            replace('\\xe2\\x80\\x9c', '"').
            replace('\\xe2\\x80\\x9d', '"').
            replace('\\xe2\\x80\\x9e', '"').
            replace('\\xe2\\x80\\x9f', '"').
            replace('\\xe2\\x80\\xa6', '...').#
            replace('\\xe2\\x80\\xb2', "'").
            replace('\\xe2\\x80\\xb3', "'").
            replace('\\xe2\\x80\\xb4', "'").
            replace('\\xe2\\x80\\xb5', "'").
            replace('\\xe2\\x80\\xb6', "'").
            replace('\\xe2\\x80\\xb7', "'").
            replace('\\xe2\\x81\\xba', "+").
            replace('\\xe2\\x81\\xbb', "-").
            replace('\\xe2\\x81\\xbc', "=").
            replace('\\xe2\\x81\\xbd', "(").
            replace('\\xe2\\x81\\xbe', ")")

                 )
    return TEXT


def killEverythingAndEveryoneThatHadAnythingToDoWithUtfThenCommitSuicide(text):
    # i swear to go if i could kill myself to escape this utf8 hell i would
    #text = text.replace('\x92', "'")
    #text = text.replace('\x96', "-")
    #text = text.replace('\x93', '"')
    #text = text.replace('\x94', '"')

    text = text.replace(r"´", "'")
    text = text.replace(r"–", "-")  
    
    return text



# see https://gist.github.com/tushortz/9fbde5d023c0a0204333267840b592f9
def fixFuckedTextForHtml(text):
    # this is so fucking stupid
    # annoying chatgpt

    text = killEverythingAndEveryoneThatHadAnythingToDoWithUtfThenCommitSuicide(text)

    return text

    if ('la carte" dining' in text) or ('18 miles of books' in text):
        print('PLEASE KILL ME')

    return text


    #textU = text.encode('utf-8')
    #textA = textU.decode('windows-1252', 'ignore').encode('latin-1', 'ignore').decode('latin-1', 'ignore')

    return textA

    text = text.replace("`","'")
    text = text.replace("–","-")
    text = text.replace("â","-")
    text = text.replace("’","'")

    #text = html.escape(text)
    return text
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
def htmlIfyBlockOfText(txt):
    # add <p> parts and use ol ul and li

    lines = txt.split('\n')
    htmlText = ''
    inList = False
    hasContent = False
    continuationListLine = ''
    for line in lines:
        # see if this is a #.  list item

        if (inList):
            matches = re.match(r'^\s\s\s\s*(.*)\s*$', line)            
            if (matches is not None):
                # this is a continuation line
                line = matches[1]
                line = line.strip()
                if (continuationListLine==''):
                    continuationListLine = line
                else:
                    if (':' in continuationListLine):
                        continuationListLine += ('<br/>' + line)
                    else:
                        continuationListLine += (':<br/>' + line)
                # skip below and check next line
                continue

        line = line.strip()
        if (line==''):
            # skip blank lines
            if (inList) or (True):
                continue

        # its not a continuation list line, so its either a new list line or a NON list line
        if (True):
            if (continuationListLine!=''):
                # we need to close last line before we move along
                htmlText += '<li>' + continuationListLine + '</li>\n'
                continuationListLine = ''
                hasContent = True
            # check if its a new list line or normal line
            matches = re.match(r'^(\d+)\.\s*(.*)\s*', line)
            if (matches is None):
                # normal line, so close list if in one
                if (inList):
                    htmlText += '</ol>\n'
                inList = False
            else:
                # yes, so start list if not in one
                if (not inList):
                    htmlText += '<ol>\n'
                    inList = True
                line = matches[2]
        #
        if (inList):
            # we might continue multiple lines in this li so dont add it yet
            continuationListLine = line
        else:
            if (isGptLineANote(line)):
                htmlText += '<p><i>' + line + '</i></p>\n'
            else:
                htmlText += '<p>' + line + '</p>\n'                
                hasContent = True
    # finish list if we left off i one
    if (continuationListLine!=''):
        # we need to close last line
        htmlText += '<li>' + continuationListLine + '</li>\n'
        hasContent = True
        continuationListLine = ''
    if (inList):
        htmlText += '</ol>\n'
    # wrap everything in div?
    htmlText = '<div>' + htmlText + '</div>'

    htmlText = fixFuckedTextForHtml(htmlText)
      
    return [htmlText, hasContent]


def isGptLineANote(line):
    if (line.startswith('Please note')):
        return True
    if (line.startswith('Unfortunately')):
        return True
    if (line.startswith('I\'m sorry')):
        return True
    if (line.startswith('Sorry for')):
        return True
    if (line.startswith('Sorry')):
        return True
    if (line.startswith('Please')):
        return True
    #if (line.startswith('While ')):
    #    return True
    if (line.startswith('It was challenging ')):
        return True                    
    if ('Please note' in line):
        return True
    if ('Please keep in mind' in line):
        return True
    if ('Please consult' in line):
        return True
    if (line.startswith('As an AI')):
        return True
    if (line.startswith('(Kindly note')):
        return True
    if (line.startswith('(Note:')):
        return True
    return False
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def changeDisplayNameToFirstNameInitialOnly(displayName):
    displayName = re.sub(r'^(.*,\s*)([^,])([^,]+)$',r'\1\2.', displayName)
    return displayName
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
def sortDictByKeys(mydict):
    myKeys = list(mydict.keys())
    myKeys.sort()
    dictSorted = {i: mydict[i] for i in myKeys}
    return dictSorted


def sortDictByAKeyVal(mydict, keyName):
    myKeys = list(mydict.keys())
    # sort by value of keyName
    myKeys.sort(key=lambda keyval: mydict[keyval][keyName])
    dictSorted = {i: mydict[i] for i in myKeys}
    return dictSorted


def sortDictByASecondaryKeyVal(mydict, firstKey, keyName):
    myKeys = list(mydict.keys())
    # sort by value of keyName
    myKeys.sort(key=lambda keyval: mydict[keyval][firstKey][keyName])
    dictSorted = {i: mydict[i] for i in myKeys}
    return dictSorted
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
def removeBlankKeys(mydict):
    delKeys = []
    for k,v in mydict.items():
        if (v is None) or (v==''):
            delKeys.append(k)
    for k in delKeys:
        del mydict[k]
    return mydict
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def movePrefixesLikeTheToFront(text):
    text = text.strip()
    matches = re.match(r'^(.+)\s*,\s*([a-zA-Z\.]+)$', text)
    if (matches is not None):
        p1 = matches[1]
        p2 = matches[2]
        p2Lower = p2.lower()
        if (p2Lower != 'etc.'):
            text = p2 + ' ' + p1
            text = text.strip()
    return text
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# see https://stackoverflow.com/questions/57503080/how-to-convert-elapsed-time-string-to-seconds-in-python
def niceElapsedTimeStr(tf):
    if tf < 60:
        return('{:.1f} seconds'.format(tf))
    elif 60 <= tf < 3600:
        mm = math.floor(tf/60)
        ss = tf - (60*mm)
        if (ss>30):
            return("{} minute{}, and {} seconds".format(mm, plurals(mm,"s"), int(ss)))
        return("{} minute{}".format(mm,plurals(mm,"s")))
    elif 3600 <= tf < 86400:
        hh = math.floor(tf/3600)
        mm = math.floor((tf-(hh*3600))/60)
        ss = tf - (hh*3600) - (60*mm)
        #return("{} hours, {} minute(s), and {} seconds".format(hh, mm, ss))
        if (mm>0):
            return("{} hour{}, {} minute{}".format(hh, plurals(hh,"s"), mm,plurals(mm,"s")))
        else:
            return("{} hour{}".format(hh, plurals(hh,"s")))
    elif tf >= 86400:
        dd = math.floor(tf/86400)
        hh = math.floor((tf-(dd*86400))/3600)
        mm = math.floor((tf-(dd*86400)-(hh*3600))/60)
        ss = tf - (86400*dd) - (hh*3600) - (60*mm)
        #return("{} days, {} hours, {} minute(s), and {} seconds".format(dd, hh, mm, ss))
        if (hh>0):
            return("{} day{}, and {} hour{}".format(dd, plurals(dd,"s"), hh, plurals(hh,"s") ))
        else:
            return("{} day{}".format(dd, plurals(dd,"s")))



def niceElapsedTimeStrMinsSecs(elapsedSecs):
    if (elapsedSecs<60):
        return '{:.1f} seconds'.format(elapsedSecs)
    return '{:.1f} minutes'.format(elapsedSecs/60)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def escapedCharacterConvert(charc):
    if (charc=='n'):
        return '\n'
    # ATTN: unfinished
    return charc
# ---------------------------------------------------------------------------
    


# ---------------------------------------------------------------------------   
def getNiceCurrentDateTime():
    return getNiceDateTime(datetime.datetime.now())

def getNiceDateTime(dt):
    return dt.strftime('%A, %B %d at %I:%M %p')

def getNiceDateTimeCompact(dt):
    #return dt.strftime('%a, %b %d at %#I:%M %p')
    return dt.strftime('%a, %b %d at %I:%M %p')


def getNiceCurrentDate():
    dt = datetime.datetime.now()
    return dt.strftime('%A, %B %d')


def hourAmPm(hour):
    if (hour==12):
        return "12 noon"
    elif (hour==0):
        return "12 midnight"
    elif (hour>12):
        return "{} pm".format(hour-12)
    else:
        return "{} am".format(hour)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
def plurals(amount, ifMoreThanOneText):
    amount = int(amount)
    if (amount==1):
        return ''
    else:
        return ifMoreThanOneText


def singularPlurals(amount, singularText, pluralText):
    amount = int(amount)
    if (amount==1):
        return singularText
    else:
        return pluralText


def alternateText(flagFirst, firstText, secondText):
    if (flagFirst):
        return firstText
    else:
        return secondText
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def makeNiceCommaAndOrList(strList, lastWord):
    listLen = len(strList)
    if (listLen==1):
        return strList[0]
    elif (listLen==2):
        return strList[0] + ' ' + lastWord + ' ' + strList[1]
    # longer
    listFront = strList[0:listLen-1]
    text = ', '.join(listFront)
    text += ', ' + lastWord + ' ' + strList[listLen-1]
    return text
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def uppercaseFirstLetter(text):
    text = text[0].upper() + text[1:]
    return text
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
def semiMatchStringsNoPunctuation(dname1, dname2):
    dname1 = dname1.lower()
    dname2 = dname2.lower()
    dname1 = ''.join(e for e in dname1 if e.isalnum())
    dname2 = ''.join(e for e in dname2 if e.isalnum())
    if (dname1 == '') or (dname2==''):
        return (dname1 == dname2)
    if (dname1 in dname2) or (dname2 in dname1):
        return True
    return False
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
def fixupUtfQuotesEtc(text):
    text = text.replace("\r\n","\n")
    text = text.replace("\r","\n")
    text = text.replace('“', '"')
    text = text.replace('”', '"')
    return text
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
def makeZipFile(generatedFileList, saveDir, fileBaseName):
    saveDir = canonicalFilePath(saveDir)
    outFilePath = '{}/{}.zip'.format(saveDir, fileBaseName)
    deleteFilePathIfExists(outFilePath)
    with zipfile.ZipFile(outFilePath, 'w') as zip:        
        for filePath in generatedFileList:
            filePath = canonicalFilePath(filePath)
            filePathRelative = filePath
            if (filePathRelative.startswith(saveDir)):
                filePathRelative = filePathRelative[len(saveDir):]
            else:
                filePathRelative = os.path.basename(filePath)
            zip.write(filePath, compress_type=zipfile.ZIP_DEFLATED, arcname=filePathRelative)
    return  outFilePath


def zipFileList(fileList, outputPath, baseFilename, optionAddDateToZipFileName, optionDebug):
    # special zip instruction
    optionZipSuffix = ""
    if (optionAddDateToZipFileName):
        nowTime = datetime.datetime.now()
        optionZipSuffix += nowTime.strftime('_%Y%m%d')
    if (len(fileList)>0):
        zipFilePath = makeZipFile(fileList, outputPath, baseFilename + optionZipSuffix)
        if (optionDebug):
            jrprint("Zipped {} files to '{}'.".format(len(fileList), zipFilePath))
        return [True, zipFilePath]
    return [False, None]

# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# see https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
def niceFileSizeStr(byteCount):
    size = byteCount
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0
    return byteCount


def niceFileSizeStrRound(byteCount):
    size = byteCount
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%d %s" % (round(size), x)
        size /= 1024.0
    return byteCount
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# see https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
def niceLargeNumberStr(byteCount):
    size = byteCount
    for x in ['', 'k']:
        if size < 1024.0:
            return "%3.1f%s" % (size, x)
        size /= 1024.0
    return byteCount


def niceLargeNumberStrRound(byteCount):
    size = byteCount
    for x in ['', 'k']:
        if size < 1024.0:
            return "%d%s" % (round(size), x)
        size /= 1024.0
    return byteCount
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def replaceInitialDirectoryPath(fullPath, initialPath):
    relPath = fullPath.replace(initialPath,'')
    startpos = 0
    while (len(relPath)>startpos) and (relPath[startpos] in ['/', '\\']):
        startpos += 1
    if (startpos>0):
        relPath = relPath[startpos:]
    return relPath


def canonicalFilePath(filePath):
    filePath = filePath.replace('\\','/')
    filePath = filePath.replace('\\\\','/')
    return filePath


def safeCharsForFilename(str):
    def safe_char(c):
        if c.isalnum():
            return c
        elif c in '.':
            return 'p'
        else:
            return "_"
    return "".join(safe_char(c) for c in str).rstrip("_")
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
def exceptionPlusSimpleTraceback(e, contextStr):
    # see https://docs.python.org/3/library/traceback.html
    #tracebackText = traceback.format_exc(e)
    tracebackLines = traceback.format_exception(e)
    #tracebackLines = traceback.format_exception(e, limit = 2)
    tracebackText = "\n".join(tracebackLines)
    msg = "ERROR, exception while {}: {}. Traceback: {}".format(contextStr, repr(e), tracebackText)
    return msg
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# handling unicode/binary logs etc
def jrSafeDecodeCharSet(text, charSet):
    try:
        return text.decode(charSet)
    except:
        return text
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def createSisterFilePath(filePath, fileName):
    directoryPath = os.path.dirname(filePath)
    filePath = directoryPath + "/" + fileName
    return filePath

def createSisterFileName(filePath, fileSuffix):
    directoryPath = os.path.dirname(filePath)
    fileBaseName = os.path.splitext(os.path.basename(filePath))[0]
    filePath = directoryPath + "/" + fileBaseName + fileSuffix
    return filePath
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def stringOrNone(val):
    if (val is None):
        return "None"
    return val
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def isNonEmptyString(val):
    return (val is not None) and (val!="")
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
# see https://stackoverflow.com/questions/379906/how-do-i-parse-a-string-to-a-float-or-int
def intOrFloatFromStr(v):
    number_as_float = float(v)
    number_as_int = int(number_as_float)
    return number_as_int if number_as_float == number_as_int else number_as_float

def boolFromStr(v):
    v = v.lower()
    if (v=="true"):
        return True
    if (v=="false"):
        return False
    return None
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
def replaceFromDict(text, repDict):
    for key, val in repDict.items():
        text = text.replace(key, val)
    return text
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
def calcTextPositionStyle(text):
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


def modifyTextToSuitTextPositionStyle(text, textPositionStyle, linestartPrefix, flagPeriodIfStandalone):
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
    #
    return text
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def minutesToTimeString(minutes):
    if (minutes is None):
        minutes = 0
    text = niceElapsedTimeStr(minutes*60)
    return text
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
class JrPerfTimer():
    def __init__(self, label, flagAnnounce):
        self.start_time = time.perf_counter()
        self.label = label
        if (flagAnnounce):
            jrprint("Starting run of {}..".format(self.label))
    def printElapsedTime(self):
        fullMsg = self.getElapsedTimeMessage()
        jrprint(fullMsg)
    def getElapsedTimeMessage(self):
        end_time = time.perf_counter()
        elapsed_time = end_time - self.start_time
        return "Finished running " + self.label + ": " + niceElapsedTimeStr(elapsed_time)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
def changeFileExtension(filePath, newExtension):
    if (not newExtension.startswith(".")):
        newExtension = "." + newExtension
    newPath = Path(Path(filePath).with_suffix("").as_posix() + newExtension)
    return str(newPath)
# ---------------------------------------------------------------------------





#import json
# ---------------------------------------------------------------------------
def dictToHtmlPre(data):
    """Formats a dictionary as HTML preformatted text."""
    import pprint
    html = "<pre>" + pprint.pformat(data) + "</pre>"
    #html = html.replace("\n","<br/>\n")
    return html
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def smartSplitTextForDropCaps(text):
    # return [firstChar, upperCaseText, remainder]
    if (len(text)==0):
        return None
    firstChar = text[0]
    # find first punctuation
    stopChars = [".",",",'"', "“", ":"]
    textlen = len(text)
    stopIndex = None
    for i in range(1,textlen):
        c = text[i]
        if (c in stopChars):
            stopIndex = i
            break
    if (stopIndex is None):
        return [firstChar, "", text[1:]]
    upperCaseText = text[1:stopIndex]
    remainderText = text[stopIndex:]
    return [firstChar, upperCaseText, remainderText]
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def quoteStringsForDisplay(val):
    if (isinstance(val,str)):
        return '"' + val + '"'
    return val
# ---------------------------------------------------------------------------
