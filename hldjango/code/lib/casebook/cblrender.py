from .cbrender import CbRenderDoc, CbRenderSection, CbRenderLead, outChunkManager

# ast
from .jrastvals import AstValString
from .jrastfuncs import getUnsafeDictValueAsString, getUnsafeDictValueAsNumber, convertEscapeUnsafePlainTextToLatex, makeLatexLabelFromRid, DefLatexVouchedPrefix, isTextLatexVouched, isTextLatexVouchedEmbeddable, removeLatexVouch, convertEscapeVouchedOrUnsafePlainTextToLatex, makeLatexLinkToRid, DefContdStr, DefInlineLeadPlaceHolder, vouchForLatexString
#
from .cbdeferblock import CbDeferredBlock, CbDef_SkipNextNewline, CbDeferredBlockPotentialEndLeadTime
#
from .cbfuncs_core_support import wrapTextInLatexBox
from .casebookDefines import *

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
from .jriexception import *

# markdown
from lib.jrmistle.hlmarkdown import HlMarkdown

# pylatex
import pylatex
import re

#
from lib.jr import jrpdf



# enable this to add section breaks in other places other than lead start and end
DefExtraBreakWarnSecEnd = False
DefBreakWarnSecMethod = "varset"















# derived render doc for latex stuff

class CblRenderDoc(CbRenderDoc):
    def __init__(self, jrinterp):
        super().__init__(jrinterp)
        #
        self.options = None
        self.chunks = outChunkManager()
        self.setCurrentColumnCount(1)
        self.setLastEntryHadPageBreakAfter(True)
        #
        # markdown helper
        self.hlMarkdown = HlMarkdown(self)
        markdownOptions = {
            "forceLinebreaks": True,
            #"autoStyleQuotes": False
        }
        self.hlMarkdown.setOptions(markdownOptions)
        #
        # pdf helper
        self.jrp = jrpdf.JrPdf()
        #
        #self.tocTopLabels = []

    def taskSetOptions(self, options):
        # start with user configured options
        env = self.getEnvironment()
        renderOptions = env.getEnvValueUnwrapped(None, "rendererData", None)
        self.options = jrfuncs.deepCopyListDict(renderOptions)
        # now overwrite with any passed in
        jrfuncs.deepMergeOverwriteA(self.options, options)
        #
        # FORCE option to make sure user cannot change it
        self.options["latexExeFullPath"] = DefCbDefine_latexExeFullPath


    def setCurrentColumnCount(self, val):
        self.currentColumnCount = val
    def getCurrentColumnCount(self):
        return self.currentColumnCount
    
    def getLastEntryHadPageBreakAfter(self):
        return self.lastEntryHadPageBreakAfter
    def setLastEntryHadPageBreakAfter(self, val):
        self.lastEntryHadPageBreakAfter = val

    def getOption(self, keyName, defaultVal):
        return jrfuncs.getDictValueOrDefault(self.options, keyName, defaultVal)


    def printDebug(self, env):
        # internals
        jrprint("Debug rendering from CbRenderDoc ({} sections):".format(len(self.children)))
        for section in self.children.getList():
            section.printDebug(env)


    def renderToPdf(self, suffixedOutputPath, suffixedBaseFileName, flagDebug, renderSectionName):
        # latex
        env = self.getEnvironment()
        #jrprint("Generating Latex...")
        documentText = self.renderDocText(env, renderSectionName)
        # run it
        [retv, fileList] = self.saveLatexGeneratePdf(documentText, suffixedOutputPath, suffixedBaseFileName, flagDebug)
        return [retv, fileList]




    def saveLatexGeneratePdf(self, documentText, suffixedOutputPath, suffixedBaseFileName, flagDebug):
        fileList = []
        filePathMain = suffixedOutputPath + "/" + suffixedBaseFileName
        filePath = filePathMain + ".latex"
        expectedPdfFilePath = filePathMain + ".pdf"
        expectedLogFilePath = filePathMain + ".log"
        #
        if (flagDebug):
            jrprint("Saving generated latex to file \"{}\".".format(filePath))
        #
        jrfuncs.saveTxtToFile(filePath, documentText, "utf-8")
        #
        #
        retv = self.generatePdf(filePath, flagDebug)
        #
        # build list of created files
        retv = jrfuncs.pathExists(expectedPdfFilePath)
        if (jrfuncs.pathExists(filePath)):
            fileList.append(filePath)
        if (jrfuncs.pathExists(expectedPdfFilePath)):
            fileList.append(expectedPdfFilePath)
        if (jrfuncs.pathExists(expectedLogFilePath)):
            fileList.append(expectedLogFilePath)
        #
        return [retv, fileList]




    def generatePdf(self, filePath, flagDebug):
        # pass through render options
        if (flagDebug):
            jrprint("Generating pdf from latex..")
        #
        self.jrp.setRenderOptions(self.options)
        cleanExtras = self.getOption("cleanExtras", False)
        #
        retv = self.jrp.generatePdflatex(filePath, flagDebug, cleanExtras)


        return retv

 






    def convertMarkdownOrVouchedTextToLatex(self, text):
        if (isTextLatexVouched(text)):
            # do NOT markdown strings that are vouched latex
            latexText = removeLatexVouch(text)
            return latexText
        return self.convertMarkdownToLatexDontVouch(text)

    def convertMarkdownToLatexDontVouch(self, text):
        # convert to latex using mistletoe library
        [latexText, extras] = self.hlMarkdown.renderMarkdown(text, "latex", True)
        return latexText



    # rendering code taken from hlparser start by searching for "def renderLeads(...)"

    def renderMarkdownToLatex(self, markdownStr):
        # convert markdown to latex
        return str
    
    def buildPdfFromLatex(self, latexStr, outFilePath):
        # build a pdf from a latex str
        return False












    def afterTaskRenderRunProcess(self, task, rmode, env):
        # CODE RUN AFTER a TASK RENDERRUN

        # merge inline pending leads
        self.mergeQueuedInlineLeadToRenderSectionWithId(env, self.getMainLeadsSectionName())

        # now impose and OVERWRITE any task-set options onto sections
        self.imposeTaskOptionsOnSections()

        # any generic post rendering steps?
        # walk leads, do any final steps (for example this adds deferred time blocks to leads)
        leadList = self.calcFlatLeadList()
        for lead in leadList:
            self.postProcessLeadRenderRun(lead, task, rmode, env)

        # debug author report generation?
        reportMode = task.getReportMode()
        if (reportMode):
            self.generateReportSections(env, self.getReportSectionName())
        else:
            self.hideReportSections(env, self.getReportSectionName())

        # sort entries
        self.sort()


    def imposeTaskOptionsOnSections(self):
        # there are options that the user can configure in their casebook file, which we can OVERWRITE in task options
        leadBreak = self.getOption("leadBreak", None)
        leadColumns = self.getOption("leadColumns", None)
        leadSection = self.getMainLeadsSection()
        if (leadBreak is not None):
            leadSection.setLeadBreak(leadBreak)
        if (leadColumns is not None):
            leadSection.setLeadColumns(leadColumns)


    def postProcessLeadRenderRun(self, lead, task, run, env):
        # executed after building all leads
        endTimeBlock = CbDeferredBlockPotentialEndLeadTime(None, None, self)
        lead.addBlocks(endTimeBlock)


























    def renderDocText(self, env, renderSectionName):
        # render entire document
        # NOTE: This function is called AFTER the structure of the render is built (CbRenderLead and CbRenderSection, etc.)
        # so it's job is NOT to generate the basic contents of leads, but rather to ASSEMBLE them and create final latex
        # for code that generates the main structure, see taskRenderRun()

        self.chunks.clear()

        # start stuff
        self.generateDocumentStart(env)

        if (renderSectionName is not None):
            renderSection = self.findRenderSectionById(renderSectionName)
            if (renderSection is None):
                raise makeJriException("In renderDocText, could not find render section '{}'.".format(renderSectionName), self)
            self.renderItem(env, renderSection, None)
        else:
            # walk all sections and generate latex text
            self.renderChildren(env, self.children, None)

        # turn off any multicol by reverting to single column default
        self.addChunkToSetCurrentColumnCountTo(1)

        # end stuff
        self.generateDocumentEnd(env)

        # return it
        documentText = self.assembleText()
        return documentText


    def assembleText(self):
        text = ""
        for chunk in self.chunks.getList():
            text += chunk
        return text




    def renderChildren(self, env, children, parentSection):
        for child in children.getList():
            self.renderItem(env, child, parentSection)
















    def renderItem(self, env, item, parentSection):
        optionSkipDebugText = True
        #

        # items can be marked as not to be rendered
        visible = item.getVisibility()
        if (not visible):
            return

        # generate header text toc, etc.
        # NEW: we have the option to defer this until later
        if (item.getAutoHeaderRender()):
            allLatexText = self.calcHeaderLatexForLead(item)
        else:
            allLatexText = ""

        isLead = isinstance(item, CbRenderLead)
        if (isLead):
            useTombstones = item.calcLeadTombstones()
        else:
            useTombstones = False

        # new "continued on next page" stuff
        flagCloseBreakwarnsec = False
        # test
        if (isLead):
            # whenever we use tombstones, add latex to show a Continued on next page footer if its is continues onto the next page
            if (useTombstones):
                allLatexText += self.breakWarnSecStart()
                flagCloseBreakwarnsec = True


        # TIME LATEX to be added later
        # we only show time IF: this case is configured to use a clock AND we are in the proper LEADS section AND this is a "lead" (as opposed to a section) AND time!=0
        # if time = none then we use DEFAULT time, otherwise we use a multiple of clock ticks
        timeLatex = self.calculateItemTimeLatex(env, item, parentSection)
        itemTimePos = item.getTimePos()

        if (timeLatex is not None) and (itemTimePos=="start"):
            # TIME at start
            allLatexText += timeLatex

        # item text contents
        resultList = item.blockList.getList()
        if (resultList is None):
            contents = []
        else:
            contents = resultList.getContents()

        # we accumulate contiguous markdown/plain text before we try to convert to markdown, since we need to know about linebreaks between them.
        latexBlocks = []
        markdownText = ""
        for index, block in enumerate(contents):
            if (isinstance(block, CbDeferredBlock)):
                # deferred render chunk gets handled first
                if (index==len(contents)-1):
                    nextBlock = None
                else:
                    # let's try to peek at subsequent block to pass to deferred item
                    nextBlock = contents[index+1]
                [block, newPriorMarkdownText, newNextBlock] = block.renderToLatexString(env, self, item, parentSection, markdownText, nextBlock)
                # change prior and subsequent if specified
                if (newPriorMarkdownText is not None):
                    markdownText = newPriorMarkdownText
                if (nextBlock is not None) and (newNextBlock is not None) and (newNextBlock != nextBlock):
                    # replace next block
                    contents[index+1] = newNextBlock
                # now 'block' is assigned the RESULT of deferred output, where it is handled below
                # drop down
            #
            if (isinstance(block, str)):
                text = block
            elif (isinstance(block, AstValString)):
                text = block.getUnWrappedExpect(AstValString)
            elif (block is None):
                jrprint("RENDER WARNING: Null block in render.")
                raise Exception ("Internal Runtime error: Null block in render.")
                continue
            else:
                # UNKNOWN WARNING/ERROR
                jrprint("RENDER WARNING: UNKNOWN RESULT BLOCK IN RENDER CONTENTS: {}".format(type(block)))
                continue

            # skip if it starts with "DEBUG:"
            if (optionSkipDebugText) and (text.startswith("DEBUG:")):
                continue
            # convert to markdown IFF appropriate
            if (isTextLatexVouched(text)):
                # there are TWO options here for combining some latex with mardown -- we can EITHER embed the latex as if it were a word that could be wrapped in markdown tags
                # OR we can FORCE markdown to complete before appending the latex
                isLatexEmbeddable = isTextLatexVouchedEmbeddable(text)
                if (isLatexEmbeddable):
                    # we EMBED this latex into the markdown where we will unpack it later; in this way it can be put inside markdown annotations; this can be use for word and phrase-like latex short snipped
                    markdownText += self.embedTempLatexBlockRef(len(latexBlocks))
                    latexBlockText = self.convertMarkdownOrVouchedTextToLatex(text)
                    latexBlocks.append(latexBlockText)
                else:
                    # we force markdown to complete then add latex; this should be used for sections of latex that need to be self containted and cannot be INSIDE the middle of a markdown thing
                    if (markdownText!=""):
                        markdownTextAsLatex = self.convertMarkdownOrVouchedTextToLatex(markdownText)
                        # ok now we need to REPLACE the blocks
                        markdownTextAsLatex = self.unembedTempLatexBlockRefs(markdownTextAsLatex, latexBlocks)
                        allLatexText += markdownTextAsLatex
                        markdownText = ""
                    # add latex
                    allLatexText += self.convertMarkdownOrVouchedTextToLatex(text)
            else:
                # accumulate markdown text into one big block
                markdownText += text

        # pending markdown
        if (markdownText!=""):
            markdownTextAsLatex = self.convertMarkdownOrVouchedTextToLatex(markdownText)

            # ok now we need to REPLACE the blocks
            markdownTextAsLatex = self.unembedTempLatexBlockRefs(markdownTextAsLatex, latexBlocks)

            allLatexText += markdownTextAsLatex
            markdownText = ""


        # now we have the entire text
        # strip it
        allLatexText = allLatexText.strip()


        # contents break beforehand (note this runs even if our "contents" are blank)
        self.addChunkForBreakBefore(item, parentSection)

        if (allLatexText!=""):
            # contents columns
            self.addChunkToSetCurrentColumnCount(item, parentSection)

            # contents text
            self.chunks.append(allLatexText)
            # add linebreak since we stripped text of end linebreaks
            self.chunks.append("\n")


        # add tombstone if its a lead (as opposed to a section)
        if (isLead):
            # if we have an explicit tombstones value use it
            if (useTombstones):
                # ATTN: new add a nopagebreak for tombstone so it doesnt end up alone
                text = "\\nopagebreak" + self.hlMarkdown.latexTombstone()
                self.chunks.append(text)

        # close any "continued on next page stuff that we started"
        if (flagCloseBreakwarnsec): 
            self.chunks.append(self.breakWarnSecEnd())
            flagCloseBreakwarnsec = False

        # contents break after (note this runs even if our "contents" are blank)
        self.addChunkForBreakAfter(item, parentSection)

        # now recursively walk all children
        if (hasattr(item, "children")):
            self.renderChildren(env, item.children, item)







    def calcHeaderLatexForLead(self, item):
        # build the header subheading etc text for lead
        optionMaxLevel = 3
        level = item.getLevel()

        # item TITLE/LABEL
        titleOrig = item.calcDisplayTitle()
        # set toc, possibly based on title
        toc = item.getToc()
        if (toc is None):
            toc = titleOrig
        # title
        title = titleOrig
        # heading, which will replace title
        heading = item.getHeading()
        if (heading is not None):
            title = heading
        #
        allLatexText = ""

        titleLatex = convertEscapeVouchedOrUnsafePlainTextToLatex(title)
        tocLatex = convertEscapeVouchedOrUnsafePlainTextToLatex(toc)

        # modifying section font details
        komaHeaderModifier = None
        headingStyle = item.getHeadingStyle()
        if (headingStyle is not None):
            #jrprint("DEBUG BREAK")
            if (headingStyle=="huge"):
                komaHeaderModifier = r"{\fontsize{96}{128}\selectfont}"
            else:
                raise makeJriException("Unknown headingStyle: {}.".format(headingStyle), None)
                #komaHeaderModifier = r"\addtokomafont{section}{\fontsize{64}{80}\selectfont}"

        # some items may want to disable their heading and toc entry
        blankHead = item.getBlankHead()

        # TOC and title lines
        if (not blankHead):
            # the TOC entry
            ltext = ""
            if (level==1):
                if (title is not None) and (title!=""):
                    ltext += "\n" + self.wrapInKomaSectionModifierIfNeeded("chapter", komaHeaderModifier, "\\chapter*{{{}}}%\n\n".format(titleLatex))
                if (toc is not None) and (toc!=""):
                    ltext += r"\addcontentsline{toc}{chapter}{~~" + tocLatex + "}\n"
            elif (level==2):
                if (title is not None) and (title!=""):
                    ltext += "\n" + self.wrapInKomaSectionModifierIfNeeded("section", komaHeaderModifier, "\\section*{{{}}}%\n\n".format(titleLatex))
                if (toc is not None) and (toc!=""):
                    ltext += r"\addcontentsline{toc}{section}{~~" + tocLatex + "}\n"
            elif (level==3) and (optionMaxLevel>=3):
                if (title is not None) and (title!=""):
                    ltext += "\n" + self.wrapInKomaSectionModifierIfNeeded("subsection", komaHeaderModifier, "\\subsection*{{{}}}%\n\n".format(titleLatex))
                if (toc is not None) and (toc!=""):
                    ltext += r"\addcontentsline{toc}{subsection}{~~" + tocLatex + "}\n"
            else:
                # higher level toc headings just get shown bold
                if (title is not None) and (title!=""):
                    ltext += "\\textbf{{{}}}%\n\n".format(titleLatex)

            # the label that is target of hyperlink above in toc
            if (level <= optionMaxLevel):
                # add label that can be target of hyperref (needs to be unique?)
                if (toc is not None) and (toc!=""):
                    if (level>1):
                        if (True):
                            ltext += makeLatexLabelFromRid(item.getRid())

            # build latex
            allLatexText += ltext


        # subheading
        subheading = item.getSubHeading()
        if (subheading is not None) and (subheading!=""):
            subheadingLatex = convertEscapeUnsafePlainTextToLatex(subheading)
        else:
            subheadingLatex = ""

        # add inlinedFromLead info to subheading
        inlinedFromLead = item.getInlinedFromLead()
        if (inlinedFromLead is not None):
            inlinedFromAddLatex = self.calcInlinedFromLatex(subheading, inlinedFromLead)
            if (subheadingLatex==""):
                subheadingLatex = "From {}".format(inlinedFromAddLatex)
            else:
                repStr = "(" + inlinedFromAddLatex + ")"
                # replace only the first
                subheadingLatex = subheadingLatex.replace(DefInlineLeadPlaceHolder, repStr, 1)

        # add continued from, which is like inlinedFrom but set on non-inline
        continuedFromStr = item.getContinuedFromLead()
        if (continuedFromStr is not None):
            continuedFromLead = self.findLeadByIdPath(continuedFromStr, item.getEntry())
            if (continuedFromLead is None):
                raise JriException("Could not find lead id specified in 'continued from' ({})".format(continuedFromStr, item))
            continedFromLatex = self.calcInlinedFromLatex(subheading, continuedFromLead)
            continedFromLatex = " from {}".format(continedFromLatex)
            if (subheadingLatex==""):
                subheadingLatex = str(DefContdStr).title() + continedFromLatex
            else:
                subheadingLatex = subheadingLatex + " (" + str(DefContdStr) + continedFromLatex + ")"

        if (True):
            # address as part of subheadingLatex
            address = item.calcLeadAddress()
            if (address is not None) and (address !="") and (address!="auto"):
                addressLatex = "\\newline\\small{{{}}}%\n".format(convertEscapeUnsafePlainTextToLatex(address))
                if (subheadingLatex!=""):
                    subheadingLatex += "\n" + addressLatex
                else:
                    subheadingLatex = addressLatex

        # display subheading
        if (not blankHead) and (subheadingLatex != ""):
            ltext = "\\cbsubheading{{{}}}%\n\n".format(subheadingLatex)
            allLatexText += ltext

        # address
        if (False):
            address = item.calcLeadAddress()
            if (address is not None) and (address !="") and (address!="auto"):
                ltext = "\\textsc{{{}}}%\n\n".format(convertEscapeUnsafePlainTextToLatex(address))
                allLatexText += ltext

        return allLatexText












    # Helper code to generate "Continued on next page" text in footer automatically
    def breakWarnSecStart(self):
        # there are two ways to do this, one to wrap in an environment, which has some consequences in that it may hide stuff we do inside from outer
        # the other ways is to simply set variable directly, which is less prone to complaints
        #return "\n" + "\\begin{breakwarnsec}\n"
        if (DefBreakWarnSecMethod=="varset"):
            return r"\warnpgbrktrue "
        else:
            return r"\refstepcounter{question}\label{question-start-\thequestion}"

    def breakWarnSecEnd(self):
        #return "\n" + "\\end{breakwarnsec}\n"
        if (DefBreakWarnSecMethod=="varset"):
            return r"\warnpgbrkfalse "
        else:
            return r"\label{question-end-\thequestion}"






    def wrapInKomaSectionModifierIfNeeded(self, sectionType, komaHeaderModifier, text):
        if (komaHeaderModifier is None) or (komaHeaderModifier==""):
            return text
        text = r"\begingroup" + r"\addtokomafont{" + sectionType + "}" + komaHeaderModifier + "\n" + text + "\n" + r"\endgroup" + "\n"
        return text



    # ATTN: move this to RenderBase eventually
    def calculateItemTime(self, env, item, parentSection):
        # an item is times IFF: this case is configured to use a clock AND we are in the proper LEADS section AND this is a "lead" (as opposed to a section) AND time!=0
        itemTime = item.getTime()
        if (itemTime==0):
            return False
        if (not isinstance(item, CbRenderLead)):
            return False
        if (item.getLevel()==1) or (parentSection is None):
            # top level is not elligble
            return False
        # section time tells us the DEFAULT time for all entries in it; this is the LEADS section, etc
        defaultSectionTime = parentSection.getTime()
        if (defaultSectionTime is None):
            return False
        if (itemTime is None) or (itemTime==-1):
            # no time specified, or -1, then we use default
            itemTime = defaultSectionTime
        # now return time
        return itemTime

    def calculateItemTimeLatex(self, env, item, parentSection):
        itemTime = self.calculateItemTime(env, item, parentSection)
        if (itemTime is not None) and (itemTime != False) and (itemTime>0):
            timeText = "Time advances {} minutes.".format(int(itemTime))
            timeLatex = "\n" + wrapTextInLatexBox("default", timeText, False, "clock", "red", None)
            return timeLatex
        # no time statement
        return None




    def embedTempLatexBlockRef(self, blockIndex):
        text = "XYZZYBLOCKREF{}XYZZY".format(blockIndex)
        return text

    def unembedTempLatexBlockRefs(self, text, latexBlocks):
        blockRefRegex = r"XYZZYBLOCKREF(\d+)XYZZY"
        text = re.sub(blockRefRegex, lambda m: self.unembedTempLatexBlockRef(m.group(1), latexBlocks), text)
        return text

    def unembedTempLatexBlockRef(self, numberStr, latexBlocks):
        try:
            index = int(numberStr)
            return latexBlocks[index]
        except Exception as e:
            raise makeJriException("INTERNAL RENDER ERROR: Could not replace latex markdown replacement palceholder block #{}".format(numberStr), None)


    def addChunkForBreakBefore(self, item, parentSection):
        breakStyle = self.calcBreakForSectionOrLead(item, parentSection, True)
        retv = self.addChunkForBreakBeforeUsingStyle(breakStyle, True)

    def addChunkForBreakAfter(self, item, parentSection):
        breakStyle = self.calcBreakForSectionOrLead(item, parentSection, False)
        retv = self.addChunkForBreakBeforeUsingStyle(breakStyle, False)
        self.setLastEntryHadPageBreakAfter(retv)

    def addChunkForBreakBeforeUsingStyle(self, breakStyleYesNo, positionBefore):
        # the tricky part here is when we have the previous item with a forced break AFTER and next item with a forced break BEFORE, we dont want to do it twice
        newPageLatex = "\\newpage\n"
        clearDoublePageLatex = "\\cleardoublepage\n"
        #
        if (breakStyleYesNo == "no"):
            return False
        elif (breakStyleYesNo == "yes"):
            if (not self.getLastEntryHadPageBreakAfter()) or (not positionBefore):
                # do we want to turn off any "continued on the next page" stuff when we have a manual break? this only works if we are not using the environment-based style (otherwise we would not have matching begin end)
                if (DefExtraBreakWarnSecEnd):
                    # i don't think it's very important
                    self.chunks.append(self.breakWarnSecEnd())
                #
                text = newPageLatex
                self.chunks.append(text)
            return True
        elif (breakStyleYesNo == "facing"):
            # do we want to turn off any "continued on the next page" stuff when we have a manual break? this only works if we are not using the environment-based style (otherwise we would not have matching begin end)
            if (DefExtraBreakWarnSecEnd):
                # i don't think it's very important
                self.chunks.append(self.breakWarnSecEnd())
            #
            # here we want at least one newpage but maybe two to get on padd page
            if (not self.getLastEntryHadPageBreakAfter()) or (not positionBefore):
                text = newPageLatex
                self.chunks.append(text)
            text = clearDoublePageLatex
            self.chunks.append(text)
            return True
        else:
            raise makeJriException("Internal Render Error: Uknnown breakstyle in addChunkForBreakBeforeUsingStyle: {}".format(breakStyleYesNo))

    def calcBreakForSectionOrLead(self, item, parentSection, positionBefore):
        # from "yes", "no", "facing"
        isLead = isinstance(item, CbRenderLead)
        #
        if (isLead):
            breakStyle = item.calcLeadBreak()
        else:
            breakStyle = item.calcSectionBreak()
        #
        if (positionBefore):
            if (breakStyle in ["before", "solo"]):
                return "yes"
            elif (breakStyle in ["beforeFacing", "soloFacing"]):
                return "facing"
            return "no"
        #
        if (breakStyle in ["after", "solo", "soloFacing"]):
            return "yes"
        elif (breakStyle in ["afterFacing", "soloAfterFacing"]):
            return "facing"
        return "no"




    def calcInlinedFromLatex(self, label, leadp):
        # now the REFERENCE to the original lead
        returnRid = leadp.getRid()
        returnLeadId = leadp.getLabelIdPreferAutoId()

        if (label is not None) and (label.startswith(returnLeadId)):
            # in this case the label is ALREADY what we would use as return text so we don't need to repeat
            pageNumberStyle = "page"
            returnTextLatex = makeLatexLinkToRid(returnRid, "", pageNumberStyle)
            fromLatex = "{}".format(returnTextLatex)
        else:
            pageNumberStyle = "onpage"
            returnTextLatex = makeLatexLinkToRid(returnRid, returnLeadId, pageNumberStyle)
            fromLatex = "{}".format(returnTextLatex)
        #
        return fromLatex






    def addChunkToSetCurrentColumnCount(self, item, parentSection):
        columnCount = self.calcColumnCountForSectionOrLead(item, parentSection)
        self.addChunkToSetCurrentColumnCountTo(columnCount)
    
    def addChunkToSetCurrentColumnCountTo(self, newColumnCount):
        currentColumnCount = self.getCurrentColumnCount()
        if (currentColumnCount == newColumnCount):
            # nothing to do already at this column count
            return
        # change it
        if (currentColumnCount>1):
            # we need to END our current multicol
            # do we want to turn off any "continued on the next page" stuff when we have a manual break? this only works if we are not using the environment-based style (otherwise we would not have matching begin end)
            if (DefExtraBreakWarnSecEnd):
                # i don't think it's very important
                self.chunks.append(self.breakWarnSecEnd())
            text = "\\end{multicols*}\n"
            self.chunks.append(text)
        if (newColumnCount>1):
            # start new
            text = "\\begin{multicols*}{" + str(newColumnCount) + "}\n"
            self.chunks.append(text)
        # remember
        self.setCurrentColumnCount(newColumnCount)






    def calcColumnCountForSectionOrLead(self, item, parentSection):
        isLead = isinstance(item, CbRenderLead)
        #
        if (isLead):
            columnCount = item.calcLeadColumns()
        else:
            columnCount = item.calcSectionColumns()
        #
        if (columnCount is None):
            # this should not happen as we should top out at renderdoc with defaults
            raise makeJriException("Internal Render Error: Could not find columnCount value up render hiearachy.", None)
        return columnCount








    def generateDocumentStart(self, env):
        self.generateDocumentStartDocClass(env)
        self.generateDocumentStartPackages(env)
        self.generateDocumentStartExtras(env)
        self.generateDocumentStartMetaInfo(env)
        self.generateDocumentStartBeginDoc(env)


















    def generateDocumentStartDocClass(self, env):
        # ATTN: get this from settings

        # options
        doubledSided = self.getOption("doubleSided", False)
        latexPaperSize = self.getOption("latexPaperSize", None)
        latexFontSize = self.getOption("latexFontSize", None)

        # extra options?
        extra = ""

        # latex stuff
        if (doubledSided):
            sidedLatex = "twoside=semi"
        else:
            sidedLatex = "oneside"




        # document class; sets:
        #  whether it is double sided (page numbers alternate sides) or not (always in same corner)
        #  the base font size (in points)
        #  the paper size ["letter", "A4", "A5", etc.]
        # for KOMA script, the DIV value is: DIV=15 means that the page height is divided into 15 units. The top margin is one unit, the bottom gets two units and the remaining units go to the text height
        text = r"\documentclass[" + sidedLatex + ", openany, " + str(latexFontSize) + "pt, paper=" + latexPaperSize +", DIV=15" + extra + "]{scrbook}%" + "\n"
        self.chunks.append(text)




















    def generateDocumentStartPackages(self, env):


        # packages
        text = r"""
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{textcomp}
\usepackage{lastpage}
\usepackage{FiraSans} % font
\usepackage{librebaskerville} % font
\usepackage{setspace}
\usepackage{graphicx} % for graphics
\usepackage{amssymb} % symbols
\usepackage{amsthm} % symbols
\usepackage{amsmath} % symbols
\usepackage{wasysym} % symbols
\usepackage{MnSymbol} % symbols
\usepackage{parskip}
\usepackage{scrlayer-scrpage} % main document class
\usepackage{tocloft} % table of contents support
\usepackage{multicol} % multi-column support
\usepackage[pdfusetitle,colorlinks=true,linkcolor=blue,filecolor=magenta,urlcolor=cyan,bookmarksopen=true,bookmarksopenlevel=1]{hyperref} % support for links, bookmarks, etc.
\usepackage{tikz}
\usepackage{clock} % clock symbols
\usepackage[clock]{ifsym} % clock symbols
\usepackage{fontawesome5} % various symbols
\usepackage{pgfornament} % ornaments like tombstones between leads
\usepackage{fancybox} % fancy boxed blocks of text

\usepackage{aurical}
\usepackage{listings} % checkbox lists
\usepackage{pdfpages} % embedding pdf files?
\usepackage{enumitem} % lists of items
\usepackage{refcount} % new ContinuedOnNextPage Stuff
\usepackage{tabularray} % autosizing tables (tabulary seemed broken)
\usepackage[export]{adjustbox} % for image alignment in table cells
\usepackage{printlen} % for reporting image sizes

\usepackage{options} % needed by others? see https://ctan.math.utah.edu/ctan/tex-archive/macros/latex/contrib/longfbox/longfbox.sty
\usepackage{pict2e} % see above (longbox needs?)
\usepackage[most]{tcolorbox} % more fancy boxed blocks
\usepackage{longfbox} % more fancy boxed blocks
\usepackage{lettrine} % first big character drop caps
\usepackage{lipsum} % for testing blocks of text
\usepackage{marginnote} % margin notes
%\usepackage{epigraph} % for nice looking quotes
"""
        self.chunks.append(text)


        # fakepar is use for kludge lettrine workaround
        text = ""
        text += r"\def\fakepar{\hfill\mbox{}\vspace{\parskip}\newline\mbox{}\hspace{\parindent}}" + "\n"
        self.chunks.append(text)

        # % \usepackage{printlen} % for reporting image sizes and converting - UNUSED

        # auto quote packages
        text = ""
        autoStyleQuotes = self.getOption("autoStyleQuotes", False)
        # ATTN: csquotes needs more setting
        if True and (autoStyleQuotes) :
            text += r"\usepackage[english]{babel}" + "\n"
            text += r"\usepackage[autostyle, english = american, debug=true]{csquotes}" + "\n"
        else:
            text += r"\usepackage[]{csquotes}" + "\n"
        self.chunks.append(text)




    def generateDocumentStartExtras(self, env):
        # see https://tex.stackexchange.com/questions/656716/changing-contentsname-in-scrartcl for how to change contentsname to blank
        # auto quote packages
        autoStyleQuotes = self.getOption("autoStyleQuotes", False)
        optionUseCalendar = True

        text = r"""
\raggedbottom
\raggedcolumns
"""

        # section formatting and toc
        text += r"""
% section and chapter name formatting part 1
\let\origaddcontentsline\addcontentsline
\let\origcftaddtitleline\cftaddtitleline
\setlength{\columnsep}{1cm}%
\onehalfspacing%
\setlength{\parindent}{0pt}%
\RedeclareSectionCommand[beforeskip=0pt,afterskip=0.5cm]{chapter}
\renewcommand*{\chapterheadstartvskip}{\vspace*{-1.0cm}}
\renewcommand*{\chapterheadendvskip}{\vspace*{0.5cm}}
\renewcommand{\cftsecfont}{\ttfamily}
\renewcommand{\cftsubsecfont}{\ttfamily}
\renewcommand{\cftsubsubsecfont}{\ttfamily}
\renewcommand{\cftchappagefont}{\ttfamily}
\renewcommand{\cftsecpagefont}{\ttfamily}
\renewcommand{\cfttoctitlefont}{\fontsize{25}{30}\selectfont\bfseries\scshape}
\newenvironment{cb_quoteenv}{}{} % quote environment for when we need one
"""

        # more section formatting
        # fix for table of contents SUB section not getting proper font of ttfamily set above
        text += "\\DeclareTOCStyleEntries[entryformat=\\ttfamily, pagenumberformat=\\ttfamily]{tocline}{subsection, subsubsection}\n"
        # text += "\\DeclareTOCStyleEntries[entryformat=\ttfamily, pagenumberformat=\ttfamily]{tocline}{chapter, section, subsection, subsubsection}\n"

        # more section formatting
        text += r"""
% section and chapter name formatting part 2
\renewcommand\cftchapafterpnum{\vskip-2pt}
\renewcommand\cftsecafterpnum{\vskip-2pt}
\newcommand\cbsubheading[1]{\vskip-0.35cm\textbf{#1}}
\renewcommand\contentsname{}
\defcaptionname{\languagename}{\contentsname}{}
\addtokomafont{chapter}{\fontsize{50}{60}\selectfont}\renewcommand{\cftchapfont}{\ttfamily}
\setkomafont{disposition}{\bfseries}
\setlength{\cftbeforetoctitleskip}{-2em}
\setlength{\cftaftertoctitleskip}{-2em}
"""

        # custom checkbox lists (uses \usepackage{enumitem} above)
        if (True):
            text += r"""
% checkbox lists, etc (uses package enumitem)
\newlist{todolist}{itemize}{2}
\setlist[todolist]{label=\openbox}
\newlist{nobulletlist}{itemize}{2}
\setlist[nobulletlist]{label=}
"""

        # kludge fix for longfbox (known bug workaround see https://tex.stackexchange.com/questions/571207/error-with-longfbox-package)
        if (True):
            text += r"""
% kludge fix for longfbox (see code comments)
\makeatletter
\newdimen\@tempdimd
\makeatother
"""


        # calendar
        if (optionUseCalendar):
            text += r"""
% calendar support
\usetikzlibrary{calendar,shapes.misc}
\makeatletter%
\tikzoption{day headings}{\tikzstyle{day heading}=[#1]}
\tikzstyle{day heading}=[]
\tikzstyle{day letter headings}=[
    execute before day scope={ \ifdate{day of month=1}{%
      \pgfmathsetlength{\pgf@ya}{\tikz@lib@cal@yshift}%
      \pgfmathsetlength\pgf@xa{\tikz@lib@cal@xshift}%
      \pgftransformyshift{-\pgf@ya}
      \foreach \d/\l in {0/M,1/T,2/W,3/T,4/F,5/S,6/S} {
        \pgf@xa=\d\pgf@xa%
        \pgftransformxshift{\pgf@xa}%
        \pgftransformyshift{\pgf@ya}%
        \node[every day,day heading]{\l};%
      } 
    }{}%
  }%
]
\makeatother%
"""


        # auto quotes makes nicer left and right quote marks that look different
        # ATTN: this can cause errors that are hard to find and diagnose on unbalanced quotes
        # if you find a weird error you can't diagnose try disabling this
        if (autoStyleQuotes):
            text += "\\MakeOuterQuote{\"} % Automatically use different left and right quote mark symbols (WARNING: This can lead to hard to diagnose errors on imbalanced double quotes!!)\n"

        # add text
        self.chunks.append(text)






    def generateDocumentStartMetaInfo(self, env):
        info = env.getEnvValueUnwrapped(None, "info", None)
        if (info is None):
            raise self.makeRenderException(None, "Could not find 'info' object for game to retrieve author, etc.")
        #
        titleStr = getUnsafeDictValueAsString(env, info, "title", "n/a")
        authorsStr = getUnsafeDictValueAsString(env, info, "authors", "n/a")
        versionStr = getUnsafeDictValueAsString(env, info, "version", "n/a")
        dateStr =  getUnsafeDictValueAsString(env, info, "versionDate", "n/a")
        keywordsStr =  getUnsafeDictValueAsString(env, info, "keywords", "")
        if (keywordsStr!=""):
            keywordsStr = "casebook, " + keywordsStr
        else:
            keywordsStr = "casebook"
        #
        # see https://www.karlrupp.net/2016/01/pdf-metadata-in-latex-documents/
        #
        text = "\n"
        text += "% embed info into generated pdf\n"
        text += "\\hypersetup{\n"
        text += "pdfauthor={{{}}},\n".format(authorsStr)
        text += "pdftitle={{{}}},\n".format(titleStr)
        text += "pdfsubject={{New York Noir - {} v{}}},\n".format(titleStr, versionStr)
        #text += "\\pdfdate={{{}}},\n".format(dateStr)
        text += "pdfkeywords={{{}}},\n".format(keywordsStr)
        text += "}\n"
        text += "\\date{{{}}}\n".format(dateStr)

        # add text
        self.chunks.append(text)












    def generateDocumentStartBeginDoc(self, env):
        # start doc
        text = "\n\n"
        text += "\\begin{document}\n\n"
        self.chunks.append(text)


        # other startup stuff
        text = r"""
\normalsize%
\clearpairofpagestyles
"""

        # latex support code to help issue a "Continued on the next page" line in footer if we break a lead between pages
        # see also breakWarnSecStart(), breakWarnSecEnd()
        text += r"""
% footers get page numbers and a "continued on next page" line if appropriate
\rofoot*{{\pagemark}\scriptsize\mycontdfoot\textbf}
\lefoot*{{\pagemark}\scriptsize\mycontdfoot\textbf}
\newif\ifwarnpgbrk
\warnpgbrkfalse
\newcounter{question}
\newcommand\mycontdfoot{\ifwarnpgbrk \begin{center}CONTINUED ON NEXT PAGE\end{center} \fi}
\newcommand\mycontdfootLabelMethodUnused{\ifnum\getpagerefnumber{question-start-\thequestion}<\getpagerefnumber{question-end-\thequestion} \begin{center}CONTINUED ON NEXT PAGE\end{center} \fi}
\newenvironment{breakwarnsec}{\warnpgbrktrue}{}
"""




        # add text
        self.chunks.append(text)










    def generateDocumentEnd(self, env):
        buildStr = env.getBuildString()
        currentDateStr = jrfuncs.getNiceCurrentDateTime()
        text = "\n\\end{{document}}\n\n% Generated by casebook tool {} on {}\n\n".format(buildStr, currentDateStr)
        # add text
        self.chunks.append(text)


