# plugins can configured to run on section children



# jr libs
from lib.jr import jrfuncs




# defines
DefPluginDomainEntryLeadProcessor = "leadEntryProcessor"







# CbPluginManager manages a collection of plugin that can be found by name
class CbPluginManager:
    def __init__(self, interp):
        self.plugins = {}
        self.interp = interp
        #

    def addPlugin(self, plugin):
        plugin.setInterp(self.interp)
        id = plugin.getId()
        pluginType = plugin.getPluginType()
        if (pluginType not in self.plugins):
            self.plugins[pluginType] = {}
        self.plugins[pluginType][id] = plugin
    def findPluginById(self, pluginType, id):
        if (pluginType in self.plugins) and (id in self.plugins[pluginType]):
            return self.plugins[pluginType][id]
        return None

    def preBuildPreRender(self, env):
        # run the post build for all plugins
        # ATTN: this is not implemented yet
        for pluginTypeKey, pluginTypeGroup in self.plugins.items():
            for pluginIdLey, plugin in pluginTypeGroup.items():
                plugin.preBuildPreRender(env)


    def postBuildPreRender(self, env):
        # run the post build for all plugins
        # ATTN: this is not implemented yet
        for pluginTypeKey, pluginTypeGroup in self.plugins.items():
            for pluginIdLey, plugin in pluginTypeGroup.items():
                plugin.postBuildPreRender(env)
















# The CbPlugin class is used to help sort and file output sections in a file render book
# derived classes may handle this differently.
# as an example, in New York Noir cases, the CbFilerNyNoir class would create subsections for each # prefix in the leads section
# and in SHCD cases, a CbFilerShcd would create sections for NW, SW, NW, WC, S, etc., and also format lead ids in a consistent way ("25 SW" instead of "SW25") 
# THOUGH perhaps this is best done by options in the parent SECTION options for # LEADS
# and we should let the parent section entry be responsible for creating output rendering sections
class CbPlugin:
    def __init__(self):
        pass



    # main functions that should be implemented
    # processEntry(), processLead() and fileLead()







    # THESE ARE THE MAIN FUNCTIONS THAT A PROCESSOR PROVIDES
    # YOU MIGHT HAVE MULTIPLE PROCESSORS THAT RUN PROCESSLEAD() BUT ONLY ONE CAN RUN FILELEAD() AND RETURN TRUE

    # process an ENTRY (not a render lead, but will eventually be instantiated as a rendered lead); 
    def processEntry(self, env, entry, parentEntry):
        pass


    # process a lead to set modified labels (to make them canonical etc)
    def processLead(self, env, lead, parentSection, renderDoc):
        # standardize lead labels to be of the form "CHARACTER-####""
        #
        id = lead.getIdPreferAutoId()
        label = lead.getLabel()
        isAutoId = lead.hasAutoId()
        [autoSectionName, canonicalLabel, subheading] = self.parseHumanLabel(env, renderDoc, lead, id, label, isAutoId, True)
        #
        if (subheading is not None):
            lead.setSubHeading(subheading)
        #
        # update label
        if (canonicalLabel is not None) and (canonicalLabel!="") and (canonicalLabel != label):
            lead.setLabel(canonicalLabel)


    # file a lead into a sub section (possibly created to organize by letter or prefix, etc.)
    def fileLead(self, env, lead, parentSection, renderDoc):
        # BEFORE calling this our caller should call processLead
        # RETURN True if we have filed it, otherwise false
        # now figure out what section to put it in
        subSection = self.findOrMakeSubsectionForLead(env, lead, parentSection, renderDoc)
        if (subSection is not None):
            subSection.addChild(lead)
            return True
        else:
            return False









    # helper; this may be subclasses
    def findOrMakeSubsectionForLead(self, env, lead, parentSection, renderDoc):
        # instead of subclassing this you can subclass 

        # cb modules
        from .cbrender import CbRenderSection, DefSortMethodAlphaNumeric

        # find the lead sub-section where to file this lead
        # return None to just put it in normal section
        # get neighborhood code that we set during processLead
        optionBumpLevel = 1

        # get autoSectionName
        id = lead.getIdPreferAutoId()
        label = lead.getLabel()
        isAutoId = lead.hasAutoId()
        [autoSectionName, canonicalLabel, subheading] = self.parseHumanLabel(env, renderDoc, lead, id, label, isAutoId, False)

        # if not autoSectionName then nothing to do
        if (autoSectionName is None):
            return None

        # we are going to use a subsection        
        autoSectionLabel = autoSectionName

        if (optionBumpLevel):
            # bump lead indent once
            lead.setLevel(lead.getLevel()+1)

        # create section for the neighborhoodcode
        subSection = parentSection.findChildById(autoSectionName)
        if (subSection is not None):
            # already there; found it; nothing more to do
            return subSection
        #
        # make the new auto section
        #
        # should we bump in levels?
        subheading = None
        subSection = CbRenderSection(renderDoc, parentSection.getLevel()+optionBumpLevel, parentSection, parentSection.getEntry(), autoSectionName, autoSectionLabel, subheading, None)
        # propagate parent section time value to autosection for LEADS with default time
        subSection.setTime(parentSection.getTime())
        subSection.setTimePos(parentSection.getTimePos())
        #
        # any overrides from parent entry options?
        self.customizeAutoSection(subSection, parentSection)

        # add it
        parentSection.children.add(subSection)
        # return it
        return subSection





    def setInterp(self, val):
        self.interp = val
    def getInterp(self):
        return self.interp
    def getTagManager(self):
        return self.getInterp().getTagManager()


    def generateOtherSubsectionId(self):
        return "Other"

    def customizeAutoSection(self, autoSection, parentSection):
        # hide subsection label by setting this to "" or default show by setting it to None; dont leave blank or it will inherit from parent
        autoSectionToc = None
        autoSection.setToc(autoSectionToc)
        # set sorting methods for parent and for us
        autoSection.setSortMethodAlphaNumeric()
        parentSection.setSortMethodAlphaNumeric()
        # font size
        autoSection.setHeadingStyle("huge")



    #
    def dualMatch(self, regexObj, label, id, remainderTextGroupIndex, flagCheckLabel):
        # do regex match against label, then fallback to id
        # return [matches, "label"|"id", extraLabelText]
        if (flagCheckLabel) and (label is not None) and (label!=""):
            matches = regexObj.match(label)
            if (matches is not None):
                if (remainderTextGroupIndex is not None):
                    remainderText = matches.group(remainderTextGroupIndex)
                else:
                    remainderText = None
                return [matches, "label", remainderText]
        if (id is not None) and (id!=""):
            matches = regexObj.match(id)
            if (matches is not None):
                remainderText = label
                if (remainderTextGroupIndex is not None):
                    remainderTextAdd = matches.group(remainderTextGroupIndex)
                    if (remainderTextAdd!=""):
                        if (remainderText is not None) and (remainderText!=""):
                            remainderText += " " + remainderTextAdd
                        else:
                            remainderText = remainderTextAdd
                else:
                    remainderText = None
                return [matches, "id", remainderText]
        return [None, None, None]



    def calcTagObfuscatedLabelForId(self, id, flagTitleCase):
        if (id.startswith("doc")):
            label = "document {}".format(1)
        else:
            label = "tag {}".format("A")
        if (flagTitleCase):
            label = label.title()
        return label







    # many derived plugins could simply subclass these functions instead of the main ones

    def parseHumanLabel(self, env, renderDoc, lead, id, label, isAutoId, flagStageProcess):
        # returns [autoSectionName, canonicalLabel, subheading]
        return [None, None, None]

    def assembleCanonicalLabels(self, env, renderDoc, lead, autoSectionName, leadIdNumberText, postLabel, flagStageProcess):
        # return [autoSectionName, canonicalLabel, subheading]
        return [autoSectionName, None, None]





    def compareProposedLeadIdLabelWithDatabase(self, env, renderDoc, lead, leadIdNumberText, label, subheading):
        # this function will look up the lead id in the lead database and compare the database label with user casebook label
        # it will generate a warning if the lead has a label that does not seem compatible/similar with database label
        # it could also SET our display label if the user has asked for it
        # return label, subheading
        # also we can set lead.setDatabaseLabel() with the database label for future use
        from .jrastutilclasses import JrINote

        # get api prev for warnings
        hlApiPrev = renderDoc.getHlApiPrev()
        [leadRowPrev, sourceKeyPrev] = hlApiPrev.findLeadRowByLeadId(leadIdNumberText)


        # get api
        hlApi = renderDoc.getHlApi()
        [leadRow, sourceKey] = hlApi.findLeadRowByLeadId(leadIdNumberText)
        if (leadRow is None):
            # generate warning that we have a lead id# specified but it doesn't exist in db
            msg = 'Lead was not found in leadDb ({})'.format(hlApi.getVersion())
            note = JrINote("leadDbWarning", lead, msg, None, None)
            env.addNote(note)

            # provide info about PREV LEAD
            if (leadRowPrev is None):
                # generate warning that we have a previous lead id# specified but it doesn't exist in db
                msg = 'Lead was ALSO NOT found in PREVIOUS leadDb ({})'.format(hlApiPrev.getVersion())
                note = JrINote("leadDbWarning", lead, msg, None, None)
                env.addNote(note)
            else:
                # generate warning that about what it was in PREVIOUS db
                prevDbLabel = hlApiPrev.getNiceFullLabelWithAddress(leadRowPrev)
                msg = 'CAUTION! Lead WAS found in PREVIOUS leadDb () - {}: {}'.format(hlApiPrev.getVersion(), prevDbLabel)
                note = JrINote("leadDbWarning", lead, msg, None, None)
                env.addNote(note)

            return [label, subheading]

        # ok we got a row
        leadRowProperties = leadRow["properties"]
        dName = leadRowProperties["dName"]

        # warn on volatility
        isLeadRowFromVolatileDb = hlApi.isLeadRowSourceFromVolatileDb(sourceKey)
        if (isLeadRowFromVolatileDb):
            # generate warning that lead row is from volatile db that could change on new version
            msg = 'Lead is from a leadDb [{}:{}] that is volatile (could change on major directory update); consider submitting userdblead json to maintainers for locking.'.format(hlApi.getVersion(), sourceKey)
            note = JrINote("leadDbWarning", lead, msg, None, None)
            env.addNote(note)


        # auto address assign
        if (lead.calcLeadAddress()=="auto"):
            neighborhoodOption = "abbreviation"
            addressLine = hlApi.getNiceAddress(leadRow, neighborhoodOption, True)
            addressLineFirstPart = addressLine.split(",")[0].lower()
            if (addressLineFirstPart not in subheading.lower()):
                lead.setAddress(addressLine)

        if (subheading is None):
            msg = 'Lead {} has no descriptive label; in database as: \"{}\"'.format(leadIdNumberText, dName)
            note = JrINote("leadDbWarning", lead, msg, None, None)
            env.addNote(note)
        elif (not hlApi.leadRowHasSimilarLabel(leadRow, subheading)):
            # dissimilar warning
            msg = 'Lead label differs from database label: \"{}\"'.format(dName)
            note = JrINote("leadDbWarning", lead, msg, None, None)
            env.addNote(note)

        # warn about previous lead differences
        if (leadRowPrev is not None):
            leadRowPrevProperties = leadRowPrev["properties"]
            addressPrev = leadRowPrevProperties["address"]
            dNamePrev = leadRowPrevProperties["dName"]
            address = leadRowProperties["address"]
            dName = leadRowProperties["dName"]
            labelPrev = "{} @ {}".format(dNamePrev, addressPrev)
            labelNew = "{} @ {}".format(dName, address)
            if (labelNew != labelPrev):
                msg = "CAUTION! The old leaddb data ({} \"{}\") differs from new ({} \"{}\")".format(hlApiPrev.getVersion(), labelPrev,  hlApi.getVersion(), labelNew)
                note = JrINote("leadDbWarning", lead, msg, None, None)
                env.addNote(note)

        # record that we used it
        hlApi.addUsedLead(sourceKey, leadRow, lead)

        # done
        return [label, subheading]


    def preBuildPreRender(self, env):
        pass

    def postBuildPreRender(self, env):
        pass