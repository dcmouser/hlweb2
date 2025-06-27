# AST = Abstract Syntax Tree

# ast util classes
from .cblarkdefs import *

# these are our main ast work class so we bring in all helpers
from .cbtask import *
from .jrastfuncs import *
from .jrastvals import *
from .jriexception import *
from .cbplugin import DefPluginDomainEntryLeadProcessor

from . import cblocale

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint


# other defines
DefCbDefine_IDEmpty = ""
DefCbDefine_IdBlank = "BLANK"

DefEntryIdOptions = "OPTIONS"
DefEntryIdSetup = "SETUP"
DefSpecialEntryIdsAlwaysRunDontRender = [DefEntryIdOptions, DefEntryIdSetup]
DefSpecialEntryIdsEarlyRunWithOptions = [DefEntryIdOptions, DefEntryIdSetup]


# global counter for rid assignments to leads and sections, which we use to give unique labels and hyperref links
GlobalEidCounter = 0








































# root
class JrAstRoot (JrAst):
    def __init__(self, interp):
        super().__init__(None, None)
        #
        self.interp = interp
        self.prelimaryMatter = None
        self.endMatter = None
        #
        self.entries = JrAstEntryChildHelper(None, self)



    def printDebug(self, env, depth):
        # nice hierarchical tabbed pretty print
        super().printDebug(env, depth)
        # and now our entries
        self.entries.printDebug(env, depth+1)


    def loadCoreFunctions(self, env):
        # load functions from module
        from . import cbfuncs_core1, cbfuncs_core2
        env.loadFuncsFromModule(None, cbfuncs_core1)
        env.loadFuncsFromModule(None, cbfuncs_core2)

    def loadCorePlugins(self, interp, env):
        from . import cbplugins_lead
        cbplugins_lead.registerPlugins(interp.getPluginManager())




    def convertParseTreeToAst(self, env, parseTree):
        # given a LARK parse tree, convert it into OUR AST format

        # we go through a process of restructuring the parse tree to build a kind of AST (syntax tree) using standard python dictionaries
        # ATTN: can we use visitor/transform helper utilities from lark to do this all in a nicer way?

        # walk the parse tree and build out our itree hierarchy which organizes the parse tree by section -> child -> subchild
        # but all the BODY's of entries (and options) remained in parse tree form, just reorganized into our dictionary hierarchy
        # the main benefit at this point is all entries with IDs are sorted into their sections, so we can easily FIND an entry by its id

        # Note we need env here so that we can pass to convertTopLevelItemStoreAsChild for error handling

        # walk the children at root, which should be entries
        pchildren = parseTree.children
        for pchild in pchildren:
            self.convertTopLevelItemStoreAsChild(env, pchild)


    def convertTopLevelItemStoreAsChild(self, env, pnode):
        # top level can only be preliminary_matter, end_matter, or an entry
        # Note we need env here so that we can pass to convertEntryAddMergeChildAst
        rule = getParseNodeRuleNameSmart(pnode)
        if (rule == JrCbLarkRule_preliminary_matter):
            self.prelimaryMatter = self.convertGenericPnodeContents(pnode)
        elif (rule == JrCbLarkRule_end_matter):
            self.endMatter = self.convertGenericPnodeContents(pnode)
        elif (rule in [JrCbLarkRule_level1_entry, JrCbLarkRule_overview_level1_entry]):
            self.entries.convertEntryAddMergeChildAst(env, pnode, 1)
        else:
            # this shouldn't happen as parser should catch it
            raise makeJriException("Uncaught syntax error; expected top level item to be from {}.".format([JrCbLarkRule_preliminary_matter, JrCbLarkRule_end_matter, JrCbLarkRule_level1_entry, JrCbLarkRule_overview_level1_entry]), pnode)






    def taskRenderRun(self, env, task, flagFullRender):
        # when "run" (interpretting) casebook code, functions may behave differently based on the TARGET OUTPUT
        # that is, we may be targetting latex, html, etc; and the FUNCTIONS may need to know that
        # we accomplish this with the use of some global variables/constants

        #
        env.setTask(task)
        rmode = task.getRmode()

        # stage 0
        # ATTN: IMPORTANT - first tell jrinterp to clear all render helpers (so that we can run multiple tasks without them building data on top of each other)
        env.getInterp().resetDataForRender(env)

        # new, set variables based on task
        self.imposeTaskOptionsEnvironmentVariables(task, env)

        # stage 1
        self.stage1RenderRunApplyOptionsRecursively(task, rmode, env)

        if (flagFullRender):
            # stage 2
            env.getInterp().postBuildPreRender(env)

            # stage 3
            self.stage2RenderRun(task, rmode, env)

            # stage 4 - let RENDERER doc do some final stuff
            renderer = env.getRenderer()
            renderer.afterTaskRenderRunProcess(task, rmode, env)




    def imposeTaskOptionsEnvironmentVariables(self, task, env):
        # there are options that the user can configure in their casebook file, which we can OVERWRITE in task options
        #
        sectionBreak = task.getOption("sectionBreak", None)
        sectionColumns = task.getOption("sectionColumns", None)
        leadBreak = task.getOption("leadBreak", None)
        leadColumns = task.getOption("leadColumns", None)
        #
        if (sectionBreak is not None):
            env.setCreateEnvValue(None, "taskLeadSectionBreak", sectionBreak, False, False)
        if (sectionColumns is not None):
            env.setCreateEnvValue(None, "taskLeadSectionColumns", sectionColumns, False, False)
        if (leadBreak is not None):
            env.setCreateEnvValue(None, "taskLeadBreak", leadBreak, False, False)
        if (leadColumns is not None):
            env.setCreateEnvValue(None, "taskLeadColumns", leadColumns, False, False)





    # note the two-stage process here; this is so that OPTIONS and SETUP sections are fully renderRun FIRST, which can INFORM the process of resolving OPTIONS for all other entries
    # then we can proceed linearly and run every other entry after all entry options have been processed
    # we do this so that all entries options are processed before we "run" most (except special setup and options)

    def stage1RenderRunApplyOptionsRecursively(self, task, rmode, env):
        # apply options to special entries
        for child in self.entries.childList:
            if (child.calcIsEarlyOptionsEntry()):
                # this entry should renderRun (run) and ONLY renderRun during this special apply options stage (see below)
                # this should include options and setup
                child.renderRun(DefRmodeRun, env, child, None, False)
            # apply options recursively
            child.applyOptionsRecursively(rmode, env)

        # language translation
        self.configureSetupLocaleTranslation(env)

        # now that options are processed, we might do things that depend on options being set (such as setting up the hlapi)
        self.configureHlApi(env)

        # AND now we can sort tags, since all tags should have been defined by now
        tagManager = env.getTagManager()
        tagManager.postProcessTagsIfNeeded(env)



    def stage2RenderRun(self, task, rmode, env):
        # walk children ENTRIES and "run" each (they will store their output locally inside them)
        for child in self.entries.childList:
            if (child.calcIsEarlyOptionsEntry()):
                # this entry should ONLY renderRun during special apply options stage (see abpve)
                pass
            elif (child.calcIsSpecialEntryAlwaysRunDontRender()):
                # if its a special options or setup, then we always RUN it even if we are otherwise RENDERING
                child.renderRun(DefRmodeRun, env, child, None, False)
            else:
                child.renderRun(rmode, env, child, None, False)






    def configureHlApi(self, env):
        # get any configured data options
        # main lead data
        interp = env.getInterp()
        leadDbData = env.getEnvValueUnwrapped(None, "leadDbData", None)
        dataVersion = jrfuncs.getDictValueOrDefault(leadDbData, "version", None)
        dataVersionPrevious = jrfuncs.getDictValueOrDefault(leadDbData, "versionPrevious", None)
        seed = jrfuncs.getDictValueOrDefault(leadDbData, "seed", None)
        #
        if (dataVersion is not None):
            hlApiOptions = {"dataVersion": dataVersion, "seed": seed}
            interp.getHlApi().configure(hlApiOptions)
        #
        if (dataVersionPrevious is not None) and (dataVersionPrevious!=""):
            hlApiOptions = {"dataVersion": dataVersionPrevious, "seed": seed}
            interp.getHlApiPrev().configure(hlApiOptions)
        else:
            interp.getHlApiPrev().setDisabled(True)




    def configureSetupLocaleTranslation(self, env):
        localeData = env.getEnvValueUnwrapped(None, "localeData", None)
        language = jrfuncs.getDictValueOrDefault(localeData, "language", None)
        cblocale.changeLanguage(language)




    def findEntryByIdPath(self, id, astloc):
        # find and return the lead with matching id (id path)
        # ATTN: we want to throw exception if multiple matching ids
        # ATTN: path should of form PARENTID > CHILDID (we can't use dot notation since ids may be dotted)
        idParts = id.split(">")
        parentp = self
        descendant = None
        for idPart in idParts:
            idPart = idPart.strip()
            descendant = parentp.entries.findDescendantByIdOrLabel(idPart, astloc)
            if (descendant is None):
                # not found
                return None
                #raise makeJriException("Could not find referenced entry with id ({}) with path ({})".format(idPart, id), astloc)
            parentp = descendant
        # ok we found it
        return descendant











# entries (our main things)
class JrAstEntry(JrAst):
    def __init__(self, sloc, parentp, level):
        super().__init__(sloc, parentp)
        self.level = level
        #
        #self.idOriginal = None
        self.autoId = None
        self.id = None
        self.label = None
        self.options = None
        self.bodyBlockSeqs = []
        #
        # options set
        self.isAutoLead = False
        self.copyFrom = None
        self.shouldRender = True
        self.continuedFromLead = None
        # no defaults
        self.leadColumns = None
        self.sectionColumns = None
        self.toc = None
        self.childToc = None
        self.heading = None
        self.childPlugins = None
        #
        # global rid
        global GlobalEidCounter
        GlobalEidCounter += 1
        self.rid = "e" + str(GlobalEidCounter)
        #
        self.headingStyle = None
        self.childHeadingStyle = None
        self.layout = None
        self.blankHead = False
        self.time = None
        self.timePos = None
        self.dividers = None
        self.mStyle = None
        self.address = None
        self.dName = None
        #
        self.sectionBreak = None
        self.leadBreak = None
        #
        self.sortGroup = None
        self.sortKey = None
        #
        self.multiPage = None
        #
        self.entries = JrAstEntryChildHelper(self, self)


    def printDebug(self, env, depth):
        # nice hierarchical tabbed pretty print
        super().printDebug(env, depth, "LEVEL {}".format(self.level))
        astPrintDebugLine(depth+1, "ID: " + self.getId())
        astPrintDebugLine(depth+1, "LABEL: " + self.getLabelOrBlank())
        if (self.options is not None):
            self.options.printDebug(env, depth+1)

        # blocks
        if (len(self.bodyBlockSeqs)>0):
            astPrintDebugLine(depth+1, "BLOCK SEQS ({}):".format(len(self.bodyBlockSeqs)))
            for blockseq in self.bodyBlockSeqs:
                blockseq.printDebug(env, depth+2)

        # children entries
        self.entries.printDebug(env, depth+1)


    def calcIsEarlyOptionsEntry(self):
        # return True if we are a special options or setup entry
        if (self.id in DefSpecialEntryIdsEarlyRunWithOptions):
            return True
        return False
 
    def calcIsSpecialEntryAlwaysRunDontRender(self):
        # return True if we are a special options or setup entry
        if (self.id in DefSpecialEntryIdsAlwaysRunDontRender):
            return True
        return False


    def getDisplayIdLabel(self):
        return "{}:'{}'".format(self.getId(), self.getLabelOrBlank())
    
    def getRuntimeDebugDisplay(self, env, entryp, leadp):
        return "ENTRY {}:{} (level {})".format(self.getId(), self.getLabelOrBlank(), self.level)

    def setId(self, val):
        #if (self.idOriginal is None):
        #    # remember idOriginal, a bit of a kludge
        #    self.idOriginal = self.id
        self.id = val
    def getId(self):
        return self.id

    def getAutoId(self):
        return self.autoId
    def setAutoId(self, val):
        self.autoId = val

    def getMindMapNodeInfo(self):
        id = self.getId()
        label = self.label
        if (id is None) or (id==""):
            nodeLabel = label
        elif (label is None) or (label==""):
            nodeLabel = id
        else:
            nodeLabel = "{}:{}".format(id,label)
        #
        # kludge to remove unnesc. placeholder text.
        #nodeLabel = nodeLabel.replace(DefInlineLeadPlaceHolder, "")
        #
        mStyle = self.calcHierarchicalMStyle()
        #
        mmInfo = {
            "id": "ENTRY.{}".format(self.rid),
            "label": nodeLabel,
            "type": "entry",
            "pointer": self,
            "mStyle": mStyle,
            "showDefault": False,
            }
        return mmInfo
    
    def setLabel(self, val):
        self.label = val
    def getLabel(self):
        return self.label
    def getLabelOrBlank(self):
        if (self.label is None):
            return ""
        return self.label
    def getLevel(self):
        return self.level

    def getRid(self):
        return self.rid

    def calcDisplayTitle(self):
        title = self.label
        if (title is None):
            title = self.getId()
        return title

    def setOptions(self, pnode):
        self.options = JrAstArgumentList(pnode, self)

    def setIsAutoLead(self, val):
        self.isAutoLead = val
    def getIsAutoLead(self):
        return self.isAutoLead
    def setCopyFrom(self, val):
        self.copyFrom = val
    def getCopyFrom(self):
        return self.copyFrom
    def setShouldRender(self, val):
        self.shouldRender = val
    def getShouldRender(self):
        return self.shouldRender
    def setContinuedFromLead(self, val):
        self.continuedFromLead = val
    def getContinuedFromLead(self):
        return self.continuedFromLead
    def setMStyle(self, val):
        self.mStyle = val
    def getMStyle(self):
        return self.mStyle
    def calcHierarchicalMStyle(self):
        val = self.mStyle
        if (val is None) and (self.parentp is not None):
            val = self.parentp.calcHierarchicalMStyle()
        return val

    def getLeadColumns(self):
        return self.leadColumns
    def getSectionColumns(self):
        return self.sectionColumns
    def setLeadColumns(self, val):
        self.leadColumns = val
    def setSectionColumns(self, val):
        self.sectionColumns = val
    def getLeadBreak(self):
        return self.leadBreak
    def getSectionBreak(self):
        return self.sectionBreak
    def setLeadBreak(self, val):
        self.leadBreak = val
    def setSectionBreak(self, val):
        self.sectionBreak = val
    def getToc(self):
        return self.toc
    def setToc(self, val):
        self.toc = val
    #
    def getChildToc(self):
        return self.childToc
    def setChildToc(self, val):
        self.childToc = val


    def setHeadingStyle(self, val):
        self.headingStyle = val
    def getHeadingStyle(self):
        return self.headingStyle
    def setChildHeadingStyle(self, val):
        self.childHeadingStyle = val
    def getChildHeadingStyle(self):
        return self.childHeadingStyle

    def setBlankHead(self, val):
        self.blankHead = val
    def getBlankHead(self):
        return self.blankHead
    def setLayout(self, val):
        self.layout = val
    def getLayout(self):
        return self.layout


    def getTime(self):
        return self.time
    def setTime(self, val):
        self.time = val
    def getTimePos(self):
        return self.timePos
    def setTimePos(self, val):
        self.timePos = val

    def getHeading(self):
        return self.heading
    def setHeading(self, val):
        self.heading = val

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

    def getSortGroup(self):
        return self.sortGroup
    def getSortKey(self):
        return self.sortKey
    def setSortGroup(self, val):
        self.sortGroup = val
    def setSortKey(self, val):
        self.sortKey = val

    def getMultiPage(self):
        return self.multiPage
    def setMultiPage(self, val):
        self.multiPage = val

    def getParentEntry(self):
        parentp = self.getParentp()
        if (parentp is None) or (not isinstance(parentp, JrAstEntry)):
            return None
        return parentp

    def getChildPlugins(self):
        return self.childPlugins
    def setChildPlugins(self, val):
        self.childPlugins = val

    def shouldEntryIdBeUnique(self):
        # ATTN: note that options have not been processed yet, so getBlankHead() is not a reliable check
        id = self.getId()
        if (self.getBlankHead()) or (id in [DefCbDefine_IdBlank, DefCbDefine_IDEmpty]):
            return False
        return True

    def getMarkdownLabel(self):
        displayLabel = self.calcDisplayTitle()
        return "{} {}".format("#" * self.level, displayLabel)


    def addAstBodyBlockSeq(self, blockSeq):
        self.bodyBlockSeqs.append(blockSeq)

    def mergeNewBodyBlockSeqsFrom(self, otherEntry):
        for blockSeq in otherEntry.bodyBlockSeqs:
            self.addAstBodyBlockSeq(blockSeq)



    # helper function to get the ID of an entry node, which may be explicitly provided; we use label if no id
    def getEntryIdFallback(self, defaultVal):
        id = self.getId()
        if (jrfuncs.isNonEmptyString(id)):
            return id
        label = self.getLabel()
        if (jrfuncs.isNonEmptyString(label)):
            return label
        # defulat
        return defaultVal


    def convertCoreFromPnode(self, pnode):
        # Convery core from pnode to ast node, but NOT children (yet)
        # make sure we got what we expected
        verifyPNodeType(pnode, "adding entry children", [JrCbLarkRule_level1_entry, JrCbLarkRule_level2_entry, JrCbLarkRule_level3_entry, JrCbLarkRule_overview_level1_entry])

        # first two children of node are head and body
        pchildCount = len(pnode.children)
        if (pchildCount<2):
            raise makeJriException("Uncaught syntax error; expected first two children of parent entry to be header and body, but didn't find even these 2.", pnode)

        # head
        thisHeadPnode = pnode.children[0]
        verifyPNodeType(thisHeadPnode, "processing entry head", [JrCbLarkRule_entry_header, JrCbLarkRule_entry_header_overview])
        self.convertStoreHeaderInfo(thisHeadPnode)

        # body (may be None)
        thisBodyPnode = pnode.children[1]
        verifyPNodeType(thisBodyPnode, "processing entry body", [JrCbLarkRule_entry_body])
        self.convertAddBodyBlockSeq(thisBodyPnode)





    def convertStoreHeaderInfo(self, pnode):
        # process an entry header; this uses a parse tree grammar for specifying id, label, options
        for pchild in pnode.children:
            pchildValue = pchild.data.value
            expectList = [JrCbLarkRule_entry_id_opt_label, JrCbLarkRule_overview_level1_id, JrCbLarkRule_overview_level1_id]
            if (pchildValue in expectList):
                for achild in pchild.children:
                    achildValue = achild.data.value
                    if (achildValue in [JrCbLarkRule_overview_entry_id]):
                        self.setId(getParseTreeChildLiteralToken(achild))
                    elif (achildValue in [JrCbLarkRule_entry_id]):
                        self.setId(getParseTreeChildLiteralTokenOrString(achild))
                    elif (achildValue == JrCbLarkRule_entry_label):
                        val = getParseTreeChildStringOrTextLine(achild)
                        self.setLabel(val)
                    elif (achildValue == JrCbLarkRule_entry_linelabel):
                        val = getParseTreeEntryLineLabel(achild)
                        self.setLabel(val)
                    else:
                       raise makeJriException("Uncaught syntax error; expected to find {}.".format([JrCbLarkRule_entry_id, JrCbLarkRule_overview_entry_id, JrCbLarkRule_entry_label, JrCbLarkRule_overview_level1_id]), pchild)
            elif (pchildValue == JrCbLarkRule_entry_options):
                # options come as an argument list which is child 0 of options; nothing else
                optionsArgumentListNode = pchild.children[0]
                self.setOptions(optionsArgumentListNode)
            else:
                # this shouldnt happen because parser should flag it
                raise makeJriException("Uncaught syntax error; expected to find entry header element from {}.".format([JrCbLarkRule_entry_id_opt_label, JrCbLarkRule_overview_level1_id, JrCbLarkRule_entry_options]), pchild)

        # ATTN: 2/1/25: Fixup for blank IDs
        # if we just have a label, and no id, this is a kludge in the syntax parser and we treat this as the ID not the label
        label = self.getLabel()
        id = self.getId()
        if (id=="") and (label!="") and (label is not None):
            # move label to id, and clear label?
            self.setId(label)
            # should we really clear label or leave it same as id?
            if (False):
                self.setLabel("")



    def convertAddBodyBlockSeq(self, node):
        # just add the entire node as the body
        bodyContent = node.children[0]
        # find the block seq (may be None)
        if (bodyContent is not None):
            blockSeq = JrAstBlockSeq(bodyContent, self)
            self.addAstBodyBlockSeq(blockSeq)


    def applyOptionsRecursively(self, rmode, env):
        # now apply options to all
        self.applyOptionsAndPluginsOnEntries(env, self.options)
        # now for children
        for child in self.entries.childList:
            child.applyOptionsRecursively(rmode, env)


    def applyOptionsAndPluginsOnEntries(self, env, optionsArgList):
        if (self.options is None):
            # no options to set -- but we would like to call on empty args for default
            optionsArgList = JrAstArgumentList(None, self)
        else:
            optionsArgList = self.options

        # we implement this by calling a special FUNCTION, and invoking it by passing argList, AND this entry as a special arg
        functionName = "_entryApplyOptions"
        # so this code looks much like the normal function execution
        funcVal = env.getEnvValue(self, functionName, None)
        if (funcVal is None):
            raise makeJriException("Internal error; could not find special entry options function '{}' in environment.".format(functionName), self)
        funcp = funcVal.getWrappedExpect(AstValFunction)

        # force pointer to us (no longer used, we pass entry into the invoke now)
        #optionsArgList.setNamedArgValue("_entry", AstValObject(self.getSourceLoc(), self, self, False, True))

        # invoke it (alwaysin run mode)
        retv = funcp.invoke(DefRmodeRun, env, self, None, self, optionsArgList, [])

        # and now run any plugins
        self.runPluginsOnEntry(env)

        # ignore return value
        return retv



    def runPluginsOnEntry(self, env):
        #
        try:
            parentEntry = self.getParentEntry()
            if (parentEntry is not None):
                parentChildPlugins = parentEntry.getChildPlugins()
                if (parentChildPlugins is not None):
                    pluginIds = parentChildPlugins.split(",")
                    for pluginId in pluginIds:
                        pluginManager = env.getPluginManager()
                        plugin = pluginManager.findPluginById(DefPluginDomainEntryLeadProcessor, pluginId)
                        if (plugin is None):
                            raise makeJriException("Unknown plugin '{}:{}' in runPluginsOnEntry".format(DefPluginDomainEntryLeadProcessor, pluginId), self)
                        # all plugin run their "processLead" function (which might change label, etc.)
                        plugin.processEntry(env, self, parentEntry)
        except Exception as e:
            e = makeModifyJriExceptionAddLocIfNeeded(e, self, None)
            interp = env.getInterp()
            if (interp.getFlagContinueOnException()):
                interp.displayException(e, True)
            else:
                raise e



    def renderRun(self, rmode, env, entryp, inleadp, optionJustReturnResults):
        # Entry run
        # Entries are where we collect and store output -- their children blocks do not need to store output long term
        # an entry is made up of some BODIES (text inside it), and possible collection of CHILDREN ENTRIES
        # A level 1 entry is a SECTION (e.g. "Day1" or "Leads" or "Hints" or "Documents" or "Cover", etc.)
        # A level 2 entry is a LEAD
        # A level 3 entry might be a sub-lead
        #

        # level of this entry (1 = section, 2 = lead)
        level = self.getLevel()
        # build output
        resultList = JrAstResultList()

        #jrprint("RenderRun ({}): {}".format(rmode, self.getRuntimeDebugDisplay(env, entryp, inleadp)))

        renderer = env.getRenderer()
        addOutputToRenderer = (not self.calcIsSpecialEntryAlwaysRunDontRender())

        if (not self.getShouldRender()):
            # setting this means we will NOT add a renderlead for this entry
            # ATTN: new 6/13/25 - we dont have to use this since we check below when iterating children
            if False and (not optionJustReturnResults) and (not addOutputToRenderer):
                # this means we are rendering ourselves AND we are a render = false
                # so if we are not being embedded, and we are not a special no-render
                # then we should not even run?
                # ATTN: maybe better to check this when just dumping leads in a section?
                return AstValNull(None, entryp)
            optionJustReturnResults = True


        doCreateRenderBase = (addOutputToRenderer) and (not optionJustReturnResults) and (renderer is not None)

        # we wrap this childs renderrunning in a try catch exception in case we want to catch exceptions as warnings
        renderBase = inleadp
        try:
            # get renderer (if not None)

            # create lead early so that we can pass it around in renderrun (it will not have its contents yet)
            if doCreateRenderBase:
                # create the lead or section (both derived from renderBase)
                if (level == 1):
                    # create and add it (we need to add it now because child lead might be recursively created and need to access it)
                    renderBase = renderer.createSectionFromEntry(self, env)
                    renderer.addSection(renderBase)
                elif (level == 2):
                    # create this lead; no need to add it yet?
                    renderBase = renderer.createLeadFromEntry(self, env)

            if (level > 2):
                # when we are an entry bigger than level 2, we basically just use our label as a markdown header; as if it were just a text item
                retv = "\n\n" + self.getMarkdownLabel() + "\n\n"
                resultList.flatAdd(retv)

            # BODY of this entry
            for blockSeq in self.bodyBlockSeqs:
                retv = blockSeq.renderRun(rmode, env, self, renderBase)
                resultList.flatAdd(retv)

        except Exception as e:
            e = makeModifyJriExceptionAddLocIfNeeded(e, self, None)
            interp = env.getInterp()
            if (interp.getFlagContinueOnException()):
                interp.displayException(e, True)
            else:
                raise e


        # CHILDREN ENTRIES (RECURSIVE CALL)
        for child in self.entries.childList:
            childShouldRenderFlag = child.getShouldRender()
            if (not childShouldRenderFlag):
                # ATTN: new 6/13/25 - when walking children we do not render this; these only get rendered on explicit embed
                continue
            retv = child.renderRun(rmode, env, self, renderBase, optionJustReturnResults)
            if (addOutputToRenderer) or (optionJustReturnResults):
                if (level > 1):
                    resultList.flatAdd(retv)


        # copy contents from another entry?
        # this is VERY similar to the cbfuncs_core function embedLead, with the exception of a shorthand copy="next" statement
        copyFromId = self.getCopyFrom()
        if (copyFromId is not None):
            if (copyFromId=="next"):
                parentp = self.getParentEntry()
                copyEntry = parentp.getNextNonCopyChildEntry(self, env)
            else:
                copyEntry = env.findEntryByIdPath(id, self)
            if (copyEntry is not None):
                # add contents
                resultList.flatAdd(copyEntry.renderRun(rmode, env, self, renderBase, True))
            else:
                raise makeJriException("Entry is marked as copyFrom ({}) but could not find it".format(copyFromId), self)


        # if its level 2 lead, then create lead from contents
        if doCreateRenderBase:
            if (level == 2):
                renderer.fileLeadWithBlockList(env, self, renderBase, resultList)
            elif (level == 1):
                # save built up contents of section
                renderBase.setBlockList(resultList)

        if (level > 2) or (optionJustReturnResults):
            # bigger than level 2 its just the resultList we return which will be added to the higher level lead
            return resultList
        else:
            return None



    def getNextNonCopyChildEntry(self, entryp, env):
        # walk children, find US, then get next child without a copy = next
        return self.entries.getNextNonCopyChildEntry(entryp, env)





























class JrAstBlockSeq(JrAst):
    def __init__(self, blockSeqPnode, parentp):
        super().__init__(blockSeqPnode, parentp)
        #
        self.blocks = []
        #
        if (blockSeqPnode is not None):
            self.addBlocksFromBlockSeqPnode(blockSeqPnode)
    
    def printDebug(self, env, depth):
        # nice hierarchical tabbed pretty print
        super().printDebug(env, depth)
        # now our child blocks
        for block in self.blocks:
            block.printDebug(env, depth+1)



    def addBlocksFromBlockSeqPnode(self, blockSeqPnode):
        verifyPNodeType(blockSeqPnode, "block sequence", JrCbLarkRuleList_BlockSeqs)
        for pchild in blockSeqPnode.children:
            pchildData = pchild.data
            if (pchildData == JrCbLarkRule_Block_Newline):
                block = JrAstNewline(pchild, self)
            else:
                block = self.makeConvertDerivedBlock(pchild)
            self.blocks.append(block)


    
    def makeConvertDerivedBlock(self, blockpnode):
        # must be child
        blockpnode = blockpnode.children[0]
        rule = getParseNodeRuleNameSmart(blockpnode)
        if (rule == JrCbLarkRule_Block_Text):
            return JrAstBlockText(blockpnode, self)    
        elif (rule == JrCbLarkRule_Block_FunctionCall):
            return JrAstFunctionCall(blockpnode, self)
        elif (rule == JrCbLarkRule_Block_ControlStatement):
            return self.makeConvertControlStatement(blockpnode)
        elif (rule == JrCbLarkRule_Block_Expression):
            return JrAstExpression(blockpnode, self)  
        # not understood
        raise makeJriException("Internal rrror: Expected to process a block of type {} but got '{}'.".format([JrCbLarkRule_Block_FunctionCall, JrCbLarkRule_Block_Text, JrCbLarkRule_Block_ControlStatement, JrCbLarkRule_Block_Expression], rule), blockpnode)



    def makeConvertControlStatement(self, pnodeControlStatement):
        # make derived control statement
        pnode = pnodeControlStatement.children[0]
        rule = getParseNodeRuleNameSmart(pnode)
        if (rule == JrCbLarkRule_if_statement):
            return JrAstControlStatementIf(pnode, self)  
        elif (rule == JrCbLarkRule_for_statement):
            return JrAstControlStatementFor(pnode, self)  
        raise makeJriException("Internal error: Uknown control statement expected {} got '{}'.".format([JrCbLarkRule_if_statement,JrCbLarkRule_for_statement], rule), pnode)



    def renderRun(self, rmode, env, entryp, leadp):
        # Body render

        # render all the blocks in squence (note that a "block" could be various things, including a function call, a text block, etc.)
        resultList = JrAstResultList()
        for block in self.blocks:
            retv = block.renderRun(rmode, env, entryp, leadp)
            resultList.flatAdd(retv)
        
        return resultList




















































# fundamental building blocks

class JrAstBlockText(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        # store text
        self.text = getParseNodeTokenValue(pnode.children[0])


    def renderRun(self, rmode, env, entryp, leadp):
        #jrprint("Running ({}) BLOCKTEXT statement at {}".format(rmode, self.sloc.debugString()))
        retv = self.text
        return retv
































class JrAstFunctionCall(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        childCount = len(pnode.children)
        functionNameNode = pnode.children[0]
        argumentListNode = pnode.children[1]
        # now target brace groups
        if (childCount>3):
            raise makeJriException("Internal error: Expected 2 or 3 children for function call parse.", pnode)
        if (childCount==3):
            multiBraceGroupNode = pnode.children[2]
        else:
            multiBraceGroupNode = None
        #
        functionNameStr = functionNameNode.value
        self.functionName = functionNameStr
        self.argumentList = JrAstArgumentList(argumentListNode, self)
        if (multiBraceGroupNode is None):
            self.targetGroups = []
        else:
            self.targetGroups = convertParseMultiBraceGroupOrBlockSeq(multiBraceGroupNode, self)
        
        # ATTN:
        # note that at this point we have NOT evaluated/resolved the arguments or blocks -- they are simply stored as AST nodes -- uncomputed/unevaluated expressions that have no types, and could result in runtime errors, etc.,
        # they may in fact have recursive function calls inside the args, etc.
        # in fact we can't resolve them yet because we have no runtime environment/context


    def printDebug(self, env, depth):
        # nice hierarchical tabbed pretty print
        super().printDebug(env, depth, "{}(..)".format(self.getFunctionName()))


    def getRuntimeDebugDisplay(self, env, entryp, leadp):
        niceCallString = self.calcResolvedArgListWithDetailsForDebug(env, entryp, leadp)
        return "FUNCTION {}".format(niceCallString)


    def getFunctionName(self):
        return self.functionName


    def calcResolvedArgListWithDetailsForDebug(self, env, entryp, leadp):
        # to aid in debugging

        # get function pointer
        funcp = self.resolveFuncp(env)
        functionName = self.getFunctionName()

        # ask for the arg list
        compileTimeArgListString = self.argumentList.asDebugStr()
        annotatedArgListString = funcp.calcAnnotatedArgListStringForDebug(env, self, self.argumentList, self.targetGroups, entryp, leadp)
        return "{}({}) --> {}({})".format(functionName, compileTimeArgListString, functionName, annotatedArgListString)


    def resolveFuncp(self, env):
        # get function pointer
        functionName = self.getFunctionName()
        funcVal = env.getEnvValue(self, functionName, None)
        if (funcVal is None):
            msg = "Runtime error; Attemped to invoke undefined function: ${}(..).".format(self.getFunctionName())
            didYouMean = env.findDidYouMeanFunction(functionName)
            if (didYouMean is not None):
                msg += " Did you mean: " + didYouMean + "?"
            raise makeJriException(msg, self)
        funcp = funcVal.getWrappedExpect(AstValFunction)
        return funcp


    def resolve(self, env, flagResolveIdentifiers, entryp, leadp):
        # most value return themselves
        rmode = DefRmodeRun
        retv = self.execute(rmode, env, entryp, leadp)
        return retv


    def renderRun(self, rmode, env, entryp, leadp):
        #invoke the function

        funcRetVal = None
        funcRetVal = self.execute(rmode, env, entryp, leadp)
        return funcRetVal


    def execute(self, rmode, env, entryp, leadp):
        # execute the function, return an AstVal

        # get function pointer
        funcp = self.resolveFuncp(env)

        # invoke it
        retv = funcp.invoke(rmode, env, entryp, leadp, self, self.argumentList, self.targetGroups)

        # wrap return value
        if (rmode == DefRmodeRender):
            # if we are rendering, then we just return result of render (a renderlist or a string; rather than wrap it)
            funcRetVal = retv
        else:
            funcRetVal = wrapValIfNotAlreadyWrapped(self, self, retv)

        return funcRetVal







































class JrAstControlStatementIf(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        expressionNode = pnode.children[0]
        self.ifExpression = JrAstExpression(expressionNode, self)
        self.consequenceTrue = None
        self.elseIf = None
        self.consequenceElse = None
        consequenceNode = pnode.children[1]
        self.convertConsequenceSet(consequenceNode)
        pass

    def convertConsequenceSet(self, consequenceSetNode):
        # set other parts of if
        verifyPNodeType(consequenceSetNode, "if_consequence", [JrCbLarkRule_if_consequence])
        consequenceChildNode = consequenceSetNode.children[0]
        self.consequenceTrue = convertParseBraceGroupOrBlockSeq(consequenceChildNode, self)
        # now if there is ANOTHER child it is EITHER an elif or an else
        childCount = len(consequenceSetNode.children)
        if (childCount>1):
            elseChildNode = consequenceSetNode.children[1]
            rule = getParseNodeRuleNameSmart(elseChildNode)
            if (rule == JrCbLarkRule_elif_statement):
                elseIfChildNode = elseChildNode.children[0]
                self.elseIf = JrAstControlStatementIf(elseIfChildNode, self)
            elif (rule == JrCbLarkRule_else_statement):
                elseConsquenceNode = elseChildNode.children[0]
                self.consequenceElse = convertParseBraceGroupOrBlockSeq(elseConsquenceNode, self)
            else:
                raise makeAstExceptionPNodeType("if consequence set", elseChildNode, [JrCbLarkRule_elif_statement, JrCbLarkRule_else_statement])
        

    def renderRun(self, rmode, env, entryp, leadp):
        jrprint("run IF statement")

        consequenceResult = None

        # evaluate expression
        expressionResultVal = self.ifExpression.resolve(env, True, entryp, leadp)
        # is it true?
        evaluatesTrue = expressionResultVal.getWrappedExpect(AstValBool)
        if (evaluatesTrue):
            # run the consequence
            consequenceResult = self.consequenceTrue.renderRun(rmode, env, entryp, leadp)
        else:
            # at most one if these can be non-None (possibly both)
            if (self.elseIf is not None):
                # we have an else if IF
                consequenceResult = self.elseIf.renderRun(rmode, env, entryp, leadp)
            elif (self.consequenceElse is not None):
                consequenceResult = self.self.consequenceElse.renderRun(rmode, env, entryp, leadp)
            else:
                # nothing to do
                pass

        # ATTN: unfinished; return consequenceResult
        return consequenceResult




















class JrAstControlStatementFor(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        forExpressionNode = pnode.children[0]
        verifyPNodeType(forExpressionNode, "for expression", [JrCbLarkRule_for_expression_in])
        # identifier that will loop through list
        identifierNameNode = forExpressionNode.children[0]
        self.identifierName = getParseNodeTokenValue(identifierNameNode)
        # expression which will HAVE to evaluate at runtime into a list
        expressionNode = forExpressionNode.children[1]
        self.inExpression = JrAstExpression(expressionNode, self)
        # consequence loop
        consequenceNode = pnode.children[1]
        self.loopConsequence = convertParseBraceGroupOrBlockSeq(consequenceNode, self)


    def renderRun(self, rmode, env, entryp, leadp):
        jrprint("RenderRun ({}) FOR statement - ATTN: UNFINISHED".format(rmode))
        retv = None
        return retv













































# JrAstArgumentList represents two lists of arguments being passed to a function, a positional and named list
# note that this is a JrAst derived class, meaning that it is not a general utility class but rather a node created from parse tree (ie an argument list found in the source parse)
class JrAstArgumentList(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        self.positionalArgs = []
        self.namedArgs = {}
        #
        if (pnode is not None):
            verifyPNodeType(pnode, "parsing argument list", [JrCbLarkRule_argument_list])
            # walk children
            for childpnode in pnode.children:
                verifyPNodeType(childpnode, "parsing argument child list", [JrCbLarkRule_positional_argument_list, JrCbLarkRule_named_argument_list])
                childData = childpnode.data
                if (childData == JrCbLarkRule_positional_argument_list):
                    self.positionalArgs = convertPositionalArgList(childpnode, self)
                elif (childData == JrCbLarkRule_named_argument_list):
                    self.namedArgs = convertNamedArgList(childpnode, self)


    def asDebugStr(self):
        parts = []
        for arg in self.positionalArgs:
            simpleArgStr = arg.asDebugStr()
            parts.append(simpleArgStr)
        for key,arg in self.namedArgs.items():
            simpleArgStr = "{}={}".format(key, arg.asDebugStr())
            parts.append(simpleArgStr)
        niceString = ", ".join(parts)
        return niceString


    def getPositionArgs(self):
        return self.positionalArgs
    def getNamedArgs(self):
        return self.namedArgs

    def setNamedArgValue(self, argName, value):
        self.namedArgs[argName] = value



























class JrAstNewline(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        # nothing else to do here, it's just a newline that may be significant for text production


    def renderRun(self, rmode, env, entryp, leadp):
        #jrprint("RenderRun ({}) NEWLINE statement".format(rmode))
        return "\n"



















# brace group is just like a block sequence
# currently we just handle the functionality in base blockSeq class
class JrAstBraceGroup(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        # a brace group just always contains a block seq
        if (len(pnode.children)==1):
            self.blockSeq = JrAstBlockSeq(pnode.children[0], self)
        elif (len(pnode.children)==0):
            # empty
            self.blockSeq = None
        else:
            raise makeJriException("Expected a blockseq inside a brace group.", pnode)

    def renderRun(self, rmode, env, entryp, leadp):
        #jrprint("RenderRun ({}) BraceGroup".format(rmode))
        if (self.blockSeq is None):
            return ""
        return self.blockSeq.renderRun(rmode, env, entryp, leadp)









































# expressions, simple or complext
# this will require quite a bit of work
# but i think rules are always going to be 1 or 2 children
# ATTN: unfinished
# JrAstExpression currently just wraps a specific operation/atom
class JrAstExpression(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        self.element = convertExpression(pnode, self)


    def asDebugStr(self):
        # IF the expression is JUST a wrapped value, return that
        atomicVal = self.getAstValOrNoneIfComplex()
        if (atomicVal is not None):
            return atomicVal.asDebugStr()
        # fallback to just reportign class
        return "CompoundExpression"

    def getAstValOrNoneIfComplex(self):
        # return the astAval if its a simple expression
        element = self.element
        if (isinstance(element, AstVal)):
            return element
        # atomic expressions is same thing, a single value wrapped
        if (isinstance(element, JrAstExpressionAtom)):
            operand = self.element.getOperand()
            return operand
        return None


    def resolve(self, env, flagResolveIdentifiers, entryp, leadp):
        # resolve the expression (recursively using ast)
        return self.element.resolve(env, flagResolveIdentifiers, entryp, leadp)


    def renderRun(self, rmode, env, entryp, leadp):
        #jrprint("RenderRun ({}) EXPRESSION".format(rmode))
        retv = self.resolve(env, True, entryp, leadp)
        return retv







class JrAstExpressionBinary(JrAst):
    def __init__(self, rule, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        self.rule = rule
        self.leftOperand = convertExpressionOperand(pnode.children[0], self)
        self.rightOperand = convertExpressionOperand(pnode.children[1], self)

    def resolve(self, env, flagResolveIdentifiers, entryp, leadp):
        # resolve the expression (recursively using ast)
        # run the operation on the resolved operand
        # resolve operand
        leftOperandResolved = self.leftOperand.resolve(env, flagResolveIdentifiers, entryp, leadp)
        rightOperandResolved = self.rightOperand.resolve(env, flagResolveIdentifiers, entryp, leadp)
        rule = self.rule
        #
        if (rule == JrCbLarkRule_Operation_Binary_add):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, (lambda a,b: a+b), (lambda a,b: a+b), None)
        elif (rule == JrCbLarkRule_Operation_Binary_sub):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, (lambda a,b: a-b), None, None)
        elif (rule == JrCbLarkRule_Operation_Binary_or):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, None, None, (lambda a,b: (a or b)))
        elif (rule == JrCbLarkRule_Operation_Binary_and):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, None, None, (lambda a,b: (a and b)))
        elif (rule == JrCbLarkRule_Operation_Binary_mul):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, (lambda a,b: a*b), (lambda a,b: a*b), None)
        elif (rule == JrCbLarkRule_Operation_Binary_div):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, (lambda a,b: a/b), None, None)
        elif (rule == JrCbLarkRule_Operation_Binary_lessthan):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, None, None, (lambda a,b: (a < b)))
        elif (rule == JrCbLarkRule_Operation_Binary_lessthanequal):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, None, None, (lambda a,b: (a <= b)))
        elif (rule == JrCbLarkRule_Operation_Binary_greaterthan):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, None, None, (lambda a,b: (a > b)))
        elif (rule == JrCbLarkRule_Operation_Binary_greaterthanequal):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, None, None, (lambda a,b: (a >= b)))
        elif (rule == JrCbLarkRule_Operation_Binary_equal):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, (lambda a,b: (a == b)), (lambda a,b: (a == b)), (lambda a,b: (a == b)))
        elif (rule == JrCbLarkRule_Operation_Binary_notequal):
            [success, operationResult] = self.operateBinary(rule, leftOperandResolved, rightOperandResolved, (lambda a,b: (a != b)), (lambda a,b: (a != b)), (lambda a,b: (a != b)))
        elif (rule == JrCbLarkRule_Operation_Binary_in):
            [success, operationResult] = self.operateBinaryInCollection(rule, leftOperandResolved, rightOperandResolved)
        else:
            raise makeJriException("Internal error: unknown binary expression operator ().".format(rule), self)
        if (not success):
            raise self.makeExpExceptionUnsupportedOperands(self, rule, leftOperandResolved, rightOperandResolved)
        return operationResult


    # helper function for running numeric/string/bool lambda binary operations based on the value types with generic errors for mismatched operands, etc.
    def operateBinary(self, opLabel, leftOperand, rightOperand, numericOp, stringOp, boolOp):
        leftType = leftOperand.getType()
        rightType = rightOperand.getType()
        leftOperandValue = leftOperand.getWrapped()
        rightOperandValue = rightOperand.getWrapped()
        #
        success = False
        operationResult = None
        #
        if (leftType != rightType):
            raise self.makeExpExceptionOperandMismatch(self, opLabel, leftOperand, rightOperand)
        #
        if (leftType == AstValNumber) and (numericOp is not None):
            resultVal = numericOp(leftOperandValue, rightOperandValue)
            operationResult = AstValNumber(self, self, resultVal)
            success = True
        if (leftType == AstValString) and (stringOp is not None):
            resultVal = stringOp(leftOperandValue, rightOperandValue)
            operationResult = AstValString(self, self, resultVal)
            success = True
        if (leftType == AstValBool) and (boolOp is not None):
            resultVal = boolOp(leftOperandValue, rightOperandValue)
            operationResult = AstValBool(self, self, resultVal)
            success = True
        return [success, operationResult]



    def operateBinaryInCollection(self, operationLabel, leftOperand, rightOperand):
        leftType = leftOperand.getType()
        rightType = rightOperand.getType()
        #
        success = False
        operationResult = None
        #
        try:
            # we will try to do native python IN test; if we throw PYTHON exception we will convert it to our own
            if (rightType == AstValList):
                resultVal = leftOperand in rightOperand
                success = True
            elif (rightType == AstValDict):
                resultVal = leftOperand in rightOperand
                success = True
            if (success):
                operationResult = AstValBool(self, self, resultVal)
        except Exception as e:
            # failed
            success = False
            detailStr = self.makeOperandDebugString(operationLabel, leftOperand, rightOperand)
            raise makeJriException("Runtime error: incompatible operation expression types for: {}.".format(detailStr), self)
        #
        return [success, operationResult]


    def makeOperandDebugString(self, operationLabel, leftOperand, rightOperand):
        leftTypeStr = calcNiceShortTypeStr(leftOperand)
        rightTypeStr = calcNiceShortTypeStr(rightOperand)
        msg = "'{}:{}' *{}* '{}:{}'".format(leftTypeStr, leftOperand.getWrappedForDisplay(), operationLabel, rightTypeStr, rightOperand.getWrappedForDisplay())
        return msg





    def makeExpExceptionOperandMismatch(self, sloc, operationLabel, leftOperand, rightOperand):
        detailStr = self.makeOperandDebugString(operationLabel, leftOperand, rightOperand)
        return makeJriException("Runtime error: mismatch of operation operands: {}.".format(detailStr), sloc)

    def makeExpExceptionUnsupportedOperands(self, sloc, operationRuleLabel, leftOperand, rightOperand):
        detailStr = self.makeOperandDebugString(operationRuleLabel, leftOperand, rightOperand)
        return makeJriException("Runtime error: Unsupported operation operands for: {}.".format(detailStr), sloc)
















class JrAstExpressionUnary(JrAst):
    def __init__(self, rule, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        self.rule = rule
        self.operand = convertExpressionOperand(pnode.children[0], self)

    def resolve(self, env, flagResolveIdentifiers, entryp, leadp):
        # resolve the expression (recursively using ast)
        # run the operation on the resolved operand
        # resolve operand
        operandResolved = self.operand.resolve(env, flagResolveIdentifiers, entryp, leadp)
        # run operation
        if (self.rule == JrCbLarkRule_Operation_Unary_neg):
            operationResult = self.operateNeg(operandResolved)
        elif (self.rule == JrCbLarkRule_Operation_Unary_not):
            operationResult = self.operateNot(operandResolved)
        else:
            raise makeJriException("Internal error: unknown unary expression operator ().".format(self.rule), self)
        # return result
        return operationResult
    
    def operateNeg(self, operand):
        operandAsNumber = operand.getWrappedExpect(AstValNumber)
        resultVal = -1 * operandAsNumber
        # recast to numeric val
        operationResult = AstValNumber(self, self, resultVal)
        return operationResult

    def operateNot(self, operand):
        operandAsBool = operand.getWrappedExpect(AstValBool)
        resultVal = (not operandAsBool)
        # recast to bool val
        operationResult = AstValBool(self, self, resultVal)
        return operationResult





class JrAstExpressionAtom(JrAst):
    def __init__(self, rule, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        self.rule = rule
        operandNode = pnode.children[0]
        if (rule == JrCbLarkRule_Atom_string):
            self.operand = AstValString(pnode, self, getParseTreeString(pnode))
        elif (rule == JrCbLarkRule_Atom_number):
            self.operand = AstValNumber(pnode, self, getParseNodeTokenValue(operandNode))
        elif (rule == JrCbLarkRule_Atom_boolean):
            self.operand = AstValBool(pnode, self, getParseNodeBool(operandNode))
        elif (rule == JrCbLarkRule_Atom_identifier):
            self.operand = AstValIdentifier(pnode, self, getParseNodeTokenValue(operandNode))
        elif (rule == JrCbLarkRule_Atom_null):
            self.operand = AstValNull(pnode, self)
        else:
            raise makeJriException("Internal error; unexpected token in atom expression ({}).".format(rule), pnode)

    def resolve(self, env, flagResolveIdentifiers, entryp, leadp):
        # resolve the expression (recursively using ast)
        # for an atom value, we just ask the value to resolve
        operandResolved = self.operand.resolve(env, flagResolveIdentifiers, entryp, leadp)
        return operandResolved

    def getOperand(self):
        return self.operand





class JrAstExpressionCollectionList(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        collectionNode = pnode.children[0]
        if (collectionNode is None):
            itemList = []
        else:
            itemList = convertPositionalArgList(collectionNode, self)
        #
        self.itemList = itemList


    def resolve(self, env, flagResolveIdentifiers, entryp, leadp):
        # resolve the expression (recursively using ast)

        # for a list, we need to ask each item in list to resolve
        resolvedItemList = []
        for item in self.itemList:
            resolvedItemList.append(item.resolve(env, flagResolveIdentifiers, entryp, leadp))
        return AstValList(self, self, resolvedItemList)





class JrAstExpressionCollectionDict(JrAst):
    def __init__(self, pnode, parentp):
        super().__init__(pnode, parentp)
        #
        collectionNode = pnode.children[0]
        if (collectionNode is None):
            itemDict = {}
        else:
            itemDict = convertDictionary(collectionNode, self)
        #
        self.itemDict = itemDict



    def resolve(self, env, flagResolveIdentifiers, entryp, leadp):
        # resolve the expression (recursively using ast)

        flagReadOnly = False
        flagCreateKeyOnSet = True

        # for a dict, we need to ask each item in dict to resolve
        resolvedItemDict = {}
        for key, item in self.itemDict.items():
            resolvedItemDict[key] = item.resolve(env, flagResolveIdentifiers, entryp, leadp)
        aDict = AstValDict(self, self, resolvedItemDict, flagReadOnly, flagCreateKeyOnSet)
        return aDict

















































# entry child helper manages the children of an entry
class JrAstEntryChildHelper(JrAst):
    def __init__(self, sloc, parentp):
        super().__init__(sloc, parentp)
        # ordered list of children
        self.childList = []
        # hash of children by Id
        self.childIdHash = {}

    def printDebug(self, env, depth):
        # nice hierarchical tabbed pretty print
        str = None
        childCount = len(self.childList)
        if (childCount==0):
            #str = "Zero children"
            pass
        elif (childCount==1):
            str = "1 child:"
        else:
            str = "{} children:".format(childCount)
        #
        if (str is not None):
            super().printDebug(env, depth, str)
            #astPrintDebugLine(depth, "{}: {} @ {}".format(self.getTypeStr(), str, self.getOwnerParentp().sloc.debugString()))

        # now children
        for child in self.childList:
            child.printDebug(env, depth+1)


    def getOwnerParentp(self):
        return self.parentp


    def findExistingEntryChild(self, entryAst):
        # return info on an existing child or NONE if none matches
        if (self.childIdHash is None):
            return None
        entryId = entryAst.getEntryIdFallback(DefCbDefine_IDEmpty)
        if (entryId in self.childIdHash):
            return self.childIdHash[entryId]
        return None


    def addChild(self, env, childAst, pnode):
        # create children if there are none yet
        if (self.childList is None):
            self.childList = []
            self.childIdHash = {}

        # add to hash
        # ATTN: im not sure we even use the hash for fast lookups currently
        entryId = childAst.getEntryIdFallback(DefCbDefine_IDEmpty)
        if (True):
            # add it
            childIndex = len(self.childList)
            self.childList.append(childAst)   
            # add hash; note that it will overwrite if it already exists, which we dont really care about, error would have flagged earlier at time of creationg
            self.childIdHash[entryId] = childAst



    def convertEntryAddMergeChildAst(self, env, pnode, expectedLevel):
        # start by creating a NEW JrAstEntry node (we may dispose it if we choose to merge but it's more straighforward to do this)
        # NOTE: we pass env here so that we can catch exceptions at this level and continue if we want for better error reporting

        try:
            return self.convertEntryAddMergeChildAstDoWork(env, pnode, expectedLevel)
        except Exception as e:
            e = makeModifyJriExceptionAddLocIfNeeded(e, self, None)
            interp = env.getInterp()
            if (interp.getFlagContinueOnException()):
                interp.displayException(e, True)
            else:
                raise e




    def convertEntryAddMergeChildAstDoWork(self, env, pnode, expectedLevel):
        newEntryAst = JrAstEntry(pnode, self.getOwnerParentp(), expectedLevel)
        # convert core but not children
        newEntryAst.convertCoreFromPnode(pnode)

        # now see if this exists already as a child and should be merged
        if (newEntryAst.shouldEntryIdBeUnique()):
            # this id should be unique so see if there is another with this same id
            existingChild = self.findExistingEntryChild(newEntryAst)
        else:
            #  we dont care about it being unique, so create a new one
            existingChild = None

        if (existingChild is None):
            # no existing child, so we will add this child, and add its children recursively to it
            self.addChild(env, newEntryAst, pnode)
            recurseEntryAst = newEntryAst
        else:
            # we have an existing child with this id, so we check for conflicts and then merge children into it if there are none
            recurseEntryAst = existingChild
            # check for conflict
            if (jrfuncs.isNonEmptyString(newEntryAst.getLabel())):
                # want to use new label
                if (jrfuncs.isNonEmptyString(existingChild.getLabel()) and (existingChild.getLabel() != newEntryAst.getLabel())):
                    raise makeJriException("Grammar error: Redefinition of label in repeat use of entry header for entry with id '{}' (only one should be non-empty); old={} vs new={}.".format(newEntryAst.getDisplayIdLabel(), existingChild.getLabel(), newEntryAst.getLabel()), pnode)
                existingChild.label = newEntryAst.label
            if (newEntryAst.options is not None):
                # want to use new options
                if (existingChild.options is not None) and (existingChild.options != newEntryAst.options):
                    raise makeJriException("Grammar error: Redefinition of options in repeat use of entry header for entry with id '{}' (only one should be non-empty); old={} vs new={}.".format(newEntryAst.getDisplayIdLabel(), existingChild.options, newEntryAst.options), pnode)
                existingChild.options = newEntryAst.options
            # ATTN: NEW we do not allow anything but top level entry merging as it is too likely to be a mistake if two leads have same id
            if (expectedLevel!=1) or (existingChild.getLevel()!=1):
                raise makeJriException("Grammar error: Two (non-top-level) entries have the same id '{}').".format(newEntryAst.getDisplayIdLabel()), pnode)

            # is body trickier? do we want to merge?
            if (len(newEntryAst.bodyBlockSeqs) > 0):
                # new bodies to add
                # we could complain about both having bodies, but instead we just append bodies -- but WHY?
                if (len(existingChild.bodyBlockSeqs)>0):
                    if (False):
                        raise makeJriException("Grammar error: Redefinition of body in repeat use of entry header for entry with id '{}' (only one should be non-empty); old={} vs new={}.".format(newEntryAst.getDisplayIdLabel(), existingChild.body, newEntryAst.body), pnode)
                # APPEND body from new to existing
                # ATTN: What is the use case for this? THE USE CASE IS SECTIONS LIKE SETUP|OPTIONS
                existingChild.mergeNewBodyBlockSeqsFrom(newEntryAst)


        # now recurse and add OUR children (those after head and body), to the newly added child ast OR the merged existing one
        pchildCount = len(pnode.children)
        if (pchildCount>2):
            for i in range(2, pchildCount):
                pchild = pnode.children[i]
                recurseEntryAst.entries.convertEntryAddMergeChildAst(env, pchild, expectedLevel+1)


    def findEntryById(self, id):
        for child in self.childList:
            if (child.getId()==id):
                return child
        # not found
        return None


    def findDescendantByIdOrLabel(self, id, astloc):
        foundResults = []
        # walk children looking for match
        for child in self.childList:
            childEntryId = child.getId()
            if (childEntryId == id):
                foundResults.append(child)
        if (len(foundResults)==0):
            # didn't find any.. allow recursion into children
            for child in self.childList:
                childEntryId = child.getId()
                foundResult = child.entries.findDescendantByIdOrLabel(id, astloc)
                if (foundResult is not None):
                    foundResults.append(foundResult)

        # if we found exactly one, then return it
        if (len(foundResults)==1):
            return foundResults[0]
        # if we found too many, complain
        if (len(foundResults)>1):
            raise makeJriException("Too many ({}) entries/sections match id ({}); use path string like SECTION>ID to be more specific".format(len(foundResults), id))
        # not found
        return None


    def getNextNonCopyChildEntry(self, entryp, env):
        grabNext = False
        for child in self.childList:
            if (child == entryp):
                grabNext = True
            elif (grabNext):
                # let's see if this one is good
                childCopyFrom = child.getCopyFrom()
                if (childCopyFrom is None):
                    # got one!
                    return child
                # it's not none, but if its not next, then try to use it
                if (childCopyFrom=="next"):
                    # next, so keep oing
                    continue
                # it's an explicit
                copyEntry = env.findEntryByIdPath(childCopyFrom, self)
                return copyEntry
        # didn't fine one
        return None


    def addFlatEntries(self, retList):
        # recursively add all RenderLEADS
        for child in self.childList:
            if (isinstance(child, JrAstEntry)):
                retList.append(child)
                if (child.entries is not None):
                    child.entries.addFlatEntries(retList)








class JrAstResultList:
    def __init__(self):
        self.contents = []

    def append(self, item):
        self.contents.append(item)

    def flatAdd(self, item, flagChangeBlankLinesToLatexNewlines=False):
        # if item being added is a list or another JrAstResultList then flatten it before adding
        if (isinstance(item, list)):
            for i in item:
                self.flatAdd(i, flagChangeBlankLinesToLatexNewlines)
        elif (isinstance(item, JrAstResultList)):
            for i in item.getContents():
                self.flatAdd(i, flagChangeBlankLinesToLatexNewlines)
        else:
            if (flagChangeBlankLinesToLatexNewlines) and (item=="\n"):
                item = vouchForLatexString(r"~\\"+"\n", True)
            self.append(item)

    def flatAddBlankLine(self):
        self.flatAdd("~\n")

    def getContents(self):
        return self.contents
    def __len__(self):
        return len(self.contents)

    def removeByIndex(self, index):
        del self.contents[index]

    def flatInsertAtIndex(self, item, index):
        # if item being added is a list or another JrAstResultList then flatten it before adding
        if (isinstance(item, list)):
            for i in item:
                self.flatInsert(i, index)
                index += 1
        elif (isinstance(item, JrAstResultList)):
            for i in item.getContents():
                self.flatInsertAtIndex(i, index)
                index += 1
        else:
            self.contents.insert(index, item)

    def printDebug(self, env):
        for index,block in enumerate(self.contents):
            if (block=="\n"):
                block = "[NEWLINE]"
            elif (isinstance(block, AstValString)):
                block = 'AstValString: "{}"'.format(block.getWrapped())
            jrprint("         {}: {}".format(index+1, block))



# result atom is going to be something we can add to result list
class ResultAtom:
    def __init__(self, value):
        self.value = str(value)
    def __str__(self):
        return self.value
    def isSafeLatex(self):
        return False
    def isMarkdown(self):
        return False


# ATTN: i want to move from vouched latex string to this;
# so eventually vouched latex string will actually be ResultAtomLatex instanced
class ResultAtomLatex(ResultAtom):
    def __init__(self, value, flagIsEmbeddable):
        super().__init__(value)
        self.isEmbeddable = flagIsEmbeddable
    def isSafeLatex(self):
        return True
    def getIsLatexEmbeddable(self):
        return self.isEmbeddable



class ResultAtomMarkdownString(ResultAtom):
    def __init__(self, value):
        super().__init__(value)
    def isMarkdown(self):
        return True


class ResultAtomPlainString(ResultAtom):
    def __init__(self, value):
        super().__init__(value)


class ResultAtomNote(ResultAtom):
    def __init__(self, note):
        super().__init__("")
        self.note = note
    def getNote(self):
        return self.note
    def isSafeLatex(self):
        # it's safe latex because it's BLANK
        return True








def convertTypeStringToAstType(typeStr):
    rmap = {
        "string": AstValString,
        "number": AstValNumber,
        "bool": AstValBool,
        "list": AstValList,
        "dict": AstValDict,
        "identifier": AstValIdentifier,
    }
    if (typeStr in rmap):
        return rmap[typeStr]
    # any kind
    return None


