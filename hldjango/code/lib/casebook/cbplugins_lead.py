# core casebook plugins

# cb modules
from .cbplugin import CbPlugin, DefPluginDomainEntryLeadProcessor
from .jriexception import *

# python modules
import re

# jr libs
from lib.jr import jrfuncs




def registerPlugins(pluginManager):
    # register plugins
    pluginManager.addPlugin(CbPluginShcd())
    pluginManager.addPlugin(CbPluginNyNoir())
    pluginManager.addPlugin(CbPluginDocs())
    pluginManager.addPlugin(CbPluginHints())




#parseHumanLabel() and assembleCanonicalLabels() returns
# returns [autoSectionName, canonicalLabel, subheading]


class CbPluginShcd(CbPlugin):
    def __init__(self):
        super().__init__()

    def getId(self):
        return "shcd"
    def getPluginType(self):
        return DefPluginDomainEntryLeadProcessor

    def parseHumanLabel(self, env, renderDoc, lead, id, label, isAutoId, flagStageProcess):
        flagCheckLabel = (not isAutoId)

        # set flag to show this is a main lead
        lead.setIsMainLead(True)

        if (True):
            # first regex
            [matches, whereMatch, postLabel] = self.dualMatch(re.compile(r"(\d+)[\s\-]?([^\s]+)(.*)"), label, id, None, flagCheckLabel)
            if (matches is not None):
                # got a match "25 NW" or "25-NW" or "25NW"
                leadIdNumberText = matches.group(1)
                autoSectionName = matches.group(2)
                [autoSectionName, canonicalLabel, subheading] = self.assembleCanonicalLabels(env, renderDoc, lead, autoSectionName, leadIdNumberText, postLabel, flagStageProcess)
                return [autoSectionName, canonicalLabel, subheading]

            if (matches is None):
                [matches, whereMatch, postLabel] = self.dualMatch(re.compile(r"(.*[^\s\d])[\s\-]?(\d+)"), label, id, None, flagCheckLabel)
            if (matches is not None):
                # got a match "NW 25" or "NW-25" or "NW25"
                leadIdNumberText = matches.group(2)
                autoSectionName = matches.group(1)
                [autoSectionName, canonicalLabel, subheading] = self.assembleCanonicalLabels(env, renderDoc, lead, autoSectionName, leadIdNumberText, postLabel, flagStageProcess)
                return [autoSectionName, canonicalLabel, subheading]

        # not found
        autoSectionName = self.generateOtherSubsectionId()
        return [autoSectionName, None, None]


    def assembleCanonicalLabels(self, env, renderDoc, lead, autoSectionName, leadIdNumberText, postLabel, flagStageProcess):
        # convert to uppercase
        autoSectionName = autoSectionName.upper()
        # replacements
        sectionNameReplacements = {"WEST":"W", "EAST":"E", "NORTH":"N", "SOUTH": "S", "ELSEWHERE": "ELSE"}
        autoSectionName = jrfuncs.replaceFromDict(autoSectionName, sectionNameReplacements)
        # form canonical label
        label =  "{} {}".format(leadIdNumberText, autoSectionName)
        if (postLabel is not None) and (postLabel!=""):
            label += " " + postLabel
        subheading = None
        #
        return [autoSectionName, label, subheading]
























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
            [label, subheading] = self.compareProposedLeadIdLabelWithDatabase(env, renderDoc, lead, leadIdNumberText, label, subheading)

        return [autoSectionName, label, subheading]











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
        tag = tagManager.findOrDeclareTag(env, id, deadline, label, tagLocation, tagObfuscatedLabel, lead.getEntry(), "Parsing tag for hint", lead)
        #
        # in report mode we show the real tag label
        reportMode = env.getReportMode()
        #
        tagOLabel = tag.getNiceObfuscatedLabelWithType(False, reportMode)
        label = "Hint for " + tagOLabel
        labelToc = "Hint for " + tag.getNiceObfuscatedLabelWithType(False, False)
        lead.setToc(labelToc)
        subheading = ""
        #
        lead.setRoleHint(tag)
        lead.setMindMapLabel("Hint for " + tag.getId() + "\n(" + tagOLabel + ")")
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
        #
        deadline = ""
        #
        tagManager = self.getTagManager()
        tagLocation = None
        tagObfuscatedLabel = None
        #tag = tagManager.findOrDeclareTag(env, id, deadline, label, tagLocation, tagObfuscatedLabel, lead.getEntry(), "Parsing tag for doc", lead)
        tag = tagManager.findTagById(id)
        if (tag is None):
            raise makeJriException("An entry in the DOCUMENTS section should have been declared earlier using $declareTag(\"{}\").".format(id), lead)
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
        label = tag.getNiceObfuscatedLabelWithType(False, reportMode)
        labelToc = tag.getNiceObfuscatedLabelWithType(False, False)
        subheading = tag.getLabel()
        lead.setToc(labelToc)
        #
        # hide mind map nodes for documents
        lead.setRoleDoc(tag)
        lead.setMStyle("hide")
        #
        return [autoSectionName, label, subheading]

    def processLead(self, env, lead, parentSection, renderDoc):
        super().processLead(env, lead, parentSection, renderDoc)
        #
        parentSection.setSortMethodAlphaNumeric()


    def processEntry(self, env, entry, parentEntry):
        # process an ENTRY (not a render lead, but will eventually be instantiated as a rendered lead); 
        pass


    def preBuildPreRender(self, env):
        self.lastDocumentNumber = None
        pass

    def postBuildPreRender(self, env):
        pass
