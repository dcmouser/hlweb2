# core casebook plugins

# cb modules
from .cbplugin import CbPlugin, DefPluginDomainEntryLeadProcessor
from .jrastutilclasses import JrINote
from .jriexception import *
#
from lib.hlapi import hlapi

# translation
from .cblocale import _

# python modules
import re

# jr libs
from lib.jr import jrfuncs







def registerPlugins(pluginManager):
    # register plugins
    pluginManager.addPlugin(CbPluginNyNoir())
    pluginManager.addPlugin(CbPluginDocs())
    pluginManager.addPlugin(CbPluginHints())
    #
    pluginManager.addPlugin(CbPluginShcd())
    pluginManager.addPlugin(CbPluginShcdTable())
    #
    pluginManager.addPlugin(CbPluginMythosTales())
    pluginManager.addPlugin(CbPluginMythosTalesTable())
    pluginManager.addPlugin(CbPluginBoi())
    pluginManager.addPlugin(CbPluginBoiTable())
    pluginManager.addPlugin(CbPluginBoiSingleTable())
    #
    pluginManager.addPlugin(CbPluginAlphaNumeric())


#parseHumanLabel() and assembleCanonicalLabels() returns
# returns [autoSectionName, canonicalLabel, subheading]

# trying to match against optional passed subsection in lead label like "25 NW [int]"
regexExtraTableSectionId = re.compile(r"^\[(.*)\]$")


















class CbPluginNyNoir(CbPlugin):
    def __init__(self):
        super().__init__()

    def getId(self):
        return "nynoir"
    def getPluginType(self):
        return DefPluginDomainEntryLeadProcessor

    def parseHumanLabel(self, env, renderDoc, lead, id, label, isAutoId, flagStageProcess):
        # for NY noir, entries should start with a lead number of the form #-####
        # our first step is to see if they have such a starting number in the LABEL
        # if its NOT in the label, check the id, to see if they forgot to put it in the label (we will fix if so)
        # if we DONT'T fine it, then we use an "other" section for the lead
        leadIdNumberText = None
        flagCheckLabel = (not isAutoId)

        # set flag to show this is a main lead
        lead.setIsMainLead(True)

        if (True):
            [matches, whereMatch, postLabel] = self.dualMatch(re.compile(r"([a-zA-Z0-9]\-[^\s]+)\s*(.*)"), label, id, 2, flagCheckLabel)
            if (matches is not None):
                # got it in the label
                leadIdNumberText = matches.group(1)
                # autoSectionName is just the first letter
                autoSectionName = leadIdNumberText[0]
                #
                [autoSectionName, canonicalLabel, subheading] = self.assembleCanonicalLabels(env, renderDoc, lead, autoSectionName, leadIdNumberText, postLabel, flagStageProcess)
                return [autoSectionName, canonicalLabel, subheading]
        #
        # not found
        autoSectionName = self.generateOtherSubsectionId()
        return [autoSectionName, None, None]


    def assembleCanonicalLabels(self, env, renderDoc, lead, autoSectionName, leadIdNumberText, postLabel, flagStageProcess):
        # combine remainderText and postLabel
        label = leadIdNumberText
        if (postLabel is not None) and (postLabel!=""):
            subheading = postLabel
        else:
            subheading = None

        # check the database and add any warnings if label does not match database, etc.
        if (not lead.getIsAutomaticId() and flagStageProcess):
            flagNotAlreadyBeInUsedList = True
            [label, subheading] = self.compareProposedLeadIdLabelWithDatabase(env, renderDoc, lead, leadIdNumberText, label, subheading, flagNotAlreadyBeInUsedList)

        return [autoSectionName, label, subheading]


    def postProcessNewSubSection(self, env, renderDoc, parentSection, subSection):
        # chance for plugin to process subsection that was just created
        # the subsection formatting is based on parent lead section
        # if parent lead section uses 2 column layout, then we use a tight 2 column layout for subsection headsers
        # wheras if its 1 column, then we use blank solo facint sstuff

        #
        # first try to get setting from renderdoc which will override configured
        parentLeadColumns = renderDoc.getOption("leadColumns", None)
        if (parentLeadColumns is None):
            parentLeadColumns = parentSection.getLeadColumns()
        #
        subSection.setSectionColumns(parentLeadColumns)
        subSection.setLeadColumns(parentLeadColumns)
        if (parentLeadColumns==2):
            subSection.setSectionBreak("before")
        else:
            subSection.setSectionBreak("soloFacing")














class CbPluginHints(CbPlugin):
    def __init__(self):
        super().__init__()

    def getId(self):
        return "hints"
    def getPluginType(self):
        return DefPluginDomainEntryLeadProcessor

    def parseHumanLabel(self, env, renderDoc, lead, id, label, isAutoId, flagStageProcess):
        autoSectionName = None
        #
        deadline = ""
        #
        tagManager = self.getTagManager()
        tagLocation = None
        tagObfuscatedLabel = None
        tagDependencyString = None
        #tag = tagManager.findOrDeclareTag(env, id, deadline, label, tagLocation, tagObfuscatedLabel, tagDependencyString, lead.getEntry(), "Parsing tag for hint", lead)
        tag = tagManager.findTagById(id)
        #
        # in report mode we show the real tag label
        reportMode = env.getReportMode()
        #
        hintForText = _("Hint for")
        if (tag is not None):
            # this is a TAG hint
            tagOLabel = tag.getNiceObfuscatedLabelWithType(False, reportMode)
            label =  hintForText + " " + tagOLabel
            labelToc = hintForText + " " + tag.getNiceObfuscatedLabelWithType(False, False)
            lead.setToc(labelToc)
            deadline = tag.getDeadline()
            if (deadline is not None) and (deadline>0):
                subheading = "(" + _("must be found by end of day") + " " + str(deadline) + ")"
            else:
                subheading = ""
            #
            lead.setRoleHint(tag)
            lead.setMindMapLabel(hintForText + " " + tag.getId() + "\n(" + tagOLabel + ")")
            lead.setMStyle("hint")
        else:
            # this is a MANUAL hint (or an undeclared tag error)
            subheading = ""
            #
            lead.setRoleHint(None)
            mmLabel = jrfuncs.combineTwoStringLabels(id, label, "\n(", ")", "[unlabeled]")
            lead.setMindMapLabel(hintForText + " " + mmLabel)
            lead.setMStyle("hint")
        #
        return [autoSectionName, label, subheading]

    def processLead(self, env, lead, parentSection, renderDoc):
        super().processLead(env, lead, parentSection, renderDoc)
        parentSection.setSortMethodAlphaNumeric()


    def processEntry(self, env, entry, parentEntry):
        # process an ENTRY (not a render lead, but will eventually be instantiated as a rendered lead); 
        # this is (one place) where we will build a map from hint tags to disguised marker
        pass











class CbPluginDocs(CbPlugin):
    def __init__(self):
        super().__init__()
        self.lastDocumentNumber = None

    def getId(self):
        return "docs"
    def getPluginType(self):
        return DefPluginDomainEntryLeadProcessor

    def parseHumanLabel(self, env, renderDoc, lead, id, label, isAutoId, flagStageProcess):
        autoSectionName = None
        # subheading gets ORIGINAL label
        #
        deadline = ""
        #

        if (id is None):
            raise makeJriException("An entry in the DOCUMENTS section is missing an id (maybe label is confusing it?); the label for the entry is '{}'.".format(label), lead)

        tagManager = self.getTagManager()
        tagLocation = None
        tagObfuscatedLabel = None
        tagDependencyString = None
        #tag = tagManager.findOrDeclareTag(env, id, deadline, label, tagLocation, tagObfuscatedLabel, tagDependencyString, lead.getEntry(), "Parsing tag for doc", lead)
        tag = tagManager.findTagById(id)
        if (tag is None):
            raise makeJriException("An entry in the DOCUMENTS section should have been declared earlier using $defineTag(\"{}\").".format(id), lead)
        if (not tag.getIsTagTypeDoc()):
            raise makeJriException("All entries in the DOCUMENTS section should have an id of \"doc.ID\"; instead found \"{}\".".format(id), lead)
        #
        if (flagStageProcess):
            documentNumber = tag.getDocumentNumber()
            if (documentNumber is not None):
                # make sure it is not out of order
                if (self.lastDocumentNumber is not None):
                    if (self.lastDocumentNumber >= documentNumber):
                        raise makeJriException("Numbered entries in the DOCUMENTS section MUST follow the same order they were declared previously using $declareDog, but entry \"{}\" is out of order (numbered doc {} but previous was {}).".format(id, documentNumber, self.lastDocumentNumber), lead)
                self.lastDocumentNumber = documentNumber
        #
        # in report mode we show the real tag label
        reportMode = env.getReportMode()
        #
        obfuscatedLabel = tag.getNiceObfuscatedLabelWithType(False, reportMode)
        labelToc = tag.getNiceObfuscatedLabelWithType(False, False)

        # ok now we have a weird situation, the SUBHEADING of the document is the original label of it, but there are TWO places a label for a document could be specified
        # the first is when the TAG for the document is created; it was my intention that that is where it should be specified
        # but authors might prefer to put it in the document label..
        # for now i will allow EITHER, BUT i will generate a warning when they mismatch
        # and force tag label if only doc label is specified
        subheadingTag = tag.getLabel()
        subheadingOriginalLabel = label
        if (subheadingOriginalLabel=="" or subheadingOriginalLabel is None):
            subheading = subheadingTag
        else:
            subheading = subheadingOriginalLabel
            if (subheadingTag=="" or subheadingTag is None) and (subheadingOriginalLabel is not None):
                # SET the tag label as if author set it when definingTag
                tag.setLabel(subheadingOriginalLabel)
        if (subheading=="" or subheading is None):
            # warn no label
            if (flagStageProcess):
                env.addNote(JrINote("warning", lead, "Document has no label or subheading, either in document entry or in tag definition via defineTag()", None, None))
        elif (subheadingTag!="" and subheadingTag is not None) and (subheadingOriginalLabel!="" and subheadingOriginalLabel is not None):
            # both specified
            if (subheadingTag!=subheadingOriginalLabel):
                # warn that they differ and tell author we are using subheadingOriginalLabel
                if (flagStageProcess):
                    env.addNote(JrINote("warning", lead, "Mismatch in document entry label and tag definition label using defineTag(), defaulting to using the label specfied on the document and ignoring that specified in defineTag()", None, None))
            else:
                # warn author that they dont need to specify both
                if (flagStageProcess):
                    env.addNote(JrINote("warning", lead, "Document entry has a label and document tag definition has same label specified again; you only need to put the label in the defineTag() definition and it will be shown on the document page automatically.", None, None))
        elif (subheadingTag=="" or subheadingTag is None) and (subheadingOriginalLabel!="" and subheadingOriginalLabel is not None):
            # warn them that we prefer them put the label in the tag rather than the document
            if (flagStageProcess):
                env.addNote(JrINote("warning", lead, "You have specified the label for the document in the document entry; this is ok, but it might (im not sure yet) be better to instead specify it when defining the tag with defineTag().", None, None))       

        lead.setToc(labelToc)
        #
        # hide mind map nodes for documents
        lead.setRoleDoc(tag)
        lead.setMStyle("hide")
        #
        return [autoSectionName, obfuscatedLabel, subheading]

    def processLead(self, env, lead, parentSection, renderDoc):
        super().processLead(env, lead, parentSection, renderDoc)
        parentSection.setSortMethodAlphaNumeric()


    def processEntry(self, env, entry, parentEntry):
        # process an ENTRY (not a render lead, but will eventually be instantiated as a rendered lead); 
        pass


    def preBuildPreRender(self, env):
        self.lastDocumentNumber = None
        pass

    def postBuildPreRender(self, env):
        pass


































# ---------------------------------------------------------------------------
class CbPluginClassicLead(CbPlugin):
    def __init__(self):
        super().__init__()
        # classic style of addresses
        self.regexList = [
            {"regex": re.compile(r"(\d+)[\s\-]?([a-zA-Z]+)[\s\-]*(.*)"), "neighborhood": 2, "number": 1, "extra": 3}, #e.g. "25 NW" or "25-NW" or "25NW"
            {"regex": re.compile(r"([a-zA-Z]*)[\s\-]*(\d+)[\s\-]*(.*)"), "neighborhood": 1, "number": 2, "extra": 3}, #e.g. "NW 25" or "NW-25" or "NW25"
        ]
        #self.canonicalRegex = {"regex": re.compile(r"(\d+) (.*)\s*(?\[(.*)\])"), "neighborhood": 2, "number": 1}  #e.g. "25 NW"
        self.canonicalRegex = {"regex": re.compile(r"(\d+) ([^\[\]\s]*)\s*(?:\[(.*)\])?"), "neighborhood": 2, "number": 1, "table": 3} #e.g. "25 NW" or "25 NW [inv]"
        self.sectionNameStringReplacements = {"WEST":"W", "EAST":"E", "NORTH":"N", "SOUTH": "S", "ELSEWHERE": "ELS"}
        self.sectionTableIdDict = {}

    def getPluginType(self):
        return DefPluginDomainEntryLeadProcessor

    def parseHumanLabel(self, env, renderDoc, lead, id, label, isAutoId, flagStageProcess):
        flagCheckLabel = (not isAutoId)

        # set flag to show this is a main lead
        lead.setIsMainLead(True)

        for rpat in self.regexList:
            # first regex
            regex = rpat["regex"]
            [matches, whereMatch, postLabel] = self.dualMatch(regex, label, id, None, flagCheckLabel)
            if (matches is not None):
                # got a match "25 NW" or "25-NW" or "25NW"
                leadIdNumberText = matches.group(rpat["number"]) if (rpat["number"] is not None) else ""
                neighborhood = matches.group(rpat["neighborhood"]) if (rpat["neighborhood"] is not None) else None
                extra = matches.group(rpat["extra"]) if (rpat["extra"] is not None) else None
                if (extra is not None) and (extra!=""):
                    # new system put extra in []
                    postLabel = extra
                [autoSectionName, canonicalLabel, subheading] = self.assembleCanonicalLabels(env, renderDoc, lead, neighborhood, leadIdNumberText, postLabel, flagStageProcess)
                return [autoSectionName, canonicalLabel, subheading]

        # not found
        autoSectionName = self.generateOtherSubsectionId()
        return [autoSectionName, None, None]


    def assembleCanonicalLabels(self, env, renderDoc, lead, autoSectionName, leadIdNumberText, postLabel, flagStageProcess):
        # convert to uppercase
        if (autoSectionName is not None) and (autoSectionName != ""):
            autoSectionName = autoSectionName.upper()
            # replacements
            autoSectionName = jrfuncs.replaceFromDict(autoSectionName, self.sectionNameStringReplacements)
            # form canonical label
            label =  "{} {}".format(leadIdNumberText, autoSectionName)
        else:
            # canoncial label is just the id
            label = leadIdNumberText
        #
        if (postLabel is not None) and (postLabel!=""):
            if (self.getShouldSortIntoHierarchicalSections()):
                postLabel = postLabel.strip()
                # see if its of the form [..] if so we use it as a nested section
                matches = regexExtraTableSectionId.match(postLabel)
                if (matches is not None):
                    subSectionTableId = matches.group(1)
                    subSectionTableId = self.translateTableSectionIdToNiceSectionLabel(subSectionTableId)
                    autoSectionName = subSectionTableId + ">" + autoSectionName
                    if False and (flagStageProcess):
                        # keep any postLabel id like [els]; we normally dont do this when we are sorting into hierarchical sections with >
                        label += " " + postLabel
                else:
                    label += " " + postLabel
            else:
                label += " " + postLabel

        subheading = None
        #
        return [autoSectionName, label, subheading]



    def translateTableSectionIdToNiceSectionLabel(self, subSectionTableId):
        if (subSectionTableId in self.sectionTableIdDict):
            return self.sectionTableIdDict[subSectionTableId]["label"]
        return subSectionTableId



    def processLead(self, env, lead, parentSection, renderDoc):
        # we might set toc to blank if we don't want it shown in toc
        childToc = parentSection.getChildToc()
        if (childToc is not None) and (childToc == ""):
            # force not to show in Table of Contents
            lead.setToc("")
        #
        super().processLead(env, lead, parentSection, renderDoc)
        # do we need to do this?
        parentSection.setSortMethodAlphaNumeric()











class CbPluginClassicLeadTable(CbPluginClassicLead):
    def __init__(self):
        super().__init__()
        self.defaultLeadTableId = ""
        self.disableOutOfRangeErrors = True
        self.shouldSortIntoHierarchicalSections = False

    def getPluginType(self):
        return DefPluginDomainEntryLeadProcessor

    def parseHumanLabel(self, env, renderDoc, lead, id, label, isAutoId, flagStageProcess):
        # let normal shcd processor parse it first
        optionAddressAsSubheading = True

        if (flagStageProcess):
            [autoSectionName, canonicalLabel, subheading] = super().parseHumanLabel(env, renderDoc, lead, id, label, isAutoId, flagStageProcess)
            # and then we "obfuscated" with a table lookup
        else:
            return [None, label, None]

        # set subheading to canonical label

        if (flagStageProcess):
            # and now set canonical label to the looked up paragraph number
            paragraphNumber = self.lookupParagraphNumberFromCanoncialTableAddress(canonicalLabel)
            if (paragraphNumber is None):
                # not found, do nothing
                # what about sorting into sections? yes let's leave the sorting by not clearing autoSectionName
                pass
            else:
                # save canonical label as pagraph number?
                if (optionAddressAsSubheading):
                    if (canonicalLabel is not None):
                        if (subheading is not None):
                            subheading = canonicalLabel + " - " + subheading
                        else:
                            subheading = canonicalLabel
                canonicalLabel = str(paragraphNumber)
                # do not sort into auto sections (alternatively we could sort by first digit)
                autoSectionName = None

        # force to large heading style for paragraph number
        lead.setHeadingStyle("large")

        # this seems to happen on auto generated leads
        if (autoSectionName==""):
            autoSectionName = None

        return [autoSectionName, canonicalLabel, subheading]


    def lookupParagraphNumberFromCanoncialTableAddress(self, canonicalLabel):
        # first parse into neighborhood and building
        regex = self.canonicalRegex["regex"]
        matches = regex.match(canonicalLabel)
        if (matches is None):
            # we don't know how to look it up
            return None
        # 
        tableId = matches.group(self.canonicalRegex["table"])
        if (tableId is None) or (tableId == ""):
            tableId = self.defaultLeadTableId
        buildingNum = matches.group(self.canonicalRegex["number"])
        neighborhood = matches.group(self.canonicalRegex["neighborhood"]).strip()  if (self.canonicalRegex["neighborhood"] is not None) else ""
        # find it in table
        try:
            paragraphNumber = self.hlapi.lookupTableEntry(neighborhood, buildingNum, tableId)
        except Exception as E:
            # not found, just use label as is
            return canonicalLabel

        paragraphNumberStr = str(paragraphNumber)
        if (paragraphNumberStr in ["0", "999", "XXX","-", "---"]):
            if (self.disableOutOfRangeErrors):
                return "ERR"
            raise Exception("Error in range of hlapi table; got an out of range value for location {} (parsed as {}-{}): {}.".format(canonicalLabel, neighborhood, buildingNum, paragraphNumberStr))

        # return it
        return paragraphNumberStr


    def preBuildPreRender(self, env):
        # here we will connect to to the hlapi for shcdTable and raise exception if its not being used with this lead plugin, and instruct it to build table, etc.
        # instead for now we will use our OWN custom hlapi
        flagForceLatexTableCreate = False
        self.hlapi.makeOrLoadDataTable(flagForceLatexTableCreate)
# ---------------------------------------------------------------------------








# ---------------------------------------------------------------------------
class CbPluginShcd(CbPluginClassicLead):
    def __init__(self):
        super().__init__()

    def getId(self):
        return "shcd"




class CbPluginShcdTable(CbPluginClassicLeadTable):
    def __init__(self):
        super().__init__()
        # create our own hlapi
        options = {"dataVersion": "shcdtable1", "outSuffix": "Shcd"}
        #
        numbersPerColumn = 100
        columns = {"EC":numbersPerColumn, "NW":numbersPerColumn, "SE":numbersPerColumn, "SW":numbersPerColumn, "WC":numbersPerColumn, "X":numbersPerColumn}
        tables = {"": {"title": "SHCD - LOOKUP TABLE", "toc": "Paragraph Lookup Table"}, }
        columnLimits = []
        self.hlapi = hlapi.HlApiTable(None, options, numbersPerColumn, columns, tables, "Normal", False, None)

    def getId(self):
        return "shcdTable"
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
class CbPluginMythosTales(CbPluginClassicLead):
    def __init__(self):
        super().__init__()

    def getId(self):
        return "mythosTales"



class CbPluginMythosTalesTable(CbPluginClassicLeadTable):
    def __init__(self):
        super().__init__()
        # create our own hlapi
        options = {"dataVersion": "mythosTalesTable1", "outSuffix": "MythosTales"}
        #
        numbersPerColumn = 100
        # C and R dont go past 30, but we are going to generate unique numbers to 100 because we dont have enough columns to add an X column; so if an author wants to add OTHER places, they should use C or R > 50
        #columns = {"C":30, "D":100, "E":30, "F":70, "L":70, "M":60, "N":80, "R":30, "U":70}
        columns = {"C":100, "D":100, "E":30, "F":70, "L":70, "M":60, "N":80, "R":100, "U":70}
        tables = {"": {"title": "MYTHOS TALES - LOOKUP TABLE", "toc": "Paragraph Lookup Table"}, }
        self.hlapi = hlapi.HlApiTable(None, options, numbersPerColumn, columns, tables, "Compact", False, None)

    def getId(self):
        return "mythosTalesTable"
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
class CbPluginBoi(CbPluginClassicLead):
    def __init__(self):
        super().__init__()
        self.sectionTableIdDict = {"int": {"label": "Interview",}, "inv": {"label": "Investigate",}, "els": {"label": "Elsewhere",}}


    def getId(self):
        return "boi"

    def parseHumanLabel(self, env, renderDoc, lead, id, label, isAutoId, flagStageProcess):
        [autoSectionName, canonicalLabel, subheading] = super().parseHumanLabel(env, renderDoc, lead, id, label, isAutoId, flagStageProcess)
        # TEST
        #if (label is not None) and ("SW" in label):
        #    autoSectionName = "Interview>" + autoSectionName
        #else:
        #    autoSectionName = "Investigate>" + autoSectionName    
        #
        return [autoSectionName, canonicalLabel, subheading]




class CbPluginBoiTable(CbPluginClassicLeadTable):
    def __init__(self):
        super().__init__()
        self.defaultLeadTableId = "int"
        #
        # create our own hlapi
        options = {"dataVersion": "boiTable1", "outSuffix": "Boi"}
        #
        optionOnly50Rows = True
        #
        if (optionOnly50Rows):
            numbersPerColumn = 50
            columns = {"NW":50, "NE":50, "WC":50, "EC":50, "SW":50, "SE":50, "ELS": 50}
            tables = {"int": {"title": "INTERVIEW", "toc": "Paragraph Lookup Table (Interview)"}, "inv": {"title": "INVESTIGATE", "toc": "Paragraph Lookup Table (Investigate)"}, }
            self.hlapi = hlapi.HlApiTable(None, options, numbersPerColumn, columns, tables, "SemiCompact", True, "BUREAU OF INVESTIGATION - LOOKUP TABLE")
        else:
            numbersPerColumn = 100
            columns = {"NW":50, "NE":50, "WC":50, "EC":50, "SW":50, "SE":50, "ELS": 50}
            tables = {"int": {"title": "INTERVIEW", "toc": "Paragraph Lookup Table (Interview)"}, "inv": {"title": "INVESTIGATE", "toc": "Paragraph Lookup Table (Investigate)"}, }
            self.hlapi = hlapi.HlApiTable(None, options, numbersPerColumn, columns, tables, "Normal", False, None)

    def getId(self):
        return "boiTable"



class CbPluginBoiSingleTable(CbPluginClassicLeadTable):
    def __init__(self):
        super().__init__()
        self.sectionTableIdDict = {"int": {"label": "Interview",}, "inv": {"label": "Investigate",}, "els": {"label": "Elsewhere",}}
        #
        # create our own hlapi
        options = {"dataVersion": "boiSingleTable", "outSuffix": "BoiSingle"}
        #
        optionOnly50Rows = True
        #
        if (optionOnly50Rows):
            numbersPerColumn = 50
            columns = {"NW":50, "NE":50, "WC":50, "EC":50, "SW":50, "SE":50, "ELS": 50, "X": 50}
            tables = {"": {"title": "BUREAU OF INVSTIGATION - LOOKUP TABLE", "toc": "Paragraph Lookup Table"}, }
            self.hlapi = hlapi.HlApiTable(None, options, numbersPerColumn, columns, tables, "Normal", False, None)
        else:
            numbersPerColumn = 100
            columns = {"NW":50, "NE":50, "WC":50, "EC":50, "SW":50, "SE":50, "ELS": 50, "X": 50}
            tables = {"": {"title": "BUREAU OF INVSTIGATION - LOOKUP TABLE", "toc": "Paragraph Lookup Table"}, }
            self.hlapi = hlapi.HlApiTable(None, options, numbersPerColumn, columns, tables, "Normal", False, None)


    def getId(self):
        return "boiSingleTable"
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
class CbPluginAlphaNumeric(CbPluginClassicLead):
    def __init__(self):
        super().__init__()
        # the whole id is the key, just as is
        self.regexList = [
            {"regex": re.compile(r"(.*)"), "number": 1, "neighborhood": None, "extra": None}, #e.g. "25 NW" or "25-NW" or "25NW"
        ]
        self.canonicalRegex = {"regex": re.compile(r"(.*)"), "number": 1, "neighborhood": None, "extra": None} #e.g. "25 NW" or "25 NW [inv]"

    def getId(self):
        return "alphaNumeric"


    def processLead(self, env, lead, parentSection, renderDoc):
        # process as normal
        super().processLead(env, lead, parentSection, renderDoc)
        # but now ALSO reserve it from the unused list
        hlapi = renderDoc.getHlApi()
        leadId = lead.getId()
        retv = hlapi.reserveLead(leadId)
        pass
# ---------------------------------------------------------------------------
