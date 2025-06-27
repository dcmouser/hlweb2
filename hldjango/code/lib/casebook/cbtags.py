# support classes and functions for working with tags/documents/etc

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
from .jriexception import *
from .cbfuncs_core_support import parseTagListArg


from .cbfuncs_core_support import calcMarkerActionDict

# translation
from .cblocale import _

# python modules
import math
import random


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
        self.didPostProcess = False
        self.allTagLetters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
        self.obfuscatedIdPool = None
        self.obfuscatedIdPoolNumberStages = 0

    def getTagDict(self):
        return self.tags

    def getTagList(self):
        return self.tags.values()

    def getDefaultLocation(self, env):
        defaultLocation = env.getEnvValueUnwrapped(None, "documentData.defaultLocation", "back")
        return defaultLocation

    def findOrDeclareTag(self, env, id, deadline, label, tagLocation, tagObfuscatedLabel, tagDependencyString, sloc, debugComment, leadp):
        tag = self.findTagById(id)
        if (tag is not None):
            return tag
        tag = self.declareTag(env, id, deadline, label, tagLocation, tagObfuscatedLabel, tagDependencyString, True, sloc, debugComment, leadp, False)
        return tag

    def findTagById(self, id):
        if (id in self.tags):
            return self.tags[id]
        return None

    def findTagByObfuscatedId(self, obfuscatedId):
        for tagId,tag in self.tags.items():
            tagObfuscatedId = tag.getObfuscatedLabel()
            if (obfuscatedId==tagObfuscatedId):
                return tag
        # not found
        return None


    def addTagToTags(self, id, tag):
        self.tags[id] = tag

    def declareTag(self, env, id, deadline, label, tagLocation, tagObfuscatedLabel, tagDependencyString, flagErrorIfExists, sloc, debugComment, leadp, optionLateAutoDeclare):
        tag = self.findTagById(id)
        if (tag is not None):
            if (flagErrorIfExists):
                raise makeJriException("Tag declaration when tag ({}) already exists".format(id), sloc)
            return tag
        if (tagLocation is None):
            tagLocation = self.getDefaultLocation(env)
        # parse tag to extract tag type and properid
        tag = self.parseDeclareCreateTag(id, sloc, env, tagObfuscatedLabel, tagDependencyString, tagLocation, deadline, label, optionLateAutoDeclare)

        # add debug line
        tag.addDebugUseLine(debugComment, sloc, leadp)
        # return tag
        return tag


    def autoDeclareTag(self, id, autoDeclarePrefix, deadline, label, tagLocation, tagObfuscatedLabel, tagDependencyString, env, sloc, leadp):
        # ensure it has a unique id
        if (id==""):
            id="auto"
        for num in range(1,999):
            constructedId = "{}.{}{}".format(autoDeclarePrefix, id, str(num))
            existingTag = self.findTagById(constructedId)
            if (existingTag is None):
                break

        debugComment = "auto declaring tag"
        tag = self.declareTag(env, constructedId, deadline, label, tagLocation, tagObfuscatedLabel, tagDependencyString, True, sloc, debugComment, leadp, True)
        #
        return tag



    def declareConcept(self, env, id, label, flagErrorIfExists, sloc, debugComment, leadp):
        tag = self.findTagById(id)
        if (tag is not None):
            if (flagErrorIfExists):
                raise makeJriException("Concept declaration when concept ({}) already exists".format(id), sloc)
            return tag
        # parse tag to extract tag type and properid
        tag = self.parseDeclareCreateConcept(id, sloc, label)

        # add debug line
        tag.addDebugUseLine(debugComment, sloc, leadp)
        # return tag
        return tag




















    def parseDeclareCreateTag(self, id, sloc, env, tagObfuscatedLabel, tagDependencyString, tagLocation, deadline, label, optionLateAutoDeclare):
        # all tags must be of the form PREFIX.PROPERID
        # where prefix is the tag "type" from a set list
        #
        parts = id.split(".", 1)
        if (len(parts)!=2):
            msg = ("Tag id should be of the form PREFIX.ID where PREFIX is one of {}".format(DefTagTypes))
            raise makeJriException(msg, sloc)
        tagType = parts[0]
        tagProperId = parts[1]
        if (not tagType in DefTagTypes):
            msg = ("Tag id prefix not understood; PREFIX.ID should have PREFIX one of {}".format(DefTagTypes))
            raise makeJriException(msg, sloc)

        # defaults
        documentNumber = None
        obfuscatedLabel = None
        isCustomObfuscatedLabel = False

        # obfuscate label
        if (tagObfuscatedLabel is not None):
            # explicitly set
            obfuscatedLabel = tagObfuscatedLabel
            isCustomObfuscatedLabel = True
            needsPostProcess = False
        else:
            # needs auto number / obfuscated id
            if (tagType == "doc"):
                # documents are numbered and have fixed label
                self.documentNumberIndex += 1
                obfuscatedLabel = "{}".format(self.documentNumberIndex)
                documentNumber = self.documentNumberIndex
                needsPostProcess = False
            elif (tagType in ["cond", "check", "trophy", "decoy"]):
                # will need to be assigned later, so we leave it BLANK (NONE) for now
                needsPostProcess = True
            else:
                msg = ("Internal error; tagType ({}) not understood; should be from {}".format(tagType, DefTagTypes))
                raise makeJriException(msg, sloc)

        # check dupe
        if (obfuscatedLabel is not None):
            existingTag = self.findTagByObfuscatedId(obfuscatedLabel)
            if (existingTag is not None):
                raise makeJriException("Error: Duplicate obfuscated label ({}) declared for marker.".format(obfuscatedLabel), sloc)

        # create tag
        tag = CbTagItem(id, deadline, label, tagType, tagLocation, documentNumber, needsPostProcess)
        tag.setObfuscatedLabel(obfuscatedLabel, isCustomObfuscatedLabel)

        # set tag dependencies for hints
        tag.setDependencyListString(tagDependencyString)

        if (self.didPostProcess):
            # we already did post processing of tags, so we need to assign pending obfuscated label now
            if (obfuscatedLabel is None):
                if (optionLateAutoDeclare):
                    tagData = env.getEnvValueUnwrapped(None, "tagData", None)
                    tagMode = tagData["mode"]
                    obfuscatedLabel = self.popObfuscatedTagLabel(env, tag, tagMode)
                    tag.setObfuscatedLabel(obfuscatedLabel, False)
                else:
                    raise makeJriException("Error: declareCreated a later marker ({}) with a pending obfuscated label, but we have already run post-processess.".format(id), sloc)


        # set it in our management
        self.addTagToTags(id, tag)

        return tag






    def parseDeclareCreateConcept(self, id, sloc, label):
        # all tags must be of the form PREFIX.PROPERID
        # where prefix is the tag "type" from a set list
        if (False):
            parts = id.split(".", 1)
            if (len(parts)!=2):
                msg = ("Concept id should be of the form PREFIX.ID where PREFIX is one of {}".format(DefTagTypes))
                raise makeJriException(msg, sloc)
            tagType = parts[0]
            tagProperId = parts[1]
        else:
            tagType = "concept"
            tagProperId = id

        # create tag
        tag = CbConceptItem(id, label, tagType)
        self.addTagToTags(id, tag)

        return tag



    def findDeadlineTags(self, dayNumber):
        tagList = []
        for key, tag in self.tags.items():
            deadline = tag.getDeadline()
            if (deadline == dayNumber):
                tagList.append(tag)
        return tagList



    def sortByTypeAndId(self, tagList):
        tagListSorted = sorted(tagList, key=lambda tag: self.sortKeyTagByClassAndId(tag))
        return tagListSorted

    def sortByTypeAndObfuscatedLabel(self, tagList, env, flagForceSort):
        if (flagForceSort):
            optionSortLabels = True
        else:
            tagData = env.getEnvValueUnwrapped(None, "tagData", None)
            sortRequire = tagData["sortRequire"]
            if (sortRequire):
                optionSortLabels = True
            else:
                optionSortLabels = False
        #
        tagListSorted = sorted(tagList, key=lambda tag: self.sortKeyTagByClassAndObfuscatedLabel(tag, optionSortLabels))
        return tagListSorted
    
    def sortKeyTagByClassAndObfuscatedLabel(self, tag, optionSortLabels):
        if (optionSortLabels):
            keyString = tag.getTagTypeClassSortVal() + "_" + jrfuncs.zeroPadNumbersAnywhereInString(tag.getObfuscatedLabel(), 4)
        else:
            keyString = tag.getTagTypeClassSortVal()
        return keyString

    def sortKeyTagByClassAndId(self, tag):
        keyString = tag.getTagTypeClassSortVal() + "_" + jrfuncs.zeroPadNumbersAnywhereInString(tag.getId(),4)
        return keyString



    def findHintLeadForTag(self, env, renderdoc, intag):
        # look for a lead which is the hint for this tag
        leadList = renderdoc.calcFlatLeadList(True)
        for lead in leadList:
            role = lead.getRole()
            if (role is None):
                continue
            roleType = role["type"]
            if (roleType=="hint"):
                tag = jrfuncs.getDictValueOrDefault(role, "tag", None)
                if (intag==tag) and (intag is not None):
                    return lead
        return None


    def postProcessTagsIfNeeded(self, env):
        if (not self.didPostProcess):
            self.postProcessTags(env)





    def postProcessTags(self, env):
        # this is our new function designed to sort tags in the order they were defined and use a more consistent predictable system

        tagData = env.getEnvValueUnwrapped(None, "tagData", None)
        tagMode = tagData["mode"]

        # build out the initial pool
        self.buildInitialObfuscatedLabelPool(env)

        # assign obfuscated labels
        for tagId, tag in self.tags.items():
            if (not tag.getIsForwardFacingLetterTag()):
                # doesnt need a label
                continue
            if (tag.getIsCustomObfuscatedLabel()):
                # already has a label
                continue
            obfuscatedLabel = self.popObfuscatedTagLabel(env, tag, tagMode)
            tag.setObfuscatedLabel(obfuscatedLabel, False)

        # set flag saying we've sorted
        self.didPostProcess = True

        # let's do a sanity check also, by making sure no tags have same label
        self.checkForDuplicateTags()


    def buildInitialObfuscatedLabelPool(self, env):
        # figure out about how many lettered labels we are going to need  to choose from, so we know if we need A1,A2,B1,... or jsut A1,B1,...
        forwardFacingLetterTags = min(self.countForwardFacingLetterTags(),1)
        allTagLettersCount = len(self.allTagLetters)
        self.obfuscatedIdPoolNumberStages = math.ceil(forwardFacingLetterTags/allTagLettersCount)
        # clear pool and build initial pool
        self.obfuscatedIdPool = []
        self.addObfuscatedLabelPoolLabels(env, 1, self.obfuscatedIdPoolNumberStages)


    def addMoreToObfuscatedLabelPool(self, env):
        # we can add to an empty obfuscated letter pool after post-processing, if we need to, if we want to support late generation of obfuscated labels
        self.obfuscatedIdPoolNumberStages += 1
        self.addObfuscatedLabelPoolLabels(env, self.obfuscatedIdPoolNumberStages, self.obfuscatedIdPoolNumberStages)


    def addObfuscatedLabelPoolLabels(self, env, startnum, endnum):
        # does the work of building out the obfuscated label pool
        tagData = env.getEnvValueUnwrapped(None, "tagData", None)
        alwaysNumber = tagData["alwaysNumber"]
        consistentNumber = tagData["consistentNumber"]

        for letter in self.allTagLetters:
            for num in range(startnum, endnum+1):
                if (alwaysNumber) or (num>1) or (consistentNumber and self.obfuscatedIdPoolNumberStages>1):
                    numStr = str(num)
                else:
                    numStr = ""
                potentialObfuscatedId = "{}{}".format(letter, numStr)
                existingTag = self.findTagByObfuscatedId(potentialObfuscatedId)
                if (existingTag is not None):
                    # already exist
                    continue
                self.obfuscatedIdPool.append(potentialObfuscatedId)


    def countForwardFacingLetterTags(self):
        letteredTagCount = 0
        for tagId, tag in self.tags.items():
            if (tag.getIsForwardFacingLetterTag()):
                letteredTagCount += 1
        #
        return letteredTagCount


    def popObfuscatedTagLabel(self, env, tag, tagMode):
        # first, we add to an empty obfuscated letter pool if we need to, if we want to support late generation of obfuscated labels
        if (self.obfuscatedIdPool is None):
            raise makeJriException("Error: the tag manager obfuscation pool has not been initialized during post-processing; this needs to happen before we can pop labels.", None)
        if (len(self.obfuscatedIdPool)==0):
            self.addMoreToObfuscatedLabelPool(env)

        tagType = tag.getTagType()

        # grab one
        popIndex = None
        if (tagMode=="sequential"):
            # sequential
            popIndex = 0
        elif (tagMode=="random") or ((tagMode=="firstLetter") and (tagType=="decoy")):
            # randomized label
            popIndex = random.randint(0,len(self.obfuscatedIdPool)-1)
        elif (tagMode=="firstLetter"):
            # based on first letter
            tagId = tag.getProperId()
            firstLetter = tagId[0].upper()
            nextBestIndex = None
            for index,olabel in enumerate(self.obfuscatedIdPool):
                olabelFirstLetter = olabel[0].upper()
                popIndex = index
                if (olabelFirstLetter >= firstLetter):
                    # ok good enough (bigge or equal)
                    break
        else:
            raise makeJriException("Tag mode not understood ({}).".format(tagMode), None)

        # pop out the label and used it
        obfuscatedLabel = self.obfuscatedIdPool.pop(popIndex)
        return obfuscatedLabel




    def checkForDuplicateTags(self):
        obfuscatedLabels = {}
        for tagId, tag in self.tags.items():
            obfuscatedLabel = tag.getObfuscatedLabel()
            if (obfuscatedLabel in obfuscatedLabels):
                # duplicate
                raise makeJriException("Found two tags with duplicate (obfuscated) label: '{}'.".format(obfuscatedLabel))


    def getDocCount(self):
        count = 0
        for tagId, tag in self.tags.items():
            if tag.getIsDoc():
                count +=1
        return count


    def getMarkerCount(self):
        count = 0
        for tagId, tag in self.tags.items():
            if not tag.getIsDoc():
                count +=1
        return count


    def getDependencyTagListFromTag(self, tag, optionRecurse, env, astloc):
        allTags = []
        # get string list
        aTagDependencyListString = tag.getDependencyListString(True)
        if (aTagDependencyListString is None) or (aTagDependencyListString==""):
            return []
        # parse it and lookup tags
        dependentTags = parseTagListArg(aTagDependencyListString, "", env, astloc, False)
        for dtag in dependentTags:
            if dtag not in allTags:
                allTags.append(dtag)
                if (optionRecurse):
                    childTags = self.getDependencyTagListFromTag(dtag, True, env, astloc)
                    for childTag in childTags:
                        if (childTag not in allTags) and (childTag != tag):
                            allTags.append(childTag)
        return allTags



    def getTagsGainedAtLead(self, lead):
        tagsOut = []
        for tagId, tag in self.tags.items():
            if (tag.isGainedAtLead(lead)):
                tagsOut.append(tag)
        return tagsOut
#---------------------------------------------------------------------------































class CbTagItem:
    def __init__(self, id, deadline, label, tagType, location, documentNumber, needsPostProcess):
        self.id = id
        self.deadline = deadline
        self.label = label
        self.tagType = tagType
        self.obfuscatedLabel = None
        self.location = location
        self.needsPostProcess = needsPostProcess
        self.debugUse = []
        self.gainLeads = []
        self.checkLeads = []
        self.logicLeads = []
        self.documentNumber = documentNumber
        self.dependencyTagListString = None

    def getIsForwardFacingLetterTag(self):
        if (self.getIsDoc()):
            return False
        return True

    def addDebugUseLine(self, debugComment, sloc, leadp):
        debugEntryDict = {"comment": debugComment, "sloc": sloc, "lead": leadp}
        self.debugUse.append(debugEntryDict)

    def getDeadline(self):
        return self.deadline
    def getId(self):
        return self.id
    def getLabel(self):
        return self.label
    def setLabel(self, label):
        self.label = label
    def getObfuscatedLabel(self):
        return self.obfuscatedLabel
    def setObfuscatedLabel(self, val, flagIsCustom):
        self.obfuscatedLabel = val
        self.isCustomObfuscatedLabel = flagIsCustom
    def getIsCustomObfuscatedLabel(self):
        return self.isCustomObfuscatedLabel
    def getTagType(self):
        return self.tagType
    
    def getProperId(self):
        id = self.id
        parts = id.split(".", 1)
        tagProperId = parts[1]
        return tagProperId
 

    def getIsTagTypeDoc(self):
        return (self.tagType == "doc")

    def getDocumentNumber(self):
        return self.documentNumber
    def setDocumentNumber(self, val):
        self.documentNumber = val
    
    def getLocation(self):
        return self.location
    def getNiceLocationString(self):
        location = self.getLocation()
        if (location=="back"):
            location = DefBackOfBookDocLocationString
        return location

    def getNiceIdWithLabel(self):
        label = self.id
        if (self.label is not None) and (self.label!=""):
            #label += " ("+self.label+")"
            label += " - "+self.label
        return label

    def getNiceIdWithObfuscation(self):
        label = self.id
        label += " [" + self.getObfuscatedLabel() + "]"
        return label
    

    def getNiceIdWithLabelAndObfuscation(self):
        label = self.id
        if (self.label is not None) and (self.label!=""):
            #label += " ("+self.label+")"
            label += " ("+self.label+")"
        label += " [" + self.getObfuscatedLabel() + "]"
        return label
    

    def getMindMapNodeInfo(self):
        label = self.id
        if (self.label is not None) and (self.label!=""):
            #label += "("+self.label+")"
            label += "\n"+self.label
        if (label is None) or (label==""):
            label = self.tagType
        label += "\n(" + self.getNiceObfuscatedLabelWithType(False, False) + ")"
        #
        mmInfo = {
            "id": "TAG.{}".format(self.id),
            "label": label,
            "type": "tag",
            "subtype": self.tagType,
            "pointer": self,
            "mStyle": None,
            "showDefault": True,
            }
        return mmInfo


    def getNiceObfuscatedLabelWithType(self, flagBoldMarkdown, reportMode):
        if (self.getIsCustomObfuscatedLabel()) and (" " in self.getObfuscatedLabel()):
            # IFF there is a space in the obfuscated label then assume it is a complete thing, and dont add "Marker " to front, etc.
            classNamePlus = ""
        else:
            tagTypeClass = self.getTagTypeClass()
            classNamePlus = jrfuncs.uppercaseFirstLetter(tagTypeClass) + " "
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
    
    





    def isInBook(self):
        if (self.tagType == "doc") and (self.location=="back"):
            return True
        return False

    def getWhereText(self):
        if (self.tagType == "doc"):
            niceLocation = self.getNiceLocationString()
            if (niceLocation!=""):
                retv = _("which can be found {}").format(niceLocation)
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
            return _("document")
        else:
            return _("marker")
    
    def getIsDoc(self):
        return (self.tagType=="doc")

    def getTagTypeClassSortVal(self):
        if (self.tagType=="doc"):
            return "Z_Document"
        else:
            return "A_Marker"



    def recordGain(self, env, keyword, sloc, leadp):
        # add debug line
        self.addDebugUseLine("Tag gained", sloc, leadp)
        # add gain list
        recDict = {"lead":leadp, "keyword": keyword}
        self.gainLeads.append(recDict)
        # mindmapper
        mindManager = env.getMindManager()
        mindManager.addLinkBetweenNodes(env, keyword, None, leadp, self)


    def recordCheck(self, env, keyword, sloc, leadp):
        # add debug line
        self.addDebugUseLine("Tag checked", sloc, leadp)
        # add gain list
        recDict = {"lead":leadp, "keyword": keyword}
        self.checkLeads.append(recDict)
        # mindmapper
        mindManager = env.getMindManager()
        mindManager.addLinkBetweenNodes(env, keyword, None, leadp, self)


    def recordLogic(self, env, keyword, label, sloc, leadp):
        self.addDebugUseLine("Logic relation ({})".format(label), sloc, leadp)
        useDict = {
                   "lead": leadp,
                   "keyword": keyword,
                   "label": label,
                   }
        self.logicLeads.append(useDict)


    def recordLogicGeneric(self, env, keyword, label, sloc, target):
        self.addDebugUseLine("Logic relation ({})".format(label), sloc, target)
        useDict = {
                   "target": target,
                   "keyword": keyword,
                   "label": label,
                   }
        self.logicLeads.append(useDict)


    def getGainList(self, flagRemoveDuplicates):
        leadList = self.gainLeads
        if (not flagRemoveDuplicates):
            return leadList
        return self.uniqueLeadList(leadList)

    def getCheckList(self, flagRemoveDuplicates):
        leadList = self.checkLeads
        if (not flagRemoveDuplicates):
            return leadList
        return self.uniqueLeadList(leadList)

    def getLogicList(self, flagRemoveDuplicates):
        leadList = self.logicLeads
        if (not flagRemoveDuplicates):
            return leadList
        return self.uniqueLeadList(leadList)

    def uniqueLeadList(self, leadList):
        seen = set()
        unique_list = [x for x in leadList if not (x["lead"] in seen or seen.add(x["lead"]))]
        return unique_list

    def setDependencyListString(self, val):
        self.dependencyTagListString = val
    def getDependencyListString(self, tagManager):
        # return list of tag dependencies
        return self.dependencyTagListString

    def isGainedAtLead(self, lead):
        for g in self.gainLeads:
            if (g["lead"] == lead):
                return True
        return False





class CbConceptItem(CbTagItem):
    def __init__(self, id,  label, tagType):
        super().__init__(id, None, label, tagType, None, False, None)
        self.List = []

    def getIsForwardFacingLetterTag(self):
        return False

    def getMindMapNodeInfo(self):
        label = self.id
        if (self.label is not None) and (self.label!=""):
            label += "\n"+self.label
        if (label is None) or (label==""):
            label = self.tagType
        #
        mmInfo = {
            "id": "CONCEPT.{}".format(self.id),
            "label": label,
            "type": "concept",
            "subtype": self.tagType,
            "pointer": self,
            "mStyle": None,
            "showDefault": True,
            }
        return mmInfo







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
