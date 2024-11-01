# mind manager diagram

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
    # day?
    matches = re.match(r"^DAY#(.+)$", id)
    if (matches is not None):
        dayManager = env.getDayManager()
        dayNumber = int(matches.group(1))
        day = dayManager.findDayByNumber(dayNumber)
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
        self.buildAndresolveNodesAndLinks(env)
        [retv, generatedFileName] = self.renderToDotImageFile(outputDirPath, baseFilename, flagDebug)
        return [retv, generatedFileName]



    def buildAndresolveNodesAndLinks(self, env):
        # first ADD nodes for all leads/days/tags/etc. (this can be done after they are all created)
        self.nodeHash = {}

        # create all nodes 
        self.mergeObjectListIntoNodeHash(env, self.pendingNodes, False)
        tagManager = env.getTagManager()
        self.mergeObjectDictIntoNodeHash(env, tagManager.getTagDict())
        renderer = env.getRenderer()
        leadList = renderer.calcFlatLeadList()
        self.mergeObjectListIntoNodeHash(env, leadList, True)
        dayManager = env.getDayManager()
        self.mergeObjectDictIntoNodeHash(env, dayManager.getDayDict())
        self.mergeObjectListIntoNodeHash(env, env.getFlatEntryList(), False)

        # create links from days to tag deadlines
        self.createDayTagDeadlineLinks(env)


        # now walk links and resolve them  
        for index, link in enumerate(self.links):
            sourceHashId = self.resolveMindMapObjectReferenceToHashId(env, link.source)
            targetHashId = self.resolveMindMapObjectReferenceToHashId(env, link.target)
            # reassign
            self.links[index].source = sourceHashId
            self.links[index].target = targetHashId
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
                        # this node is a HINT for a tag
                        tag = role["tag"]
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




    def resolveMindMapObjectReferenceToHashId(self, env, objectReference):
        objDict = getObjectMindMapInfo(env, objectReference)
        if (objDict is None):
            return None
        uniqueId = objDict["id"]
        if (uniqueId not in self.nodeHash):
            raise makeJriException("Could not find object by id ({}) in mind mapper hash but expected to find it.".format(uniqueId), None)
        return uniqueId





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
                relatedLead = target
            elif (target==lead):
                label = link.getNiceLabelTarget()
                relatedLead = source
            if (relatedLead is None) or (isinstance(relatedLead, CbRenderLead)):
                relatedLinkDict = {"label": jrfuncs.uppercaseFirstLetter(label), "relatedLead": relatedLead}
                retList.append(relatedLinkDict)
        return retList
# ---------------------------------------------------------------------------

















