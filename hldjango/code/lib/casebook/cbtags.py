# support classes and functions for working with tags/documents/etc

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
from .jriexception import *


# defines
DefTagTypes = ["doc", "cond", "check", "day", "trophy", "decoy"]
DefBackOfBookDocLocationString = "at the back of this case book"


class CbTagManager:
    def __init__(self):
        self.tags = {}
        self.documentNumberIndex = 0
        #
        self.tagLetterLabelsAvailable = []
        self.tagLetterStage = 0

    def getTagDict(self):
        return self.tags

    def getTagList(self):
        return self.tags.values()

    def getDefaultLocation(self, env):
        defaultLocation = env.getEnvValueUnwrapped(None, "documentData.defaultLocation", "back")
        return defaultLocation

    def findOrDeclareTag(self, env, id, deadline, label, tagLocation, tagObfuscatedLabel, sloc, debugComment, leadp):
        tag = self.findTagById(id)
        if (tag is not None):
            return tag
        tag = self.declareTag(env, id, deadline, label, tagLocation, tagObfuscatedLabel, True, sloc, debugComment, leadp)
        return tag

    def findTagById(self, id):
        if (id in self.tags):
            return self.tags[id]
        return None

    def declareTag(self, env, id, deadline, label, tagLocation, tagObfuscatedLabel, flagErrorIfExists, sloc, debugComment, leadp):
        tag = self.findTagById(id)
        if (tag is not None):
            if (flagErrorIfExists):
                raise makeJriException("Tag declaration when tag ({}) already exists".format(id), sloc)
            return tag
        if (tagLocation is not None):
            location = tagLocation
        else:
            location = self.getDefaultLocation(env)
        # parse tag to extract tag type and properid
        [tagType, tagProperId, obfuscatedLabel, isCustomObfuscatedLabel, documentNumber] = self.parseDeclareTag(id, sloc, tagObfuscatedLabel)
        # create tag
        tag = CbTagItem(id, deadline, label, tagType, obfuscatedLabel, isCustomObfuscatedLabel, location, documentNumber)
        self.tags[id] = tag
        # add debug line
        tag.addDebugUseLine(debugComment, sloc, leadp)
        # return tag
        return tag



    def parseDeclareTag(self, id, sloc, tagObfuscatedLabel):
        # all tags must be of the form PREFIX.PROPERID
        # where prefix is the tag "type" from a set list
        documentNumber = None
        parts = id.split(".", 1)
        if (len(parts)!=2):
            msg = ("Tag id should be of the form PREFIX.ID where PREFIX is one of {}".format(DefTagTypes))
            raise makeJriException(msg, sloc)
        tagType = parts[0]
        tagProperId = parts[1]
        if (not tagType in DefTagTypes):
            msg = ("Tag id prefix not understood; PREFIX.ID should have PREFIX one of {}".format(DefTagTypes))
            raise makeJriException(msg, sloc)
        # obfuscate label
        if (tagObfuscatedLabel is not None):
            obfuscatedLabel = tagObfuscatedLabel
            isCustomObfuscatedLabel = True
        else:
            [obfuscatedLabel,documentNumber]  = self.obfuscateId(tagProperId, tagType, sloc)
            isCustomObfuscatedLabel = False

        # return tuple
        return [tagType, tagProperId, obfuscatedLabel, isCustomObfuscatedLabel, documentNumber]


    def obfuscateId(self, tagProperId, tagType, sloc):
        # create an obfuscated label
        if (tagType == "doc"):
            # documents are numbered
            self.documentNumberIndex += 1
            obfuscatedLabel = "{}".format(self.documentNumberIndex)
            documentNumber = self.documentNumberIndex
        elif (tagType in ["cond", "check", "trophy"]):
            # these get letters
            obfuscatedMarkerLetter = self.obfuscateIdAsLetterTag(tagProperId, tagType, sloc)
            obfuscatedLabel = "{}".format(obfuscatedMarkerLetter)
            documentNumber = None
        else:
            msg = ("Internal error; tagType ({}) not understood; should be from {}".format(tagType, DefTagTypes))
            raise makeJriException(msg, sloc)
        # return it
        return [obfuscatedLabel, documentNumber]


    def obfuscateIdAsLetterTag(self, tagProperId, tagType, sloc):
        if (len(tagProperId)==0):
            raise makeJriException("Tag cannot be blank after prefix.", sloc)
        if (len(self.tagLetterLabelsAvailable)==0):
            # refresh it
            self.tagLetterStage += 1
            if (self.tagLetterStage == 1):
                suffix = ''
            else:
                suffix = str(self.tagLetterStage)
            self.tagLetterLabelsAvailable = list([item+suffix for item in 'ABCDEFGHJKLMNOPQRSTUVWXYZ'])
        #
        firstLetter = tagProperId[0].upper()
        if (firstLetter in self.tagLetterLabelsAvailable):
            letterLabel = firstLetter
        else:
            # find nearest one HIGHER than it (wrapping around if needed)
            letterLabel = None
            for c in self.tagLetterLabelsAvailable:
                if (c>firstLetter):
                    # got it
                    letterLabel = c
                    break
            if (letterLabel is None):
                # we warp around
                letterLabel = self.tagLetterLabelsAvailable[0]
        #        
        self.tagLetterLabelsAvailable.remove(letterLabel)
        #return "Marker {}".format(letterLabel)
        return letterLabel


    def findDeadlineTags(self, dayNumber):
        tagList = []
        for key, tag in self.tags.items():
            deadline = tag.getDeadline()
            if (deadline == dayNumber):
                tagList.append(tag)
        return tagList


    def sortByTypeAndObfuscatedLabel(self, tagList):
        tagListSorted = sorted(tagList, key=lambda tag: self.sortKeyTagByClassAndObfuscatedLabel(tag))
        return tagListSorted
    
    def sortKeyTagByClassAndObfuscatedLabel(self, tag):
        keyString = tag.getTagTypeClassSortVal() + "_" + tag.getObfuscatedLabel()
        return keyString


    def findHintLeadForTag(self, env, renderdoc, tag):
        # look for a lead which is the hint for this tag
        leadList = renderdoc.calcFlatLeadList()
        for lead in leadList:
            role = lead.getRole()
            if (role is None):
                continue
            roleType = role["type"]
            if (roleType=="hint"):
                if ("tag" in role):
                    if (role["tag"]==tag):
                        return lead
        return None


#---------------------------------------------------------------------------












class CbTagItem:
    def __init__(self, id, deadline, label, tagType, obfuscatedLabel, isCustomObfuscatedLabel, location, documentNumber):
        self.id = id
        self.deadline = deadline
        self.label = label
        self.tagType = tagType
        self.setObfuscatedLabel(obfuscatedLabel, isCustomObfuscatedLabel)
        self.location = location
        self.debugUse = []
        self.gainLeads = []
        self.checkLeads = []
        self.documentNumber = documentNumber

    
    def addDebugUseLine(self, debugComment, sloc, leadp):
        debugEntryDict = {"comment": debugComment, "sloc": sloc, "lead": leadp}
        self.debugUse.append(debugEntryDict)

    def getDeadline(self):
        return self.deadline
    def getId(self):
        return self.id
    def getLabel(self):
        return self.label
    def getObfuscatedLabel(self):
        return self.obfuscatedLabel
    def setObfuscatedLabel(self, val, flagIsCustom):
        self.obfuscatedLabel = val
        self.customObfuscatedLabel = flagIsCustom
    def getIsCustomObfuscatedLabel(self):
        return self.customObfuscatedLabel
    
    def getIsTagTypeDoc(self):
        return (self.tagType == "doc")

    def getDocumentNumber(self):
        return self.documentNumber
    def setDocumentNumber(self, val):
        self.documentNumber = val
    
    def getLocation(self):
        return self.location
    def getNiceLocationString(self):
        location = self.location
        if (location=="back"):
            location = DefBackOfBookDocLocationString
        return location

    def getNiceIdWithLabel(self):
        label = self.id
        if (self.label is not None) and (self.label!=""):
            #label += " ("+self.label+")"
            label += " "+self.label
        return label

    def getMindMapNodeInfo(self):
        label = self.id
        if (self.label is not None) and (self.label!=""):
            #label += "("+self.label+")"
            label += "\n"+self.label
        if (label is None) or (label==""):
            label = self.tagType
        label += "\n(" + self.getNiceObfuscatedLabelWithType(False, False) + ")"
        label = label
        #
        mmInfo = {
            "id": "TAG.{}".format(self.id),
            "label": label,
            "type": "tag",
            "subtype": self.tagType,
            "pointer": self,
            "mStyle": None,
            }
        return mmInfo


    def getNiceObfuscatedLabelWithType(self, flagBoldMarkdown, reportMode):
        if (self.getIsCustomObfuscatedLabel()):
            classNamePlus = ""
        else:
            classNamePlus = jrfuncs.uppercaseFirstLetter(self.getTagTypeClass()) + " "
        label = jrfuncs.uppercaseFirstLetter(self.obfuscatedLabel)
        if (self.tagType == "doc"):
            pass
        else:
            #label = "[" + label + "]"
            pass
        if (reportMode):
            label += " [{}]".format(self.getId())
        if (flagBoldMarkdown):
            return "**" + classNamePlus + label + "**"
        return classNamePlus + label
    
    
    def getNiceGainedObfuscatedLabelWithType(self, flagBoldMarkdown, reportMode, optionIsGaining):
        if (self.getIsCustomObfuscatedLabel()):
            classNamePlus = ""
        else:
            classNamePlus = jrfuncs.uppercaseFirstLetter(self.getTagTypeClass()) + " "
        label = jrfuncs.uppercaseFirstLetter(self.obfuscatedLabel)
        if (self.tagType == "doc"):
            if (optionIsGaining):
                gainPlusString = "gained access to "
            else:
                gainPlusString = "previously acquired access to "
            revealedLabel = self.getLabel()
            # only show revealed label AFTER they have gained it if its custom label, in order to keep it a surprise
            if (revealedLabel is not None) and (revealedLabel!="") and (not optionIsGaining or (not self.getIsCustomObfuscatedLabel())):
                label += " ({})".format(revealedLabel)
        else:
            if (optionIsGaining):
                gainPlusString = "gained "
            else:
                gainPlusString = "previously acquired "
        if (reportMode):
            label += " [{}]".format(self.getId())
        if (flagBoldMarkdown):
            return gainPlusString + "**" + classNamePlus + label + "**"
        return gainPlusString + classNamePlus + label


    def getInstructionText(self):
        if (self.tagType == "doc"):
            #retv = "please note this in your case log (unless you have gained access previously)"  
            retv = "please note this in your case log"  
        else:
            #retv = "please circle this marker in your case log (unless you have gained access previously)"
            retv = "please note this in your case log"
        return retv

    def getWhereText(self):
        if (self.tagType == "doc"):
            niceLocation = self.getNiceLocationString()
            if (niceLocation!=""):
                retv = ", which can be found {}".format(niceLocation)
            else:
                # no location
                retv = ""
        else:
            #retv = "please circle this marker in your case log (unless you have gained access previously)"
            retv = ""
        return retv


    def getSymbol(self):
        if (self.tagType == "doc"):
            retv = "markerDoc"  
        else:
            retv = "markerTag"
        return retv

    def getTagType(self):
        return self.tagType
    def getTagTypeClass(self):
        if (self.tagType=="doc"):
            return "document"
        else:
            return "marker"
    def getTagTypeClassSortVal(self):
        if (self.tagType=="doc"):
            return "Z_Document"
        else:
            return "A_Marker"



    def recordGain(self, env, keyword, sloc, leadp):
        # add debug line
        self.addDebugUseLine("Tag gained", sloc, leadp)
        # add gain list
        self.gainLeads.append(leadp)
        # mindmapper
        mindManager = env.getMindManager()
        mindManager.addLinkBetweenNodes(env, keyword, None, leadp, self)


    def recordCheck(self, env, keyword, sloc, leadp):
        # add debug line
        self.addDebugUseLine("Tag checked", sloc, leadp)
        # add gain list
        self.checkLeads.append(leadp)
        # mindmapper
        mindManager = env.getMindManager()
        mindManager.addLinkBetweenNodes(env, keyword, None, leadp, self)


    def getGainList(self):
        return self.gainLeads
    def getCheckList(self):
        return self.checkLeads












class CbCheckboxManager:
    def __init__(self):
        self.checkTypes = {}

    def recordCheckMarks(self, env, astloc, leadp, markType, markCount):
        if (markType not in self.checkTypes):
            self.checkTypes[markType] = CbCheckBoxItem(markType)
        self.checkTypes[markType].recordUse(env, astloc, leadp, markCount)
    
    def getCheckmarks(self):
        return self.checkTypes


class CbCheckBoxItem:
    def __init__(self, markType):
        self.markTypeName = markType
        self.uses = []

    def recordUse(self, env, astloc, leadp, markCount):
        useDict = {"lead": leadp, "count": markCount}
        self.uses.append(useDict)
    
    def getUses(self):
        return self.uses
    
    def getTypeName(self):
        return self.markTypeName
