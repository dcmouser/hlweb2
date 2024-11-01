# Report generating helpers


# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
from .jriexception import *

from .jrastvals import AstValString
from .jrast import JrAstResultList
from .jrastfuncs import isTextLatexVouched

from .jrastfuncs import vouchForLatexString
from .cbfuncs_core_support import wrapTextInLatexBox, generateLatexBoxDict, generateLatexForSymbol, generateImageEmbedLatex, generateImageSizeLatex

from .cbdeferblock import makeLatexReferenceToLead

from .jrastutilclasses import QuoteBalance



def generateAllAuthorReports(renderDoc, env, targetSection):
    generateAddReportTagUsage(renderDoc, env, targetSection)
    generateAddReportCheckboxes(renderDoc, env, targetSection)
    generateAddReportDays(renderDoc, env, targetSection)
    generateAddReportLeadSummary(renderDoc, env, targetSection)
    generateAddReportLargestLeads(renderDoc, env, targetSection)
    generateAddReportLongestTimeLeads(renderDoc, env, targetSection)
    generateAddReportQuotesInLeads(renderDoc, env, targetSection)
    #
    generateAddReportAuthorNotes(renderDoc, env, targetSection)
    generateAddReportLeadDatabaseDiscrepencies(renderDoc, env, targetSection)
    #
    generateAddReportEmbeddedPdf(renderDoc, env, targetSection)
    generateAddReportEmbeddedImages(renderDoc, env, targetSection)
    generateAddReportUnusedImages(renderDoc, env, targetSection)
    generateAddReportIncludedSource(renderDoc, env, targetSection)
    #
    generateAddReportWarnings(renderDoc, env, targetSection)
    #
    generateLeadReportExtras(renderDoc, env, targetSection)


def generateAddReportTagUsage(renderDoc, env, targetSection):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Tag Report"
    label = None
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None)
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd("The following is a report of all the tags used in this case, including documents.\n")
    #
    tagManager = env.getTagManager()
    tagList = tagManager.getTagList()
    tagList = tagManager.sortByTypeAndObfuscatedLabel(tagList)
    for tag in tagList:
        tagTextIdLabel = tag.getNiceIdWithLabel()
        tagTextObfuscated = tag.getNiceObfuscatedLabelWithType(True, False)
        results.flatAdd("\n")
        results.flatAdd("### {} ({}):\n".format(tagTextObfuscated, tagTextIdLabel))
        # now usages
        addTagUseList(renderDoc, results, tag, "Gained", tag.getGainList())
        addTagUseList(renderDoc, results, tag, "Checked", tag.getCheckList())
        # deadline
        deadlineDay = tag.getDeadline()
        if (deadlineDay is not None) and (deadlineDay!=-1):
            results.flatAdd(" * Deadline: Day {}.\n".format(deadlineDay))
        leadref = tagManager.findHintLeadForTag(env, renderDoc, tag)
        if (leadref is not None):
            leadLinkLatex = makeLatexReferenceToLead(leadref, True, True, True, True, True)
            results.flatAdd(" * Hint: ")
            results.flatAdd(leadLinkLatex)
            results.flatAdd("\n")
        if (leadref is None) and (deadlineDay is not None) and (deadlineDay!=-1):
            results.flatAdd(" * ")
            results.flatAdd(vouchForLatexString("{\\color{red} WARNING: This tag has a deadline but no hint (!)}\n",True))
            results.flatAdd("\n")

    # set text
    results.flatAdd("\n\n")
    lead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, lead, targetSection, renderDoc)


def addTagUseList(renderDoc, results, tag, label, useList):
    if (len(useList)==0):
        results.flatAdd(" * {}: N/A\n".format(label))
        return
    for leadref in useList:
        leadLinkLatex = makeLatexReferenceToLead(leadref, True, True, True, True, True)
        results.flatAdd(" * {}: ".format(label))
        results.flatAdd(leadLinkLatex)
        results.flatAdd("\n")




def generateAddReportCheckboxes(renderDoc, env, targetSection):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Checkbox Report"
    label = None
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None)
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd("The following is a report of all times when the player is instructed to mark checkboxes in this case.\n")

    #
    checkboxManager = env.getCheckboxManager()
    checkmarks = checkboxManager.getCheckmarks()
    for key, checkmark in checkmarks.items():
        checkmarkTypeName = checkmark.getTypeName()
        checkmarkUses = checkmark.getUses()
        results.flatAdd("\n")
        results.flatAdd("### {}:\n".format(checkmarkTypeName))
        if (len(checkmarkUses)==0):
            results.flatAdd(" * N/A\n")
        else:
            for checkmarkUse in checkmarkUses:
                leadref = checkmarkUse["lead"]
                markCount = checkmarkUse["count"]
                leadLinkLatex = makeLatexReferenceToLead(leadref, True, True, True, True, True)
                results.flatAdd(" * Mark {}: ".format(markCount))
                results.flatAdd(leadLinkLatex)
                results.flatAdd("\n")

    # set text
    results.flatAdd("\n\n")
    lead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, lead, targetSection, renderDoc)



def generateAddReportDays(renderDoc, env, targetSection):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Day Report"
    label = None
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None)
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd("The following is a report of the days defined for this case.\n")

    #
    dayManager = env.getDayManager()
    tagManager = env.getTagManager()
    # iterate each day
    for key, day in dayManager.getDayDict().items():
        results.flatAdd("### Day {}:\n".format(day.dayNumber))
        results.flatAdd(" * Starts: {}\n".format(jrfuncs.hourAmPm(day.startTime)))
        results.flatAdd(" * Ends: {}\n".format(jrfuncs.hourAmPm(day.endTime)))
        #
        dayNumber = day.getDayNumber()
        # now iterate all tags with this day deadline
        tagList = tagManager.findDeadlineTags(dayNumber)
        tagList = tagManager.sortByTypeAndObfuscatedLabel(tagList)
        if (len(tagList)>0):
            results.flatAdd(" * Tag deadlines:\n".format(day.startTime))
            for tag in tagList:
                # create link from day to tag for deadline
                tagTextIdLabel = tag.getNiceIdWithLabel()
                tagTextObfuscated = tag.getNiceObfuscatedLabelWithType(True, False)
                results.flatAdd("   * {} ({})\n".format(tagTextIdLabel, tagTextObfuscated))

    # set text
    results.flatAdd("\n\n")
    lead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, lead, targetSection, renderDoc)







def generateAddReportFilteredNotes(renderDoc, env, targetSection, reportTitle, filterString, itemLabel, introText):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = reportTitle
    label = None
    # create "lead" to hold this report
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None)
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd(introText + "\n")

    filteredNotes = env.getInterp().getNotesFiltered(None, filterString)
    filteredNotesCount = len(filteredNotes)
    if (filteredNotesCount==0):
        results.flatAdd("{} {}s.\n".format(filteredNotesCount, itemLabel))
    else:
        results.flatAdd("{} {}{}:\n".format(filteredNotesCount, itemLabel, jrfuncs.plurals(filteredNotesCount,"s")))
        #results.flatAdd(vouchForLatexString("\\begin{sloppypar}\n", False))
    for note in filteredNotes:
        results.flatAdd(" * ")
        latexLineText = note.getMessageAsLatex()
        if (latexLineText is not None):
            results.flatAdd(vouchForLatexString(latexLineText, True))
        else:
            plainLineText = note.getMessage()
            results.flatAdd(plainLineText)
        #
        leadref = note.getLead()
        if (leadref is not None):
            leadLinkLatex = makeLatexReferenceToLead(leadref, True, True, True, True, True)
            results.flatAdd(": ")
            results.flatAdd(leadLinkLatex)
        results.flatAdd(".\n")
    if (filteredNotesCount>0):
        #results.flatAdd(vouchForLatexString("\\end{sloppypar}\n", False))
        pass

    # set text
    results.flatAdd("\n\n")
    lead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, lead, targetSection, renderDoc)



def generateAddReportWarnings(renderDoc, env, targetSection):
    generateAddReportFilteredNotes(renderDoc, env, targetSection, "Warning Report", "warning", "Warning", "The following is a report of any warnings generated while building this case.")

def generateAddReportEmbeddedPdf(renderDoc, env, targetSection):
    generateAddReportFilteredNotes(renderDoc, env, targetSection, "Embedded PDF Report", "embedPdf", "PDF file", "The following is a report of all pdf files embedded into this case book.")



def generateAddReportIncludedSource(renderDoc, env, targetSection):
    generateAddReportFilteredNotes(renderDoc, env, targetSection, "Included Source Report", "embedSource", "Source file", "The following is a report of all source files included inside the source of this case book.")

def generateAddReportAuthorNotes(renderDoc, env, targetSection):
    generateAddReportFilteredNotes(renderDoc, env, targetSection, "Author Notes Report", "authorNote", "Author note", "The following is a report of all author notes in this case book.")

def generateAddReportLeadDatabaseDiscrepencies(renderDoc, env, targetSection):
    generateAddReportFilteredNotes(renderDoc, env, targetSection, "Lead Database Report", "leadDbWarning", "Lead Db Warning", "The following is a report of all potential lead database warnings.")










def generateAddReportLargestLeads(renderDoc, env, targetSection):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Largest Leads"
    label = None
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None)
    #
    topN = 20
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd("The following is a list of the top {} largest leads.\n".format(topN))

    # get top N leads
    leads = renderDoc.calcTopNLeads(topN, lambda lead: (-1*lead.calcStatPlainTextWordCount()["words"]) if (lead.getIsMainLead()) else 0)

    for leadref in leads:
        # make a reference to this lead
        leadLinkLatex = makeLatexReferenceToLead(leadref, True, True, True, True, True)
        sizeStr = leadref.calcStatPlainTextWordCount()["words"]
        results.flatAdd(" * {} words: ".format(sizeStr))
        results.flatAdd(leadLinkLatex)
        results.flatAdd("\n")

    # set text
    results.flatAdd("\n\n")
    lead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, lead, targetSection, renderDoc)












def generateAddReportLongestTimeLeads(renderDoc, env, targetSection):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Longest Time Leads"
    label = None
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None)
    #
    topN = 20
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd("The following is a list of the top {} longest time duration leads.\n".format(topN))

    # get top N leads
    leads = renderDoc.calcTopNLeads(topN, leadTimeCalcForSorting)

    for leadref in leads:
        # make a reference to this lead
        time = leadref.getTime()
        if (time is None) or (time<=0):
            continue
        leadLinkLatex = makeLatexReferenceToLead(leadref, True, True, True, True, True)
        sizeStr = jrfuncs.minutesToTimeString(leadref.getTime())
        results.flatAdd(" * {}: ".format(sizeStr))
        results.flatAdd(leadLinkLatex)
        results.flatAdd("\n")

    # set text
    results.flatAdd("\n\n")
    lead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, lead, targetSection, renderDoc)


def leadTimeCalcForSorting(lead):
    if (not lead.getIsMainLead()):
        return 0
    time = lead.getTime()
    if (time is None):
        return 0
    if (time==-1):
        return 0
    return -1*time




def generateAddReportQuotesInLeads(renderDoc, env, targetSection):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Quote Warnings in Leads"
    label = None
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None)
    #
    # build text contents
    results = JrAstResultList()
    errorCount = 0

    # get list of all leads
    leads = renderDoc.calcFlatLeadList()

    # get top N leads
    for leadref in leads:
        leadText = leadref.getFullRenderTextForDebug()
        quoteBalance = QuoteBalance()
        quoteBalance.scanAndAdjustCounts(leadText, "n/a", 0,0)
        messages = quoteBalance.getProblemList()
        if (len(messages)>0):
            leadLinkLatex = makeLatexReferenceToLead(leadref, True, True, True, True, True)
            results.flatAdd(leadLinkLatex)
            results.flatAdd("\n")
            for message in messages:
                msg = message["msg"]
                if ("locString" in message):
                    locString = message["locString"]
                    results.flatAdd(" * {} @ {}\n".format(msg, locString))
                else:
                    results.flatAdd(" * {}\n".format(msg))
            errorCount += 1
        results.flatAdd("\n")

    if (errorCount==0):
        results.flatAdd(" * No quote problems found in leads.\n")

    # set text
    results.flatAdd("\n\n")
    lead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, lead, targetSection, renderDoc)








def generateAddReportLeadSummary(renderDoc, env, targetSection):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Lead Summary"
    label = None
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None)
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd("The following is a report summarizing the leads for this case.\n")

    leadCount = renderDoc.calcLeadCount()
    plainTextWordCount = renderDoc.calcStatPlainTextWordCount()
    # deferred stats line
    results.flatAdd(" * {} Leads\n".format(leadCount))
    results.flatAdd(" * {} Words\n".format(jrfuncs.niceLargeNumberStr(plainTextWordCount["words"])))
    results.flatAdd(" * {}\n".format(jrfuncs.niceFileSizeStr(plainTextWordCount["bytes"])))
    results.flatAdd("\n")

    # set text
    results.flatAdd("\n\n")
    lead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, lead, targetSection, renderDoc)
















def generateLeadReportExtras(renderDoc, env, targetSection):
    # walks all leads and adds extra info to their contents with logic annotations

    # get list of all leads
    leads = renderDoc.calcFlatLeadList()

    interp = renderDoc.getInterp()
    mindManager = interp.getMindManager()
    tagManager = env.getTagManager()

    boxStyle = "report"
    symbolName = "report"
    ignoreLinkTypeList = ["go", "inlines", "inlineb", "refers", "returns"]

    # now walk leads, and see if a lead has LOGIC info we want to add to bottom of it
    for lead in leads:
        relatedLinks = mindManager.calcRelatedLeadLinks(env, lead, ignoreLinkTypeList)

        tag = None
        role = lead.getRole()
        if (role is not None):
            roleType = role["type"]
            if ("tag" in role):
                tag = role["tag"]

        if (len(relatedLinks)>0) or (tag is not None):
            results = JrAstResultList()

            # box start
            if (boxStyle):
                latexBoxDict = generateLatexBoxDict(boxStyle, None)
                latex = latexBoxDict["start"]
                if (symbolName is not None) and (symbolName!=""):
                    latex += generateLatexForSymbol(symbolName, None, None)
                #
                results.flatAdd(vouchForLatexString(latex, False))
            #
            results.flatAdd("Debug report:\n")

            # build results
            for relatedLink in relatedLinks:
                label = relatedLink["label"]
                leadref = relatedLink["relatedLead"]
                if (leadref is not None):
                    # make a reference to this lead
                    leadLinkLatex = makeLatexReferenceToLead(leadref, True, True, True, True, True)
                    results.flatAdd(" * {}: ".format(label))
                    results.flatAdd(leadLinkLatex)
                else:
                    results.flatAdd(" * {}".format(label))
                results.flatAdd("\n")

            # IF this is a TAG related lead (document or hint), then add list of gain/check locations, just as if this was a tag report
            if (tag is not None):
                # usages
                addTagUseList(renderDoc, results, tag, "Gained", tag.getGainList())
                addTagUseList(renderDoc, results, tag, "Checked", tag.getCheckList())
                deadlineDay = tag.getDeadline()
                #if WE are not a hint, show HINTS to us
                if (roleType != "hint"):
                    # IF this LEAD is not a hint, but it is attached to a tag with a hint, show the hint for this this tag role (ie we are a doc, we want to show hint)
                    leadref = tagManager.findHintLeadForTag(env, renderDoc, tag)
                    if (leadref is not None):
                        leadLinkLatex = makeLatexReferenceToLead(leadref, True, True, True, True, True)
                        results.flatAdd(" * Hint: ")
                        results.flatAdd(leadLinkLatex)
                        results.flatAdd("\n")
                    if (leadref is None) and (deadlineDay is not None) and (deadlineDay!=-1):
                        results.flatAdd(" * ")
                        results.flatAdd(vouchForLatexString("\\color{red} WARNING: This tag has a deadline but no hint (!)}\n",True))
                        results.flatAdd("\n")
                if (roleType != "doc"):
                    # this lead might be a hint -- let's see if there is a DOCUMENT lead also for this tag, if so, add a link to it
                    leadref = findDocumentLeadForTag(env, leads, tag)
                    if (leadref is not None):
                        leadLinkLatex = makeLatexReferenceToLead(leadref, True, True, True, True, True)
                        results.flatAdd(" * Document: ")
                        results.flatAdd(leadLinkLatex)
                        results.flatAdd("\n")
                # deadline
                if (deadlineDay is not None) and (deadlineDay!=-1):
                    results.flatAdd(" * Deadline: Day {}.\n".format(deadlineDay))

            # box end
            if (boxStyle):
                latex = latexBoxDict["end"]
                results.flatAdd(vouchForLatexString(latex, False))

            # add new text to output, in box
            lead.addBlocks(results)



def findDocumentLeadForTag(env, leads, tag):
    # see if we can find the lead that IS a doc, whose tag matches the one we are looking for
    for lead in leads:
        role = lead.getRole()
        if (role is not None):
            roleType = role["type"]
            if (roleType=="doc"):
                if ("tag" in role):
                    docTag = role["tag"]
                    if (docTag == tag):
                        return lead
    return None




























def generateAddReportEmbeddedImages(renderDoc, env, targetSection):
    filterString = "embedImage"
    itemLabel = "Image file"

    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Embedded Image Report"
    label = None
    # create "lead" to hold this report
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None)
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd("The following is a report of all image files used by this case book." + "\n")

    filteredNotes = env.getInterp().getNotesFiltered(None, filterString)
    filteredNotesCount = len(filteredNotes)
    if (filteredNotesCount==0):
        results.flatAdd("{} {}s.\n".format(filteredNotesCount, itemLabel))
    else:
        results.flatAdd("{} {}{}:\n".format(filteredNotesCount, itemLabel, jrfuncs.plurals(filteredNotesCount,"s")))

    # thumbnail properties
    widthStr = "1in"
    heightStr = "1in"
    borderWidth = 0
    padding = 0
    optionLongTable = True
    optionCalcImageSize = False

    if (len(filteredNotes)>0):
        #
        if (optionLongTable):
            # latex is evil
            latex = r"\DefTblrTemplate{firsthead, middlehead,lasthead}{default}{}\begin{longtblr}{l X}" + "\n"
            results.flatAdd(vouchForLatexString(latex, False))

        # one table for each (we could put them all in one big table with many rows but not sure what the benefit is)
        for note in filteredNotes:
            # make like a row with embedded image and text
            extras = note.getExtras()

            # get components
            imageFullPath = jrfuncs.getDictValue(extras,"img")
            imageLatex = generateImageEmbedLatex(imageFullPath, widthStr, heightStr, borderWidth, padding, False, "t")
            #
            labelLatex = note.getMessageAsLatex()

            if (optionCalcImageSize):
                labelLatex += " (" + generateImageSizeLatex(imageFullPath) + ")"

            #
            leadref = note.getLead()
            if (leadref is not None):
                leadLinkLatex = makeLatexReferenceToLead(leadref, True, True, True, True, False)
            else:
                leadLinkLatex = "(used location unknown)"

            # wrap in tabular orientation
            latex = ""
            if (not optionLongTable):
                latex += r"\begin{tblr}{l X}" + "\n"
            
            latex += "{" + imageLatex + "} & {" + labelLatex + " at " + leadLinkLatex + "}\n"

            if (not optionLongTable):
                latex += r"\end{tblr}" + "\n\n"
            else:
                latex += r" \\" + "\n"
        
            # add the latex
            results.flatAdd(vouchForLatexString(latex, False))

        if (optionLongTable):
            latex = r"\end{longtblr}" + "\n\n"
            results.flatAdd(vouchForLatexString(latex, False))

    # set text
    results.flatAdd("\n\n")
    lead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, lead, targetSection, renderDoc)



def generateAddReportUnusedImages(renderDoc, env, targetSection):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Unused Images"
    label = None
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None)
    #
    imageHelper = env.getFileManagerImagesCase()
    unusedFiles = imageHelper.getUnusedFiles()
    numFiles = imageHelper.getCount()
    #
    # thumbnail properties
    widthStr = "1in"
    heightStr = "1in"
    borderWidth = 0
    padding = 0
    optionLongTable = True
    optionCalcImageSize = False
    #
    # build text contents
    results = JrAstResultList()
    if (len(unusedFiles)==0):
        if (numFiles == 0):
            results.flatAdd("There are no uploaded image files in this case.\n")
        else:
            results.flatAdd("All {} of {} uploaded image files for this case have been used.\n".format(numFiles, numFiles))
    else:
        results.flatAdd("The following is a list of the {} of {} uploaded image files that have NOT been used in the case book.\n".format(len(unusedFiles), numFiles))


    if (len(unusedFiles)>0):
        #
        if (optionLongTable):
            # latex is evil
            latex = r"\DefTblrTemplate{firsthead, middlehead,lasthead}{default}{}\begin{longtblr}{l X}" + "\n"
            results.flatAdd(vouchForLatexString(latex, False))
        #
        for unusedFile in unusedFiles:
            k = "local/" + unusedFile[0]
            imageFullPath = unusedFile[1]
            imageLatex = generateImageEmbedLatex(imageFullPath, widthStr, heightStr, borderWidth, padding, False, "t")
            labelLatex = "\\path{" + k + "}"

            if (optionCalcImageSize):
                labelLatex += " (" + generateImageSizeLatex(imageFullPath) + ")"

            # wrap in tabular orientation
            latex = ""
            if (not optionLongTable):
                latex += r"\begin{tblr}{l X}" + "\n"
            latex += "{" + imageLatex + "} & {" + labelLatex + "}\n"
            if (not optionLongTable):
                latex += r"\end{tblr}" + "\n\n"
            else:
                latex += r" \\" + "\n"

            # add the latex
            results.flatAdd(vouchForLatexString(latex, False))
        #
        if (optionLongTable):
            latex = r"\end{longtblr}" + "\n\n"
            results.flatAdd(vouchForLatexString(latex, False))

    # set text
    results.flatAdd("\n\n")
    lead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, lead, targetSection, renderDoc)