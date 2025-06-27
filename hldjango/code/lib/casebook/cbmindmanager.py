# mind manager diagram

from .cbrender import CbRenderDoc, CbRenderSection, CbRenderLead, outChunkManager

# helpers
from .jriexception import *
from lib.jr import jrfuncs

# python modules
import re

















def getObjectMindMap(env, obj):
    # if reference is a string, then look it up
    if (obj is None):
        return None
    if (type(obj) is str):
        refObj = lookupGenericObjectByReferenceId(env, obj)
    elif (type(obj) is dict):
        return obj
    else:
        refObj = obj
    return refObj





def getObjectMindMapInfo(env, obj):
    # if reference is a string, then look it up
    if (obj is None):
        return None
    refObj = getObjectMindMap(env, obj)
    if (refObj is None):
        raise makeJriException("Could not find object by id ({}) in mind mapper function.".format(obj), None)
    mmInfo = refObj.getMindMapNodeInfo()
    return mmInfo


def lookupGenericObjectByReferenceId(env, id):
    # try to find id in list of LEADS, then TAGS, etc.
    renderer = env.getRenderer()
    lead = renderer.findLeadByIdPath(id, None)
    if (lead is not None):
        return lead
    # try to find in tags
    tagManager = env.getTagManager()
    tag = tagManager.findTagById(id)
    if (tag is not None):
        return tag
    # try to find in concepts
    conceptManager = env.getConceptManager()
    tag = conceptManager.findTagById(id)
    if (tag is not None):
        return tag
    # day?
    matches = re.match(r"^DAY#(.+)$", id)
    if (matches is not None):
        dayManager = env.getDayManager()
        dayNumber = int(matches.group(1))
        flagAllowTempCalculatedDay = False
        day = dayManager.findDayByNumber(dayNumber, flagAllowTempCalculatedDay)
        if (day is not None):
            return day

    # not found
    return None






















class CbMindManagerLink:
    def __init__(self, typeStr, label, source, target):
        self.typeStr = typeStr
        self.label = label
        self.source = source
        self.target = target

    def getNiceLabel(self):
        label = self.typeStr
        if (self.label is not None) and (self.label!="") and (self.label != label):
            label += " - " + self.label
        return label

    def getNiceLabelTarget(self):
        label = self.getNiceLabel()
        label = label.replace("implies", "implied by")
        label = label.replace("suggests", "suggested by")
        label = label.replace("follows", "followed by")
        return label
























class CbMindManager:
    def __init__(self):
        self.pendingNodes = []
        self.links = []
        self.nodeHash = {}
        self.needsResolveProcessing = True


    def addLinkBetweenNodes(self, env, typeStr, label, source, target):
        # note that source could be an OBJECT which implements getMindMapNodeLabel() OR a STRING which we should look up
        link = CbMindManagerLink(typeStr, label, source, target)
        self.addLink(link)

    def addLinkAtributeOnNode(self, env, typeStr, label, source):
        link = CbMindManagerLink(typeStr, label, source, None)
        self.addLink(link)

    def addLink(self, link):
        self.links.append(link)

    def addPendingNode(self, node):
        self.pendingNodes.append(node)


    def buildMindMap(self, env, outputDirPath, baseFilename, flagDebug):
        jrfuncs.createDirIfMissing(outputDirPath)
        self.buildAndResolveLinksIfNeeded(env)
        #
        [retv, generatedFileName] = self.renderToDotImageFile(outputDirPath, baseFilename, flagDebug)
        return [retv, generatedFileName]

    def buildAndResolveLinksIfNeeded(self, env):
        if (self.needsResolveProcessing):
            self.buildAndResolveNodesAndLinks(env)


    def buildAndResolveNodesAndLinks(self, env):
        # first ADD nodes for all leads/days/tags/etc. (this can be done after they are all created)
        self.needsResolveProcessing = False
        self.nodeHash = {}


        # create all nodes 
        self.mergeObjectListIntoNodeHash(env, self.pendingNodes, False)
        tagManager = env.getTagManager()
        self.mergeObjectDictIntoNodeHash(env, tagManager.getTagDict())
        conceptManager = env.getConceptManager()
        self.mergeObjectDictIntoNodeHash(env, conceptManager.getTagDict())
        renderer = env.getRenderer()
        leadList = renderer.calcFlatLeadList(True)
        self.mergeObjectListIntoNodeHash(env, leadList, True)
        dayManager = env.getDayManager()
        self.mergeObjectDictIntoNodeHash(env, dayManager.getDayDict())
        self.mergeObjectListIntoNodeHash(env, env.getFlatEntryList(), False)

        # create links from days to tag deadlines
        self.createDayTagDeadlineLinks(env)

        # now walk links and resolve them  
        for index, link in enumerate(self.links):
            source = link.source
            target = link.target
            # NEW: handle source and target being prev or next
            sourceHashId = self.resolveMindMapObjectReferenceToHashId(env, source, target)
            targetHashId = self.resolveMindMapObjectReferenceToHashId(env, target, source)
            # reassign
            self.links[index].sourceHash = sourceHashId
            self.links[index].targetHash = targetHashId
            #jrprint(link.typeStr)



    def mergeObjectListIntoNodeHash(self, env, objectList, flagCheckRoles):
        for obj in objectList:
            # get the dict for this object
            objDict = obj.getMindMapNodeInfo()
            objUniqueId = objDict["id"]
            if (objUniqueId in self.nodeHash):
                raise makeJriException("Duplicate hash in mind manager node hash with id={}.".format(objUniqueId), None)
            self.nodeHash[objUniqueId] = objDict
            # extra stuff for the node? roles that connect this node automatically to another?
            if (flagCheckRoles):
                role = obj.getRole()
                if (role is not None):
                    roleType = role["type"]
                    if (roleType=="hint"):
                        # this node is a HINT (maybe for a tag
                        tag = jrfuncs.getDictValueOrDefault(role, "tag", None)
                        if (tag is not None):
                            self.addLinkBetweenNodes(env, "hint", None, tag, obj)

    def mergeObjectDictIntoNodeHash(self, env, objectDict):
        for key, obj in objectDict.items():
            # get the dict for this object
            objDict = obj.getMindMapNodeInfo()
            objUniqueId = objDict["id"]
            if (objUniqueId in self.nodeHash):
                raise makeJriException("Duplicate hash in mind manager node hash with id={}.".format(objUniqueId), None)
            self.nodeHash[objUniqueId] = objDict

    def createDayTagDeadlineLinks(self, env):
        dayManager = env.getDayManager()
        tagManager = env.getTagManager()
        # iterate each day
        for key, day in dayManager.getDayDict().items():
            dayNumber = day.getDayNumber()
            # now iterate all tags with this day deadline
            tagList = tagManager.findDeadlineTags(dayNumber)
            for tag in tagList:
                # create link from day to tag for deadline
                self.addLinkBetweenNodes(env, "deadline", None, tag, day)




    def resolveMindMapObjectReferenceToHashId(self, env, objectReference, relativeOrigin):
        if (objectReference=="previous"):
            # relative reference
            objectReference = self.calcRelativeObjectReference(env, relativeOrigin, -1, "previous")
        if (objectReference=="next"):
            # relative reference
            objectReference = self.calcRelativeObjectReference(env, relativeOrigin, 1, "next")
        objDict = getObjectMindMapInfo(env, objectReference)
        if (objDict is None):
            return None
        uniqueId = objDict["id"]
        if (uniqueId not in self.nodeHash):
            raise makeJriException("Could not find object by id ({}) in mind mapper hash but expected to find it.".format(uniqueId), None)
        return uniqueId


    def calcRelativeObjectReference(self, env, relativeOrigin, offset, hint):
        # find lead refered to by relative origina
        objDict = getObjectMindMapInfo(env, relativeOrigin)
        if (objDict is None):
            raise makeJriException("Trying to handle a relative lead reference (typically from a $logic({}) function); could not the lead to be relative to.".format(hint), None)
        if (objDict["type"]!="lead"):
            raise makeJriException("Trying to handle a relative lead reference (typically from a $logic({}) function); but the base item was not a lead (found {}).".format(hint), objDict["type"], None)
        leadp = objDict["pointer"]
        # ok now how do we get the lead RELATIVE to this leadp?
        renderer = env.getRenderer()
        leadList = renderer.calcFlatLeadList(True)
        index = leadList.index(leadp)
        if (index==-1):
            raise makeJriException("Trying to handle a relative lead reference (typically from a $logic({}) function); but the base lead was not found ({}).".format(hint, leadp.getIdFallbackLabel()), None)
        targetIndex = index + offset
        if (targetIndex<0) or (targetIndex>=len(leadList)):
            raise makeJriException("Trying to handle a relative lead reference (typically from a $logic({}) function); but the base lead was at end of index ({}).".format(hint, leadp.getIdFallbackLabel()), None)
        targetLeadp = leadList[targetIndex]
        return targetLeadp








    def calcRelatedLeadLinks(self, env, lead, ignoreLinkTypeList):
        # build a list of dictionaries {"label":.., "lead": ...} which represent the relationships (links) with this lead, using LINKS
        # now walk links and resolve them  
        from .cbrender import CbRenderLead
        #
        retList = []
        for index, link in enumerate(self.links):
            if (link.typeStr in ignoreLinkTypeList):
                continue
            #
            source = getObjectMindMap(env, link.source)
            target = getObjectMindMap(env, link.target)
            if (source!=lead) and (target!=lead):
                continue
            #
            if (source==lead):
                label = link.getNiceLabel()
                relatedObject = target
            elif (target==lead):
                label = link.getNiceLabelTarget()
                relatedObject = source
            else:
                # iffy
                label = link.getNiceLabelTarget()
                relatedObject = target
            #
            if (relatedObject is None):
                relatedLinkDict = {"label": jrfuncs.uppercaseFirstLetter(label)}
            elif (isinstance(relatedObject, CbRenderLead)):
                relatedLinkDict = {"label": jrfuncs.uppercaseFirstLetter(label), "relatedLead": relatedObject}
            else:
                relatedLinkDict = {"label": jrfuncs.uppercaseFirstLetter(label), "relatedObject": relatedObject}
            #
            relatedLinkDict["source"] = link.source
            relatedLinkDict["target"] = link.target
            retList.append(relatedLinkDict)
        return retList



    def findDeductiveLeadsThatLogicallyImplyOrSuggestTargetLead(self, env, targetLead):
        sourceLeads = []

        # walk through all deductive links from source to target and add to sourceLeads
        excludedLinkTypes = []
        #
        for index, link in enumerate(self.links):
            linkTypeStr = link.typeStr
            source = getObjectMindMap(env, link.source)
            target = getObjectMindMap(env, link.target)
            if (linkTypeStr in excludedLinkTypes):
                continue

            if (target==targetLead) and (source is not None):
                if (not isinstance(source, CbRenderLead)):
                    continue
                sourceItem = {"lead": source, "link": linkTypeStr}
                sourceLeads.append(sourceItem)

        return sourceLeads
# ---------------------------------------------------------------------------

















