# Rendering helper class
# The basic idea here is that the casebook interpretter will be instantiating and populating a RenderDoc object.
# And THIS renderdoc is what gets turned into a pdf.
# It will closely MIRROR the structure of the parsed sections/entries, but this RenderDoc does not contain "code" it is a one-for-one mapping to the output pdf

# Step 2:
# The plan is that the markdown -> latex conversion and the compiling of latex to pdf (via pdflatex etc) can be done entirely using the CbRenderDoc object without ANY need to access other data structures (lark, ast, etc)



# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
from .jriexception import *

from .cbplugin import DefPluginDomainEntryLeadProcessor

from .jrastvals import AstValString
from .jrast import JrAstResultList
from .jrastfuncs import isTextLatexVouched

from .cbreports import generateAllAuthorReports

from lib.jrlorem import jrlorem

from .casebookDefines import *



# python modules
import re



# Defines
DefBreakStyleSoloFacing = "soloFacing"
DefBreakStyleNone = "none"
DefSortMethodAlphaNumeric = "alphanum"

# global counter for rid assignments to leads and sections, which we use to give unique labels and hyperref links
GlobalRidCounter = 0



# base class for render doc/section/lead
class CbRenderBase():
    def __init__(self, renderdoc, level, parentp, entry, id, label, subheading, blockList, flagCopyEntryRid):
        self.renderdoc = renderdoc
        self.level = level
        self.parentp = parentp
        self.entry = entry
        self.id = id
        self.autoId = None
        self.label = label
        self.subheading = subheading
        self.sortMethod = None
        self.inlinedFromLead = None
        self.continuedFromLead = None
        #
        self.blankHead = False
        self.time = None
        self.timePos = None
        self.autoHeaderRender = True
        self.headingStyle = None
        self.childHeadingStyle = None
        self.layout = None
        # global rid
        global GlobalRidCounter
        GlobalRidCounter += 1
        self.rid = "r"+str(GlobalRidCounter)
        #
        self.blockList = CbRenderBlockManager(blockList)
        self.children = CbRenderChildManager(self)
        #
        self.mindMapLabel = None
        self.mindMapExtraLabel = None
        self.mindMapShowDefault = False
        self.mStyle = None
        self.role = None
        self.roleTag = None
        #
        self.visibility = True
        self.isMainLead = False
        #
        self.dividers = None
        self.address = None
        self.multiPage = None
        #
        self.toc = None
        self.childToc = None
        #
        self.sortGroup = None
        self.sortKey = None
        #
        self.anonymousChildCount = 0
        self.autoIdHashKeyCached = None
        #
        # this has to be done AFTER the initializations above
        self.setOptionsFromEntry(renderdoc, entry, flagCopyEntryRid)





    def getMindMapNodeInfo(self):
        mindMapLabel = self.getMindMapLabel()
        #
        if (mindMapLabel is not None):
            id = self.getIdPreferAutoId()
            if (id not in mindMapLabel):
                nodeLabel = self.getIdPreferAutoId() + "\n" + mindMapLabel
            else:
                nodeLabel = mindMapLabel
        else:
            nodeLabel = self.getNiceFullLabelForMindMap(True)

        # hidden?
        visible = self.getVisibility()
        if (not visible) or (self.isBlank()):
            self.setMStyleHide()

        mStyle = self.calcHierarchicalMStyle()

        mmInfo = {
            "id": "LEAD.{}".format(self.rid),
            "label": nodeLabel,
            "type": "lead",
            "pointer": self,
            "mStyle": mStyle,
            "showDefault": self.getMindMapShowDefault(),
            }
        return mmInfo


    def setMindMapShowDefault(self, val):
        self.mindMapShowDefault = val
    def getMindMapShowDefault(self):
        return self.mindMapShowDefault


    def getNiceFullLabelForMindMap(self, flagNewLineSep):
        if (self.isBlank()):
            # no label for this special blank node type
            return self.id

        if (self.label is not None) and (self.label!=""):
            niceLabel = self.label
        else:
            niceLabel = self.getIdPreferAutoId()
        #
        if (self.id is not None) and (self.id!="") and (self.id != niceLabel):
            niceLabel = self.id + " - "+ niceLabel
        #
        if (self.subheading is not None) and (self.subheading!=""):
            if (flagNewLineSep):
                niceLabel += ":\n" + self.subheading
            else:
                niceLabel += ": " + self.subheading
        elif (self.heading is not None) and (self.heading!=""):
            if (flagNewLineSep):
                niceLabel += ":\n" + self.heading
            else:
                niceLabel += ": " + self.heading
        # add address and dName?
        if (self.subheading is None):
            address = self.getAddress()
            dName = self.getDName()
            if (dName is not None) and (not dName.lower() in niceLabel.lower()):
                niceLabel += "\n" + dName
            if (address is not None) and (not address.lower() in niceLabel.lower()):
                niceLabel += "\n" + address
        #
        return niceLabel







    def getId(self):
        return self.id
    def getIdFallbackLabel(self):
        if (self.id is not None):
            return self.id
        return self.label


    def getIdPreferAutoId(self): 
        if (self.autoId is not None):
            return self.autoId
        return self.id
    def hasAutoId(self):
        return (self.autoId is not None)
    def getLabelIdPreferAutoId(self):
        if (self.autoId is not None):
            return self.autoId
        if (self.label is not None) and (self.label!=""):
            return self.label
        return self.id
    def getIdAndAutoIdForDebug(self):
        if (self.autoId is not None):
            return "{} ({})".format(self.id, self.autoId)
        return self.id
    def getIdPreferAutoIdFallbackLabel(self): 
        if (self.autoId is not None):
            return self.autoId
        if (self.id is not None):
            return self.id
        return self.label
    #
    def getReportToc(self):
        # item TITLE/LABEL
        titleOrig = self.calcDisplayTitle()
        # set toc, possibly based on title
        toc = self.getToc()
        if (toc is None):
            toc = titleOrig
        # title
        title = titleOrig
        # heading, which will replace title
        heading = self.getHeading()
        if (heading is not None):
            title = heading
        # id
        itemId = self.getId()      
        if (True):
            subheading = None
            if (toc!="") and (toc is not None):
                if (itemId is not None) and (itemId!="") and (not itemId in toc) and (not itemId in ["FRONT","REPORT"]):
                    # ADD itemid to toc
                    toc = toc + " [" + itemId + "]"
                    if ("inline" in itemId):
                        # add subheading also
                        subheading = self.getSubHeading()
                        if (subheading is not None) and (subheading!="") and (not subheading in toc):
                            toc = toc + " - "+ subheading
                else:
                    subheading = self.getSubHeading()
                    if (subheading is not None) and (subheading!="") and (not subheading in toc):
                        toc = toc + " - "+ subheading
            # add dName from hlapi if there is no custom label
            if (subheading is None) and ((self.label is None) or (self.label=="") or (self.id==self.label)):
                dName = self.getDName()
                if (dName is not None) and (not dName.lower() in toc.lower()) and (toc is not None) and (toc!=""):
                    toc += " (" + dName + ")"
            # kludge replace to remove stuff we don't nee
            if (toc is not None):
                toc = toc.replace(DefInlineLeadPlaceHolder, "")
        return toc
    #
    def getRid(self):
        return self.rid
    def setRid(self, val):
        self.rid = val
    #
    def getLabel(self):
        return self.label
    def setLabel(self, val):
        self.label = val
    def getLevel(self):
        return self.level
    def setLevel(self, val):
        self.level = val
    def setParent(self, val):
        self.parentp = val
    def getParent(self):
        return self.parentp
    def getEntry(self):
        return self.entry
    def getSubHeading(self):
        return self.subheading
    def setSubHeading(self, val):
        self.subheading = val

    def setBlankHead(self, val):
        self.blankHead = val
    def getBlankHead(self):
        return self.blankHead

    def isBlank(self):
        # this shoudl be sufficient
        return self.getBlankHead()


    def getTime(self):
        return self.time
    def setTime(self, val):
        self.time = val
    def getTimePos(self):
        return self.timePos
    def setTimePos(self, val):
        self.timePos = val
    def setAutoHeaderRender(self, val):
        self.autoHeaderRender = val
    def getAutoHeaderRender(self):
        return self.autoHeaderRender

    def setHeadingStyle(self, val):
        self.headingStyle = val
    def getHeadingStyle(self):
        return self.headingStyle
    def setChildHeadingStyle(self, val):
        self.childHeadingStyle = val
    def getChildHeadingStyle(self):
        return self.childHeadingStyle
    #
    def calcResolvedHeadingStyle(self):
        if (self.headingStyle is None) and (self.parentp is not None):
            # ask parent
            return self.parentp.calcResolvedChildHeadingStyle()
        return self.headingStyle 
    def calcResolvedChildHeadingStyle(self):
        return self.getChildHeadingStyle() 

    def setLayout(self, val):
        self.layout = val
    def getLayout(self):
        return self.layout

    def setToc(self, val):
        self.toc = val
    def getToc(self):
        return self.toc
    def setChildToc(self, val):
        self.childToc = val
    def getChildToc(self):
        return self.childToc

    def setHeading(self, val):
        self.heading = val
    def getHeading(self):
        return self.heading

    def setSortMethodAlphaNumeric(self):
        self.setSortMethod(DefSortMethodAlphaNumeric)
    def setSortMethod(self, val):
        self.sortMethod = val
    def getSortMethod(self):
        return self.sortMethod
    #
    def getChildPlugins(self):
        return self.childPlugins
    def setChildPlugins(self, val):
        self.childPlugins = val
    #
    def getAutoId(self):
        return self.autoId
    def setAutoId(self, val):
        self.autoId = val

    def setInlinedFromLead(self, val):
        self.inlinedFromLead = val
    def getInlinedFromLead(self):
        return self.inlinedFromLead
    def setContinuedFromLead(self, val):
        self.continuedFromLead = val
    def getContinuedFromLead(self):
        return self.continuedFromLead

    def getIsAutomaticId(self):
        isAutomatic = (self.inlinedFromLead or self.autoId)
        return isAutomatic

    def setMindMapLabel(self, val):
        self.mindMapLabel = val
    def getMindMapLabel(self):
        return self.mindMapLabel
    def setMindMapExtraLabel(self, val):
        self.mindMapExtraLabel = val
    def getMindMapExtraLabel(self):
        return self.mindMapExtraLabel

    def setMStyle(self, val):
        self.mStyle = val
    def setMStyleHide(self):
        self.setMStyle("hide")
    #def getMStyle(self):
    #    return self.mStyle
    def calcHierarchicalMStyle(self):
        val = self.mStyle
        if (val is None) and (self.parentp is not None):
            val = self.parentp.calcHierarchicalMStyle()
        return val
    def setRoleHint(self, tag):
        self.role = {"type": "hint", "tag": tag}
    def setRoleDoc(self, tag):
        self.role = {"type": "doc", "tag": tag}
    def getRole(self):
        return self.role
    def setVisibility(self, val):
        self.visibility = val
    def getVisibility(self):
        return self.visibility

    def getSortGroup(self):
        return self.sortGroup
    def getSortKey(self):
        return self.sortKey
    def setSortGroup(self, val):
        self.sortGroup = val
    def setSortKey(self, val):
        self.sortKey = val

    def calcDisplayTitle(self):
        #if (self.autoId is not None):
        #    return self.autoId
        title = self.label
        if (title is None):
            title = self.getIdPreferAutoId()
        return title

    def calcDisplayTitlePreferSubheading(self):
        if (self.subheading is not None) and (self.subheading != ""):
            subheadingIgnoreRegex = re.compile(r"^\(.*\)$")
            if (subheadingIgnoreRegex.match(self.subheading) is None):
                return self.subheading
        return self.calcDisplayTitle()

    #
    # these properties are inherited down
    def setSectionColumns(self, val):
        self.sectionColumns = val
    def getSectionColumns(self):
        return self.sectionColumns
    def getLeadColumns(self):
        return self.leadColumns
    def setLeadColumns(self, val):
        self.leadColumns = val
    def calcSectionColumns(self):
        val = self.sectionColumns
        if ((val is None) or (val==-1)) and (self.parentp is not None):
            val = self.parentp.calcSectionColumns()
        return val
    def calcLeadColumns(self):
        val = self.leadColumns
        if ((val is None) or (val==-1)) and (self.parentp is not None):
            val = self.parentp.calcLeadColumns()
        return val
    #
    def setSectionBreak(self, val):
        self.sectionBreak = val

    def setLeadBreak(self, val):
        self.leadBreak = val

    def calcSectionBreak(self):
        val = self.sectionBreak
        if (val is None) and (self.parentp is not None):
            val = self.parentp.calcSectionBreak()
        return val

    def calcLeadBreak(self):
        val = self.leadBreak
        if (val is None) and (self.parentp is not None):
            val = self.parentp.calcLeadBreak()
        return val

    def calcLeadDividers(self):
        val = self.dividers
        if (val is None):
            if (self.parentp is not None):
                val = self.parentp.calcLeadDividers()
            else:
                # top level DEFAULTS to Dividers
                val = DefCbDefine_TopLevelDividers
        return val

    def calcLeadAddress(self):
        val = self.getAddress()
        if (val is None) and (self.parentp is not None):
            val = self.parentp.calcLeadAddress()
        return val

    def addBlocks(self, blockList):
        self.blockList.add(blockList)
    
    def findChildById(self, id):
        for child in self.children.getList():
            if (child.getId() == id):
                return child
        return None

    def findChildSectionById(self, id):
        return self.findChildById(id)

    def setOptionsFromEntry(self, renderdoc, entry, flagCopyEntryRid):
        if (entry is None):
            # defaults
            self.setSectionColumns(None)
            self.setLeadColumns(None)
            self.setSectionBreak(None)
            self.setLeadBreak(None)
            self.setToc(None)
            self.setChildToc(None)
            self.setHeading(None)
            self.setChildPlugins(None)
            self.setDividers(None)
            self.setAddress(None)
            self.setDName(None)
            self.setContinuedFromLead(None)
            self.setAutoId(None)
            self.setMultiPage(None)
        else:
            self.setSectionColumns(entry.getSectionColumns())
            self.setLeadColumns(entry.getLeadColumns())
            self.setSectionBreak(entry.getSectionBreak())
            self.setLeadBreak(entry.getLeadBreak())
            self.setToc(entry.getToc())
            self.setChildToc(entry.getChildToc())
            self.setHeading(entry.getHeading())
            self.setChildPlugins(entry.getChildPlugins())
            self.setContinuedFromLead(entry.getContinuedFromLead())
            self.setDividers(entry.getDividers())
            self.setAddress(entry.getAddress())
            self.setDName(entry.getDName())
            self.setMStyle(entry.getMStyle())

            if (entry.getIsAutoLead()):
                # generate an unusued (randomish lead #) for this lead
                self.generateAutoLoadId(renderdoc, self.getAutoIdHashKey(self.getParent(), False))
            else:
                self.setAutoId(entry.getAutoId())

            # override our rid from the entry; this makes it possible to reference a lead entry even before we render
            # ATTN: 2/1/25 - DANGER - this could lead to multiple entries with same eid if you are not careful
            if (flagCopyEntryRid):
                self.setRid(entry.getRid())
            # 
            self.setBlankHead(entry.getBlankHead())
            self.setHeadingStyle(entry.getHeadingStyle())
            self.setChildHeadingStyle(entry.getChildHeadingStyle())
            self.setLayout(entry.getLayout())
            self.setTime(entry.getTime())
            self.setTimePos(entry.getTimePos())
            #
            self.setSortKey(entry.getSortKey())
            self.setSortGroup(entry.getSortGroup())
            self.setMultiPage(entry.getMultiPage())


    def getAutoIdHashKey(self, parentr, flagUpdateAnonCounter):
        # ATTN: if cached, return it
        if (self.autoIdHashKeyCached is not None):
            return self.autoIdHashKeyCached

        hid = self.getIdFallbackLabel()
        if (hid is None):
            raise makeJriException("Unexpected None value for id in getAutoIdHashKey.", None)
        if (hid=="inline"):
            hid = "il"
        if (flagUpdateAnonCounter):
            # keep counter of anonymous children inlines
            if (parentr is None):
                raise makeJriException("Incompatible call to getAutoIdHashKey with None parent and flagUpdateAnonCounter true", None)
            anonymousChildCounter = parentr.getUpdateAnonymousChildCount()
            hid += "["+ str(anonymousChildCounter) + "]"
        while (parentr is not None):
            pid = parentr.getAutoIdHashKey(None, False)
            if (True):
                hid = hid + "<" + pid
            else:
                hid = pid + "." + hid
            #
            parentr = parentr.getParent()
            # stop at root (alre)
            if (parentr is not None):
                # alternatively we could stop when parentr.id is None, which i think happens only at root CbRenderDoc
                if (isinstance(parentr, CbRenderDoc)):
                    break
                if (parentr.id is None):
                    break

        # cache it and return it
        self.autoIdHashKeyCached = hid
        return hid

    def getUpdateAnonymousChildCount(self):
        self.anonymousChildCount += 1
        return self.anonymousChildCount
    

    def getDividers(self):
        return self.dividers
    def setDividers(self, val):
        self.dividers = val

    def getAddress(self):
        return self.address
    def setAddress(self, val):
        self.address = val
    def getDName(self):
        return self.dName
    def setDName(self, val):
        self.dName = val

    def getMultiPage(self):
        return self.multiPage
    def setMultiPage(self, val):
        self.multiPage = val

    def sort(self):
        self.children.sort()

    def setBlockList(self, blockList):
        self.blockList = CbRenderBlockManager(blockList)


    def calcStatPlainTextWordCount(self):
        totalCount = {"words": 0, "bytes": 0}
        #
        ourCount = self.calcStatPlainTextWordCountInUs()
        recursiveCount = self.children.calcStatPlainTextWordCountRecursive()
        totalCount["words"] += ourCount["words"] + recursiveCount["words"]
        totalCount["bytes"] += ourCount["bytes"] + recursiveCount["bytes"]
        #
        return totalCount
    
    def calcStatPlainTextWordCountInUs(self):
        totalCount = {"words": 0, "bytes": 0}
        #
        # iterate blocks and add text
        iterableBlockList = self.blockList.getList()
        if (isinstance(iterableBlockList, JrAstResultList)):
            iterableBlockList = iterableBlockList.getContents()
        if (iterableBlockList is not None):
            for block in iterableBlockList:
                # only count plain text
                if (isinstance(block, str)):
                    text = block
                elif (isinstance(block, AstValString)):
                    text = block.getUnWrappedExpect(AstValString)
                else:
                    # skip
                    continue
                if (False and isTextLatexVouched(text)):
                    continue
                totalCount["bytes"] += len(text)
                totalCount["words"] += text.count(" ")+1
        #
        return totalCount

    def getIsMainLead(self):
        return self.isMainLead

    def setIsMainLead(self, val):
        self.isMainLead = val

    def getFullRenderTextForDebug(self):
        # build text for debug report testing
        allText = ""
        # iterate blocks and add text
        iterableBlockList = self.blockList.getList()
        if (isinstance(iterableBlockList, JrAstResultList)):
            iterableBlockList = iterableBlockList.getContents()
        if (iterableBlockList is not None):
            for block in iterableBlockList:
                if (isinstance(block, str)):
                    text = block
                elif (isinstance(block, AstValString)):
                    text = block.getUnWrappedExpect(AstValString)
                else:
                    # skip
                    continue
                allText += text
        #
        return allText


    def calcTagRepresentedByLead(self, env):
        tagManager = env.getTagManager()
        itemId = self.getId()
        tag = tagManager.findTagById(itemId)
        return tag

    def getNeedsPageBreakWarning(self, env):
        # ATTN: doesnt work well enough for large documents to use; instead multiplage documents need to set a specific field
        return False
        tag = self.calcTagRepresentedByLead(env)
        if (tag is None):
            return False
        if  (tag.getIsTagTypeDoc()):
            return True
        return False
















# a document is made up of sections
class CbRenderDoc(CbRenderBase):
    def __init__(self, interp):
        #
        super().__init__(self, 0, None, None, None, None, None, None, False)
        #
        self.interp = interp
        #
        self.options = None
        #
        # ATTN:TODO set from options; defaults
        self.setSectionColumns(1)
        self.setLeadColumns(2)
        self.setSectionBreak(DefBreakStyleSoloFacing)
        self.setLeadBreak(DefBreakStyleNone)
        #
        self.designatedFiles = []
        #
        self.queuedInlineLeads = []
        #
        self.jrLorem =  jrlorem.JrLorem("city.txt")

    def getInterp(self):
        return self.interp
    def getEnvironment(self):
        return self.getInterp().getEnvironment()
    def getLorem(self):
        return self.jrLorem

    def taskSetOptions(self, options):
        # start with user configured options
        env = self.getEnvironment()
        renderOptions = env.getEnvValueUnwrapped(None, "rendererData", None)
        self.options = jrfuncs.deepCopyListDict(renderOptions)
        # now overwrite with any passed in
        jrfuncs.deepMergeOverwriteA(self.options, options)
        #
        # FORCE option to make sure user cannot change it
        #self.options["latexExeFullPath"] = DefCbDefine_latexExeFullPath

    def getOption(self, keyName, defaultVal):
        return jrfuncs.getDictValueOrDefault(self.options, keyName, defaultVal)

    def getOptionTimeStyle(self):
        return self.getOption("timeStyle", None)
    #def getOptionDefaultTime(self):
    #    return self.getOption("defaultTime", None)
    def getOptionDefaultTimeStyle(self):
        return self.getOption("defaultTimeStyle", None)
    def getOptionZeroTimeStyle(self):
        return self.getOption("zeroTimeStyle", None)
    
    def getBypassErrorOnMissingImage(self, env):
        # overridden value?
        val = self.getOption("bypassErrorOnMissingImage", None)
        if (val is None):
            # get current value in environment and default to false
            val = env.getEnvValueUnwrapped(None, "rendererData.bypassErrorOnMissingImage", False)
        return val


    def getHlApi(self):
        return self.getInterp().getHlApi()
    def getHlApiPrev(self):
        return self.getInterp().getHlApiPrev()

    def getMainLeadsSectionName(self):
        return "LEADS"
    def getReportSectionName(self):
        return "REPORT"

    def isNarrowPaperSize(self):
        return self.getOption("isNarrowPaperSize", False)

    def addSection(self, renderSection):
        # add result to lead
        self.children.add(renderSection)



    def generateIdTreeTrace(self):
        # return text showing the id hierarchy (like debug)
        text = ""
        text = self.children.generateIdTreeTrace(0)
        return text



    def fileLeadWithBlockList(self, env, entry, lead, blockList):
        #
        # find the render SECTION that this lead is a child of
        parentEntry = entry.getParentp()
        renderSection = self.findRenderSectionFromParentEntry(parentEntry)

        # add result to lead
        lead.setBlockList(blockList)

        # now add it to renderSection
        renderSection.secFileLead(self.getInterp(), env, lead, renderSection, self)



    def createLeadFromEntry(self, entry, env):
        #
        # find the render SECTION that this lead is a child of
        parentEntry = entry.getParentp()
        renderSection = self.findRenderSectionFromParentEntry(parentEntry)
        if (renderSection is None):
            sloc = entry.getSourceLoc()
            raise makeJriException("Could not find parent section for entry ({} - {})".format(entry.id, entry.label), sloc)

        # create lead
        lead = CbRenderLead(self, renderSection.getLevel()+1, renderSection, entry, entry.getId(), entry.getLabel(), None, None, True)
        # process it
        renderSection.secProcessLead(self.getInterp(), env, lead, renderSection, self)
        #
        return lead



    def createSectionFromEntry(self, entry, env):
        #
        # find the render SECTION that this lead is a child of
        renderSection = CbRenderSection(self, 1, self, entry, entry.getId(), entry.getLabel(), None, None, True)
        #
        return renderSection



    def addLeadInline(self, inlineLabel, inlinedFromLead, sloc):
        # create a random lead for contents, then return it

        # create lead
        inlineId = "inline"
        lead = CbRenderLead(self, 2, None, None, inlineId, None, inlineLabel, None, False)
        hashKey = lead.getAutoIdHashKey(inlinedFromLead, True)
        lead.generateAutoLoadId(self, hashKey)
        lead.setInlinedFromLead(inlinedFromLead)

        # now add it to renderSection
        self.queueInlineLead(lead)

        return lead


    def getInlineSection(self):
        # return the section used for inline leads
        return self.getMainLeadsSection()

    def getMainLeadsSection(self):
        # return the section used for inline leads
        return self.findRenderSectionById(self.getMainLeadsSectionName())

    def getReportSection(self):
        # return the section used for inline leads
        return self.findRenderSectionById(self.getReportSectionName())


    def findRenderSectionFromParentEntry(self, parentEntry):
        renderSection = self.children.findByEntryp(parentEntry)
        return renderSection

    def findRenderSectionById(self, sectionId):
        renderSection = self.children.findByid(sectionId)
        return renderSection


    def printDebug(self, env):
        jrprint("Debug rendering from CbRenderDoc ({} sections):".format(len(self.sections)))
        for section in self.children.getList():
            section.printDebug(env)


    def makeRenderException(self, sloc, msg):
        return makeJriException("RENDER ERROR: " + msg, sloc)


   

    def mergeQueuedInlineLeadToRenderSectionWithId(self, env, targetSectionId):
        targetSection = self.findRenderSectionById(targetSectionId)
        self.mergeQueuedInlineLeadToRenderSection(env, targetSection)


    def mergeQueuedInlineLeadToRenderSection(self, env, renderSection):
        # move all children to section
        for lead in self.queuedInlineLeads:
            lead.setParent(renderSection)
            renderSection.processAndFileLead(self.getInterp(), env, lead, renderSection, self)
        # clear it
        self.queuedInlineLeads = []


    def queueInlineLead(self, lead):
        # add it to list for later processing
        self.queuedInlineLeads.append(lead)

    def findLeadByIdPath(self, id, astloc):
        # find and return the lead with matching id (id path)
        # ATTN: we want to throw exception if multiple matching ids
        # ATTN: path should of form PARENTID > CHILDID (we can't use dot notation since ids may be dotted)
        idParts = id.split(">")
        parentp = self
        descendant = None
        for idPart in idParts:
            idPart = idPart.strip()
            descendant = parentp.children.findDescendantByIdOrLabel(idPart, astloc)
            if (descendant is None):
                return None
            parentp = descendant
        # ok we found it
        return descendant


    def calcLeadCount(self):
        return self.children.calcLeadCountRecursive()


    def calcFlatLeadList(self, flagIncludeSections):
        retList = []
        self.children.addFlatRenderLeads(retList, flagIncludeSections)
        return retList

    def calcTopNLeads(self, topN, lambdaOnLead):
        # calc the top N leads sorted by a lambda
        flatList = self.calcFlatLeadList(True)
        sortedList  = sorted(flatList, key=lambda lead: lambdaOnLead(lead))
        retList = sortedList[0:topN]
        return retList

    def calcLeadStatsString(self, env):
        leadCount = self.calcLeadCount()
        plainTextWordCount = self.calcStatPlainTextWordCount()
        text = ""
        text += "{} Leads".format(leadCount)
        # new stuff
        tagManager = env.getTagManager()
        text += " / {} Docs".format(tagManager.getDocCount())
        text += " / {} Markers".format(tagManager.getMarkerCount())

        imageHelper = env.getFileManagerImagesCase()
        numFiles = imageHelper.getCount()
        unusedFileCount = imageHelper.getUnusedFileCount()
        text += " / {} Images".format(numFiles-unusedFileCount)

        dayManager = env.getDayManager()
        text += " / {} Days".format(dayManager.getDayCount())     
        #
        wordsPerLead = (int(plainTextWordCount["words"] / leadCount)) if (leadCount>0) else 0
        text += " / {} Words ({} avg.)".format(jrfuncs.niceLargeNumberStr(plainTextWordCount["words"]), wordsPerLead)
        text += " / {}".format(jrfuncs.niceFileSizeStr(plainTextWordCount["bytes"]))
  
        #
        return text



    # render doc report functions

    def generateReportSections(self, env, targetSectionId):
        # this function generates special author report sections useful for author debugging their case; it is not used in final output
        targetSection = self.findRenderSectionById(targetSectionId)
        generateAllAuthorReports(self, env, targetSection)


    def hideReportSections(self, env, targetSectionId):
        targetSection = self.findRenderSectionById(targetSectionId)
        if (targetSection is None):
            return
        # hide report section
        targetSection.setVisibility(False)


    def designateFile(self, fileFullPath, tag, rename):
        designatedFile = {
            "path": fileFullPath,
            "tag": tag,
            "rename": rename,
        }
        self.designatedFiles.append(designatedFile)


    def calcDocumentFontModifer(self):
        latexFontSize = float(self.getOption("latexFontSize", None))
        fontModifierAdditive = latexFontSize - DefCbRenderDefault_latexFontSize
        fontModifierMultiplicative = latexFontSize / DefCbRenderDefault_latexFontSize
        return [fontModifierAdditive, fontModifierMultiplicative]

    def calcDocumentBaseFontSize(self):
        latexFontSize = float(self.getOption("latexFontSize", None))
        return latexFontSize







    def calculateItemTime(self, env, item, parentSection):
        # an item is times IFF: this case is configured to use a clock AND we are in the proper LEADS section AND this is a "lead" (as opposed to a section) AND time!=0
        itemTime = item.getTime()
        if (not isinstance(item, CbRenderLead)):
            return False
        if (item.getLevel()==1) or (parentSection is None):
            # top level is not elligble
            return False
        # section time tells us the DEFAULT time for all entries in it; this is the LEADS section, etc
        defaultSectionTime = parentSection.getTime()
        if (defaultSectionTime is None):
            return False
        if (itemTime==-2):
            # -2 means NO TIME, DONT SHOW IT
            return False
        if (itemTime is None) and (not item.getIsMainLead()):
            # when its not main lead, then it has no default time
            return False
        if (itemTime is None) or (itemTime==-1):
            # no time specified, or -1, then we use default
            itemTime = defaultSectionTime
        # now return time
        return itemTime














































# a section is made up of leads (or maybe subsections) and some blocks
class CbRenderSection(CbRenderBase):
    def __init__(self, renderdoc, level, parentp, entry, id, label, subheading, blockList, flagCopyEntryRid):
        super().__init__(renderdoc, level, parentp, entry, id, label, subheading, blockList, flagCopyEntryRid)

    def printDebug(self, env):
        jrprint("Debug rendering from CbRenderSection.")


    def addChild(self, item):
        self.children.add(item)



    def processAndFileLead(self, jrinterp, env, lead, parentSection, renderDoc):
        self.secProcessLead(jrinterp, env, lead, parentSection, renderDoc)
        didFile = self.secFileLead(jrinterp, env, lead, parentSection, renderDoc)
        return didFile

    def secProcessLead(self, jrinterp, env, lead, parentSection, renderDoc):
        # run any plugins
        didFile = self.runPluginsOnLead(jrinterp, env, lead, parentSection, renderDoc, False)

    def secFileLead(self, jrinterp, env, lead, parentSection, renderDoc):
        # add lead to section

        # run any plugins
        didFile = self.runPluginsOnLead(jrinterp, env, lead, parentSection, renderDoc, True)
        if (not didFile):
            # it wasn't filed by any plugin, so it adds as a child of US
            self.addChild(lead)



    def runPluginsOnLead(self, jrinterp, env, lead, parentSection, renderDoc, flagFileMode):
        didFile = False
        if (parentSection is not None):
            parentChildPlugins = parentSection.getChildPlugins()
            if (parentChildPlugins is not None):
                pluginIds = parentChildPlugins.split(",")
                for pluginId in pluginIds:
                    pluginManager = jrinterp.getPluginManager()
                    plugin = pluginManager.findPluginById(DefPluginDomainEntryLeadProcessor, pluginId)
                    if (plugin is None):
                        raise makeJriException("Unknown plugin '{}' in runPluginsOnLead".format(pluginId), lead.getEntry())
                    if (not flagFileMode):
                        # all plugin run their "processLead" function (which might change label, etc.)
                        plugin.processLead(env, lead, parentSection, renderDoc)
                    else:
                        # we only let one plugin do the "filing" into a subsection
                        if (not didFile):
                            didFile = plugin.fileLead(env, lead, parentSection, renderDoc)
        #
        return didFile






    def printDebug(self, env):
        jrprint("   RENDER SECTION [{}:{}]".format(self.getIdAndAutoIdForDebug(), self.getLabel()))
        if (self.blockList is not None):
            self.blockList.printDebug(env)
        for child in self.children.getList():
            child.printDebug(env)























# a lead is made up of blocks (ie one big block of text or multiple blocks of text)
# note that SOMETIMES it may be created based on a (level 2) entry, BUT sometimes it may be dynamically created and there it no existing entry that it is derived from
# that is why it must be it's own thing
class CbRenderLead(CbRenderBase):
    def __init__(self, renderdoc, level, parentp, entry, id, label, subheading, blockList, flagCopyEntryRid):
        super().__init__(renderdoc, level, parentp, entry, id, label, subheading, blockList, flagCopyEntryRid)
        self.databaseLabel = None

    def printDebug(self, env):
        jrprint("Debug rendering from CbRenderLead.")

    def printDebug(self, env):
        jrprint("     RENDER LEAD [{}] with {} content blocks.".format(self.getLabel(), len(self.blockList)))
        self.blockList.printDebug(env)

    def generateAutoLoadId(self, renderdoc, autoIdHashKey):
        hlApi = renderdoc.getHlApi()

        if (True):
            if (autoIdHashKey is None) or (autoIdHashKey == ""):
                raise makeJriException("Bad autoIdHashKey in generateAutoLoadId().")
            unusedLeadRow = hlApi.chooseUnusedLeadUsingStableHashKey(autoIdHashKey)
        else:
            # old random way
            unusedLeadRow = hlApi.popAvailableLead()


        if (unusedLeadRow is None):
            raise makeJriException("Internal Render Error: Failed to generate lead# from hlapi.", self.getEntry())
        leadId = unusedLeadRow['lead']
        leadId = leadId.strip()
        self.setAutoId(leadId)

    def setDatabaseLabel(self, val):
        self.databaseLabel = val
    def getDatabaseLabel(self):
        return self.databaseLabel


    def getParsedLabelInfo(self):
        return self.cachedParsedLabelInfo

    def setParsedLabelInfo(self, val):
        self.cachedParsedLabelInfo = val







class CbRenderChildManager:
    def __init__(self, owner):
        self.children = []
        self.owner = owner

    def generateIdTreeTrace(self, offset):
        # return text showing the id hierarchy (like debug)
        text = ""

        indentSpaces = "." * offset
        for child in self.children:
            childEntryp = child.getEntry()
            childEntryId = child.getId()
            childEntryLabel = child.getLabel()
            text += "{} [{}] '{}'\n".format(indentSpaces, childEntryId, childEntryLabel)
            if (child.children is not None):
                text += child.children.generateIdTreeTrace(offset+1)
        return text


    def add(self, child):
        self.children.append(child)
    def findByEntryp(self, entryp):
        for child in self.children:
            childEntryp = child.getEntry()
            if (childEntryp == entryp):
                return child
        return None
    def findByid(self, id):
        for child in self.children:
            if not (isinstance(child, CbRenderSection)):
                continue
            childEntryAutoId = child.getAutoId()
            childEntryId = child.getId()
            if (childEntryId == id):
                return child
            if (childEntryAutoId == id):
                return child
            retv = child.findChildSectionById(id)
            if (retv is not None):
                # ATTN: TODO this will return the FIRST matching child with this id; we may want to consider instead checking all and raising exception
                return retv
        return None

    def findDescendantByIdOrLabel(self, id, astloc):
        foundResults = []
        # walk children looking for match
        for child in self.children:
            childEntryAutoId = child.getAutoId()
            childEntryId = child.getId()
            childEntryLabel = child.getLabel()
            if (childEntryId==""):
                pass
            if (childEntryId == id):
                foundResults.append(child)
            elif (childEntryAutoId == id):
                foundResults.append(child)
            elif (childEntryLabel == id):
                jrprint("ATTN: warning got label match.")
            elif (False) and (childEntryId==""):
                # try a label match?
                childEntryLabel = child.getLabel()
                if (childEntryLabel == id):
                    foundResults.append(child)
        if (len(foundResults)==0):
            # didn't find any.. allow recursion into children
            for child in self.children:
                childEntryId = child.getId()
                foundResult = child.children.findDescendantByIdOrLabel(id, astloc)
                if (foundResult is not None):
                    foundResults.append(foundResult)

        # if we found exactly one, then return it
        if (len(foundResults)==1):
            return foundResults[0]
        # if we found too many, complain
        if (len(foundResults)>1):
            raise makeJriException("Too many ({}) leads/sections match id ({}); use path string like SECTION>ID to be more specific".format(len(foundResults), id), astloc)
        # not found
        return None


    def __len__(self):
        return len(self.children)
    def getList(self):
        return self.children


    def sort(self):
        if (len(self.children)==0):
            return

        # recursively ask our children to sort THEIR children
        for child in self.children:
            child.sort()

        # now sort OUR children
        sortMethod = self.owner.getSortMethod()
        if (sortMethod is not None):
            # yes it wants sorting
            if (sortMethod==DefSortMethodAlphaNumeric):
                self.children.sort(key=lambda keyval: self.calcChildSortKey(keyval, sortMethod))
                pass
            else:
                raise makeJriException("Internal Render Error: Unknown sort method: {}.".format(sortMethod), self.owner.getEntry())

    def calcChildSortKey(self, child, sortMethod):
        if (sortMethod==DefSortMethodAlphaNumeric):
            sortKey = child.getSortKey()
            if (sortKey is None):
                sortKey = child.calcDisplayTitle()
            #
            sortKey = sortKey.upper()
            digitlen = 6
            sortKey = jrfuncs.zeroPadNumbersAnywhereInStringAll(sortKey, digitlen)
            # ATTN: not sure we use this??
            # now we prefix it with some ZZZZ so that it is easy to force other items before or after manually
            if (True):
                sortKey = "ZZZ_" + sortKey
            # new sort group, which is will group items
            sortGroup = child.getSortGroup()
            if (sortGroup is None):
                sortGroup = 5
            sortGroup = str(sortGroup).upper()
            sortGroup = jrfuncs.zeroPadNumbersAnywhereInStringAll(sortGroup, 3)
            sortKey = sortGroup + "." + sortKey
            #
            return sortKey
        else:
            raise makeJriException("Internal Render Error: Unknown sort method: {}.".format(sortMethod), self.owner.getEntry())  


    def mergeChildren(self, fromChildManager):
        for child in fromChildManager.children:
            self.add(child)


    def calcLeadCountRecursive(self):
        totalCount = 0
        for child in self.children:
            childCount = child.children.calcLeadCountRecursive()
            if (childCount==0):
                totalCount += 1
            else:
                totalCount += childCount
        return totalCount


    def calcStatPlainTextWordCountRecursive(self):
        totalCount = {"words": 0, "bytes": 0}
        for child in self.children:
            childCount = child.calcStatPlainTextWordCount()
            totalCount["words"] += childCount["words"]
            totalCount["bytes"] += childCount["bytes"]
        return totalCount





    def addFlatRenderLeads(self, retList, flagIncludeSections):
        # recursively add all RenderLEADS
        for child in self.children:
            if (isinstance(child, CbRenderLead)):
                retList.append(child)
            elif (flagIncludeSections and (isinstance(child, CbRenderSection))):
                retList.append(child)
        for child in self.children:
            childChildren = child.children
            if (childChildren is not None):
                childChildren.addFlatRenderLeads(retList, flagIncludeSections)








class CbRenderBlockManager:
    def __init__(self, blockList):
        self.blockList = blockList

    def add(self, item):
        # if item being added is a list or another JrAstResultList then flatten it before adding
        if (isinstance(item, list)):
            for i in item:
                self.blockList.append(i)
        elif (isinstance(item, JrAstResultList)):
            for i in item.getContents():
                self.blockList.append(i)
        else:
            self.blockList.append(item)

    def __len__(self):
        return len(self.blockList)
    def getList(self):
        return self.blockList

    def printDebug(self, env):
        if (self.blockList is not None):
            jrprint("       RENDER BLOCK CONTENTS:")
            self.blockList.printDebug(env)
















# manage output chunks (just a list of text items)
# we use a class here in case we want to do more clever stuff with allowing chunks that dont resolve right away into text, or which can be marked as safe or unsafe (user text), etc.
class outChunkManager():
    def __init__(self):
        self.clear()

    def clear(self):
        self.chunks = []

    def append(self, chunk):
        self.chunks.append(chunk)
    def getList(self):
        return self.chunks
