# Report generating helpers


# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
from .jriexception import *

from .jrastvals import AstValString
from .jrast import JrAstResultList
from .jrastfuncs import isTextLatexVouched

from .jrastfuncs import vouchForLatexString, convertEscapeUnsafePlainTextToLatex
from .cbfuncs_core_support import wrapInLatexBox, wrapInLatexBoxJustStart, wrapInLatexBoxJustEnd, generateLatexForSymbol, generateImageEmbedLatex, generateImageSizeLatex, makeLatexReferenceToLead
from .cbfuncs_core_support import generateLatexForDivider

from .jrastutilclasses import JrINote, QuoteBalance

# python
import json



def generateAllAuthorReports(renderDoc, env, targetSection):
    generateAddReportConceptUsage(renderDoc, env, targetSection)
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
    generateAddReportEmbeddedImages(renderDoc, env, targetSection)
    generateAddReportUnusedImages(renderDoc, env, targetSection)
    #
    generateAddReportFingerprints(renderDoc, env, targetSection)
    #
    generateAddReportEmbeddedPdf(renderDoc, env, targetSection)
    generateAddReportIncludedSource(renderDoc, env, targetSection)
    #
    generateAddReportWarnings(renderDoc, env, targetSection)
    #
    generateAddReportWalkthrough(renderDoc, env, targetSection)
    #
    generateLeadReportExtras(renderDoc, env, targetSection)








def generateAddReportConceptUsage(renderDoc, env, targetSection):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Concept Report"
    label = None
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None, False)
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd("The following is a report of all the logic concepts used in this case, including documents.\n")
    #
    conceptManager = env.getConceptManager()
    tagList = conceptManager.getTagList()
    tagList = conceptManager.sortByTypeAndId(tagList)
    #
    for tag in tagList:
        tagTextId = tag.getId()
        tagTextLabel = tag.getLabel()
        results.flatAdd("\n")
        if (tagTextLabel!=""):
            results.flatAdd("### {} ({}):\n".format(tagTextId, tagTextLabel))
        else:
            results.flatAdd("### {}:\n".format(tagTextId))

        # now usages
        logicList =  tag.getLogicList(False)
        if (len(logicList)==0):
            results.flatAdd(" * No uses\n".format(label))
        else:
            for logicUse in logicList:
                leadref = jrfuncs.getDictValueOrDefault(logicUse, "lead", None)
                target = jrfuncs.getDictValueOrDefault(logicUse, "target", None)
                keyword = logicUse["keyword"]
                label = logicUse["label"]
                #
                fullLabel = keyword
                if (label!=""):
                    fullLabel = keyword + " ({})".format(label)
                #
                if (leadref is not None):
                    leadLinkLatex = makeLatexReferenceToLead(leadref, "report", True)
                    results.flatAdd(" * {}: ".format(fullLabel))
                    results.flatAdd(leadLinkLatex)
                    results.flatAdd("\n")
                elif (target is not None):
                    leadref = renderDoc.findLeadByIdPath(target, None)
                    if (leadref is not None):
                        leadLinkLatex = makeLatexReferenceToLead(leadref, "report", True)
                        results.flatAdd(" * {}: ".format(fullLabel))
                        results.flatAdd(leadLinkLatex)
                        results.flatAdd("\n")
                    else:
                        results.flatAdd(" * {}: ".format(fullLabel, str(target)))
                        results.flatAdd("\n")      

    # set text
    results.flatAdd("\n\n")
    lead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, lead, targetSection, renderDoc)



















def generateAddReportTagUsage(renderDoc, env, targetSection):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Tag Report"
    label = None
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None, False)
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd("The following is a report of all the tags used in this case, including documents.\n")
    results.flatAdd("\n")
    #
    tagManager = env.getTagManager()
    tagList = tagManager.getTagList()

    if (len(tagList)==0):
        results.flatAdd("* No tags defined.\n")
    else:
        # simple table, sorted by by obfuscated key
        results.flatAdd("\n\n-----\n\n### *OBFUSCATION MAP:*\n")
        tagList = tagManager.sortByTypeAndObfuscatedLabel(tagList, env, True)
        for tag in tagList:
            tagTextIdLabel = tag.getNiceIdWithLabel()
            tagTextObfuscated = tag.getNiceObfuscatedLabelWithType(True, False)
            results.flatAdd(" * {}: {}\n".format(tagTextObfuscated, tagTextIdLabel))

        # details, sorted by tupe and key
        results.flatAdd("\n\n-----\n\n### *DETAILS (sorted by tag id):*\n")
        tagList = tagManager.sortByTypeAndId(tagList)
        for tag in tagList:
            tagTextIdLabel = tag.getNiceIdWithLabel()
            tagTextObfuscated = tag.getNiceObfuscatedLabelWithType(True, False)
            results.flatAdd("\n")
            results.flatAdd("#### {} ({}):\n".format(tagTextIdLabel, tagTextObfuscated))
            # now usages
            addTagUseList(renderDoc, results, tag, "Gained", tag.getGainList(False))
            addTagUseList(renderDoc, results, tag, "Checked", tag.getCheckList(False))
            addTagUseList(renderDoc, results, tag, "Logic", tag.getLogicList(False))
            # deadline
            deadlineDay = tag.getDeadline()
            if (deadlineDay is not None) and (deadlineDay!=-1):
                results.flatAdd(" * Deadline: Day {}.\n".format(deadlineDay))
            ause = tagManager.findHintLeadForTag(env, renderDoc, tag)
            if (isinstance(ause,dict)):
                leadref = jrfuncs.getDictValueOrDefault(ause,"lead", None)
                tagLabel = jrfuncs.getDictValueOrDefault(ause,"label", "")
            else:
                leadref = ause
                tagLabel = ""
            if (leadref is not None):
                leadLinkLatex = makeLatexReferenceToLead(leadref, "report", True)
                results.flatAdd(" * Hint: ")
                results.flatAdd(leadLinkLatex)
                results.flatAdd("\n")
            elif (tagLabel!=""):
                results.flatAdd(" * {}: ".format(label, tagLabel))
                results.flatAdd("\n")
            if (leadref is None) and (deadlineDay is not None) and (deadlineDay!=-1):
                results.flatAdd(" * ")
                results.flatAdd(vouchForLatexString("{\\color{red} WARNING: This tag has a deadline but no hint (!)}\n",True))
                results.flatAdd("\n")
                # add general warning
                env.addNote(JrINote("warning", None, "Tag '{}' ({}) has deadline but no hint".format(tagTextIdLabel, tagTextObfuscated), None, None))


    # set text
    results.flatAdd("\n\n")
    lead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, lead, targetSection, renderDoc)



def addTagUseList(renderDoc, results, tag, label, useList):
    from .cbrender import CbRenderLead
    if (len(useList)==0):
        results.flatAdd(" * {}: N/A\n".format(label))
        return
    for ause in useList:
        if (isinstance(ause,dict)):
            leadref = jrfuncs.getDictValueOrDefault(ause,"lead", None)
            tagLabel = jrfuncs.getDictValueOrDefault(ause,"label", "")
            keyword = jrfuncs.getDictValueOrDefault(ause,"keyword", "")
        else:
            leadref = ause
            tagLabel = ""
            keyword = ""
        #
        if (tagLabel == ""):
            tagLabel = keyword
        if (leadref is not None) and (isinstance(leadref,str)):
            leadref = renderDoc.findLeadByIdPath(leadref, None)
        if (leadref is not None):
            leadLinkLatex = makeLatexReferenceToLead(leadref, "report", True)
            if (tagLabel!=""):
                results.flatAdd(" * {} ({}): ".format(label, tagLabel))
            else:
                results.flatAdd(" * {}: ".format(label))
            results.flatAdd(leadLinkLatex)
            results.flatAdd("\n")
        elif (tagLabel!=""):
            results.flatAdd(" * {} ({}): ".format(label, tagLabel))
            results.flatAdd("\n")



def generateAddReportCheckboxes(renderDoc, env, targetSection):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Checkbox Report"
    label = None
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None, False)
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
            markCountTotal = 0
            for checkmarkUse in checkmarkUses:
                leadref = checkmarkUse["lead"]
                markCount = checkmarkUse["count"]
                markCountTotal += markCount
                leadLinkLatex = makeLatexReferenceToLead(leadref, "report", True)
                results.flatAdd(" * Mark {}: ".format(markCount))
                results.flatAdd(leadLinkLatex)
                results.flatAdd("\n")
            results.flatAdd(" * TOTAL: {} {}s in {} place(s).".format(markCountTotal, key, len(checkmarkUses)))

    # set text
    results.flatAdd("\n\n")
    #

    #
    lead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, lead, targetSection, renderDoc)



def generateAddReportDays(renderDoc, env, targetSection):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Day Report"
    label = None
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None, False)
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
        tagList = tagManager.sortByTypeAndObfuscatedLabel(tagList, env, True)
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







def generateAddReportFilteredNotes(renderDoc, env, targetSection, reportTitle, typeFilter, itemLabel, introText):
    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = reportTitle
    label = None
    # create "lead" to hold this report
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None, False)
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd(introText + "\n")

    filteredNotes = env.getInterp().getNotesFiltered(None, typeFilter)
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
            leadLinkLatex = makeLatexReferenceToLead(leadref, "report", True)
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
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None, False)
    #
    topN = 20
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd("The following is a list of the top {} largest leads.\n".format(topN))

    # get top N leads
    leads = renderDoc.calcTopNLeads(topN, lambda lead: (-1*lead.calcStatPlainTextWordCount()["bytes"]) if (lead.getIsMainLead() and not lead.isBlank()) else 0)

    for leadref in leads:
        # make a reference to this lead
        if (not leadref.getIsMainLead()) or leadref.isBlank():
            continue

        leadLinkLatex = makeLatexReferenceToLead(leadref, "report", True)
        sizeStr = jrfuncs.niceFileSizeStr(leadref.calcStatPlainTextWordCount()["bytes"])
        wordsStr = leadref.calcStatPlainTextWordCount()["words"]
        results.flatAdd(" * {} ({} words): ".format(sizeStr, wordsStr))
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
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None, False)
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
        leadLinkLatex = makeLatexReferenceToLead(leadref, "report", True)
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
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None, False)
    #
    # build text contents
    results = JrAstResultList()
    errorCount = 0

    # get list of all leads
    leads = renderDoc.calcFlatLeadList(True)

    for leadref in leads:
        leadText = leadref.getFullRenderTextForDebug()
        leadId = leadref.getIdFallbackLabel()
        if (leadId is None):
            source = "lead <ID UNKNOWN>"
        else:
            source = "lead <" + str(leadId) + ">"
        quoteBalance = QuoteBalance()
        quoteBalance.scanAndAdjustCounts(leadText, source, 0,0)
        messages = quoteBalance.getProblemList()
        if (len(messages)>0):
            # add general warning
            env.addNote(JrINote("warning", leadref, "Quote problem in lead (see quote report)", None, None))
            #
            leadLinkLatex = makeLatexReferenceToLead(leadref, "report", True)
            results.flatAdd(leadLinkLatex)
            results.flatAdd("\n")
            results.flatAdd(vouchForLatexString(r"{\ttfamily\scriptsize ",True))
            for message in messages:
                msg = message["msg"]
                if ("locString" in message):
                    locString = message["locString"]
                    errorLine = message["errorLine"]
                    errorLineLatex = convertEscapeUnsafePlainTextToLatex(errorLine)
                    epos = message["epos"]
                    results.flatAdd(" * {} @ {}\n".format(msg, locString))
                    results.flatAdd("\n... ")
                    results.flatAdd(vouchForLatexString(errorLineLatex, True))
                    results.flatAdd("...\n")
                    results.flatAdd("... " + ("_"*epos) + "*\n\n")
                else:
                    if (False) and ("locs" in message):
                        locsText = ": " + json.dumps(message["locs"])
                    else:
                        locsText = ""
                    txtLine = "{}{}\n".format(msg, locsText)
                    txtLineEscapedLatex = convertEscapeUnsafePlainTextToLatex(txtLine)
                    results.flatAdd(" * ")
                    results.flatAdd(vouchForLatexString(txtLineEscapedLatex, True))
                    #results.flatAdd(" * {}\n".format(txtLine))
            results.flatAdd(vouchForLatexString("}"+"\n",True))
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
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None, False)
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
    leads = renderDoc.calcFlatLeadList(True)

    interp = renderDoc.getInterp()
    mindManager = interp.getMindManager()
    tagManager = env.getTagManager()
    conceptManager = env.getConceptManager()

    ignoreLinkTypeList = ["go", "inlines", "inlineb", "refers", "returns"]

    # now walk leads, and see if a lead has LOGIC info we want to add to bottom of it
    for lead in leads:
        relatedLinks = mindManager.calcRelatedLeadLinks(env, lead, ignoreLinkTypeList)

        tag = None
        role = lead.getRole()
        if (role is not None):
            roleType = role["type"]
            tag = jrfuncs.getDictValueOrDefault(role, "tag", None)

        if (len(relatedLinks)>0) or (tag is not None):
            results = JrAstResultList()

            # box start
            boxOptions = {
                "box": "report",
                "symbol": "report"
            }
            latex = wrapInLatexBoxJustStart(boxOptions)
            results.flatAdd(vouchForLatexString(latex, False))
            #
            results.flatAdd("Debug report:\n")

            # build results

            # related leads (and now tags related by logic, but we'd like to avoid gain/check links here since we list them after)
            for relatedLink in relatedLinks:
                label = relatedLink["label"]
                if ("relatedLead" in relatedLink):
                    leadref = relatedLink["relatedLead"]
                    # make a reference to this lead
                    leadLinkLatex = makeLatexReferenceToLead(leadref, "report", True)
                    results.flatAdd(" * {}: ".format(label))
                    results.flatAdd(leadLinkLatex)
                elif ("relatedObject" in relatedLink):
                    refObj = relatedLink["relatedObject"]
                    # make a reference to this lead
                    mmInfo = refObj.getMindMapNodeInfo()
                    if (mmInfo is not None):
                        relatedId = jrfuncs.getDictValueOrDefault(mmInfo, "id", "")
                        relatedType = jrfuncs.getDictValueOrDefault(mmInfo, "type", "")
                        relatedLabel = jrfuncs.getDictValueOrDefault(mmInfo, "label", "")
                        # kludgey stuff to make the debug line cleaner
                        relatedLabel = relatedLabel.replace("\n", "; ")
                        label = label.replace("Concept - ","")
                        #
                        results.flatAdd(" * {} ({}): ".format(relatedId, label))
                        results.flatAdd(" {}".format(relatedLabel))
                    else:
                        results.flatAdd(" * {}: n/a".format(label))
                else:
                    source = jrfuncs.getDictValueOrDefault(relatedLink, "source", None)
                    target = jrfuncs.getDictValueOrDefault(relatedLink, "target", None)
                    if (target is not None) and (isinstance(target,str)):
                        results.flatAdd(" * {} ({})".format(label, target))
                    elif (source is not None) and (isinstance(source,str)):
                        results.flatAdd(" * {} ({})".format(label, source))
                    else:
                        results.flatAdd(" * {}".format(label))

                #
                results.flatAdd("\n")

            # IF this is a TAG related lead (document or hint), then add list of gain/check locations, just as if this was a tag report
            if (tag is not None):
                # usages
                addTagUseList(renderDoc, results, tag, "Gained", tag.getGainList(False))
                addTagUseList(renderDoc, results, tag, "Checked", tag.getCheckList(False))
                deadlineDay = tag.getDeadline()
                #if WE are not a hint, show HINTS to us
                if (roleType != "hint"):
                    # IF this LEAD is not a hint, but it is attached to a tag with a hint, show the hint for this this tag role (ie we are a doc, we want to show hint)
                    leadref = tagManager.findHintLeadForTag(env, renderDoc, tag)
                    if (leadref is not None):
                        leadLinkLatex = makeLatexReferenceToLead(leadref, "report", True)
                        results.flatAdd(" * Hint: ")
                        results.flatAdd(leadLinkLatex)
                        results.flatAdd("\n")
                    if (leadref is None) and (deadlineDay is not None) and (deadlineDay!=-1):
                        results.flatAdd(" * ")
                        results.flatAdd(vouchForLatexString("{\\color{red} WARNING: This tag has a deadline but no hint (!)}\n",True))
                        results.flatAdd("\n")
                if (roleType != "doc"):
                    # this lead might be a hint -- let's see if there is a DOCUMENT lead also for this tag, if so, add a link to it
                    leadref = findDocumentLeadForTag(env, leads, tag)
                    if (leadref is not None):
                        leadLinkLatex = makeLatexReferenceToLead(leadref, "report", True)
                        results.flatAdd(" * Document: ")
                        results.flatAdd(leadLinkLatex)
                        results.flatAdd("\n")
                # deadline
                if (deadlineDay is not None) and (deadlineDay!=-1):
                    results.flatAdd(" * Deadline: Day {}.\n".format(deadlineDay))

            # box end
            latex = wrapInLatexBoxJustEnd(boxOptions)
            results.flatAdd(vouchForLatexString(latex, False))

            # add new text to output, in box
            lead.addBlocks(results)
















def findDocumentLeadForTag(env, leads, intag):
    # see if we can find the lead that IS a doc, whose tag matches the one we are looking for
    for lead in leads:
        role = lead.getRole()
        if (role is not None):
            roleType = role["type"]
            if (roleType=="doc"):
                tag = jrfuncs.getDictValueOrDefault(role, "tag", None)
                if (tag == intag) and (intag is not None):
                    return lead
    return None


















def generateAddReportEmbeddedImages(renderDoc, env, targetSection):
    typeFilter = ["embedImage"]
    itemLabel = "Image file"

    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Embedded Image Report"
    label = None
    # create "lead" to hold this report
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None, False)
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd("The following is a report of all image files used by this case book." + "\n")

    filteredNotes = env.getInterp().getNotesFiltered(None, typeFilter)
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
            imageFullPath = jrfuncs.getDictValue(extras, "filePath")
            if (imageFullPath is None):
                msg = "CASEBOOK ERROR: IMAGE FILE MISSING, OPTIONS CONFIGURED TO SHOW WARNING: "
                imageLatex = msg + convertEscapeUnsafePlainTextToLatex(str(extras))
                imageLatex += "\n\n"
            else:
                caption = None
                optionWrapText = False
                imageLatex = generateImageEmbedLatex(env, imageFullPath, widthStr, heightStr, borderWidth, padding, "left", "t", caption, None, None, False, optionWrapText)
            #
            labelLatex = note.getMessageAsLatex()

            if (optionCalcImageSize) and (imageFullPath is not None):
                labelLatex += " (" + generateImageSizeLatex(imageFullPath) + ")"

            #
            leadref = note.getLead()
            if (leadref is not None):
                leadLinkLatex = makeLatexReferenceToLead(leadref, "report", False)
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
    lead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None, False)
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
            caption = None
            optionWrapText = False
            imageLatex = generateImageEmbedLatex(env, imageFullPath, widthStr, heightStr, borderWidth, padding, "left", "t", caption, None, None, False, optionWrapText)
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
















# ---------------------------------------------------------------------------
def generateAddReportWalkthrough(renderDoc, env, targetSection):
    # we want to create an approximate (imperect) draft walkthrough automatically using logic/mindmap stuff

    from .cbrender import CbRenderLead
    id = "Walthrough Report"
    label = None
    reportLead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None, False)

    # set text
    results = JrAstResultList()

    # build the report into results

    # Here is the basic process
    # A walkthrough explains a process that discovers the REQUIRED tags (and nothing else)
    # we know which tags are required on each day
    # so we will build a walkthrough by day
    # for each day we will generate a path that follows the plot map connections to discover every required tags for the day

    # track the walkthrough
    visitedLeads = []
    foundTags = []

    # walk through each day
    # for each day:
    #   add the leads associated with that day as visited leads?
    #   get the list of required tags
    #   then for each required tag:
    #     if we have already found it in progress of finding another, skip it
    #     if not, generate a sub-walkthrough for that tag, keeping in mind other leads we have already seen
    #         to generate a sub-walkthrough, start at (the/a) lead that gives it, and walk backward until we hit a lead we have already visited
    #     add that sub-walkthrough to the list of visited leads and foundTags
    # Issues: There may be multiple ways to get to a required tag, and indeed multiple leads that provide a required tag; how do we handle this?
    #  I claim that the "best" solution might be to either pick the shortest path to get the required tags, but we might settle for finding one random


    dayManager = env.getDayManager()
    tagManager = env.getTagManager()

    # iterate each day
    for key, day in dayManager.getDayDict().items():
        dayNumber = day.getDayNumber()
        # get list of rags REQUIRED by this day
        tagList = tagManager.findDeadlineTags(dayNumber)
        if (len(tagList)==0):
            continue
        dayString = day.getDayNumberDateLong()
        results.flatAdd("Walkthrough for {}:\n\n".format(dayString))
        walkthroughLines = []
        for tag in tagList:
            tagLabel = tag.getNiceIdWithLabelAndObfuscation()
            if (tag in foundTags):
                # already found this tag
                line = "* Already incidentally found tag {}.\n".format(tagLabel)
                continue
            line = "* Find tag {}.\n".format(tagLabel)
            walkthroughLines.append(line)
            # generate subwalkthrough to find tag

#            if (tag.getId()=="cond.walzRoom"):
#                jrprint("ATTN: DEBUG STOP")

            subWalkthroughs = findSubWalkthroughsToTag(env, tag, visitedLeads)
            if (len(subWalkthroughs)==0):
                line = "    * Failed to find walkthrough.\n"
                walkthroughLines.append(line)
                continue
            # pick ONE walkthrough (of potentially many)
            subWalkthrough = chooseBestWalkthrough(env, subWalkthroughs)
            # now update visitedLeads and foundTags
            updateSubWalkthrough(env, subWalkthrough, visitedLeads, foundTags)
            # now add a text line showing the talkthrough
            text = generateSubWalkthroughAsText(env, subWalkthrough)
            line = text
            walkthroughLines.append(line)

        for line in walkthroughLines:
            results.flatAdd(line)

    # now for fun lets walkthrough the NON-REQUIRED tags by tag
    results.flatAdd("\n")
    latex = " " + generateLatexForDivider(env, "default", None)
    results.flatAdd(vouchForLatexString(latex, True))
    results.flatAdd("\n")
    #
    results.flatAdd("Walkthrough for NON-REQUIRED tags:\n\n")
    walkthroughLines = []
    tagList = tagManager.getTagList()
    for tag in tagList:
        if (tag in foundTags):
            continue
        tagLabel = tag.getNiceIdWithLabelAndObfuscation()
        line = "* Finding non-required tag {}.\n".format(tagLabel)
        walkthroughLines.append(line)
        # generate subwalkthrough to find tag
        subWalkthroughs = findSubWalkthroughsToTag(env, tag, visitedLeads)
        if (len(subWalkthroughs)==0):
            line = "    * Failed to find walkthrough.\n"
            walkthroughLines.append(line)
            continue
        # pick ONE walkthrough (of potentially many)
        subWalkthrough = chooseBestWalkthrough(env, subWalkthroughs)
        # now update visitedLeads and foundTags
        updateSubWalkthrough(env, subWalkthrough, visitedLeads, foundTags)
        # now add a text line showing the talkthrough
        text = generateSubWalkthroughAsText(env, subWalkthrough)
        line = text
        walkthroughLines.append(line)
    #
    for line in walkthroughLines:
        results.flatAdd(line)


    # set contents of report
    reportLead.setBlockList(results)

    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, reportLead, targetSection, renderDoc)




def findSubWalkthroughsToTag(env, tag, visitedLeads):
    # return a list of walkthroughs, one for each place where a tag can be found, and where each walkthrough is a list of items and where each item is a dict {"lead": lead, "gainedTags": [taglist]}
    walkthroughs = []
    tagManager = env.getTagManager()

    # start with gain list
    gainList = tag.getGainList(True)
    for g in gainList:
        if ("lead" not in g):
            continue
        lead = g["lead"]
        subWalkthroughs = findSubWalkthroughsToTagFromGainedLead(env, tag, visitedLeads, lead)
        if (len(subWalkthroughs)>0):
            for w in subWalkthroughs:
                walkthroughs.append(w)
    return walkthroughs



def findSubWalkthroughsToTagFromGainedLead(env, tag, visitedLeads, gainLead):
    walkthroughs = findWalksthroughToLead(env, visitedLeads, gainLead, None, False)
    return walkthroughs


def findWalksthroughToLead(env, visitedLeads, lead, sourceLinkTypeStr, visited):
    # find walkthroughs to a specific lead, by walking backwards, and we can STOP when we hit a visited lead
    optionStopAtVisited = True
    optionRevisitOneVistedLead = True

    walkthroughs = []

    mindMapper = env.getMindManager()
    # needed?
    #mindMapper.buildAndResolveLinksIfNeeded(env)

    # make a copy of visitedLeads that includes lead, so we dont get into a loop
    visitedLeads = list(visitedLeads)
    visitedLeads.append(lead)

    # what tags are generated at this lead
    tagManager = env.getTagManager()
    tagsGainedAtLead = tagManager.getTagsGainedAtLead(lead)

    leadItem = {"lead":lead, "tagsGained": tagsGainedAtLead, "link": sourceLinkTypeStr, "visited": visited}
    
    # generate list of nodes that go to target lead; each of these can generate a potential walktrough
    sourceLeadList = mindMapper.findDeductiveLeadsThatLogicallyImplyOrSuggestTargetLead(env, lead)

    # if there are no sources, then this lead is as far back as we can go
    if (sourceLeadList is not None) and (len(sourceLeadList)>0):
        # walkthrough all sources
        for sourceItem in sourceLeadList:
            sourceLead = sourceItem["lead"]
            sourceLinkTypeStr = sourceItem["link"]
            #
            if (sourceLead in visitedLeads):
                # we dont need any other path other than our own lead since the precursor is already visited (inject this in)
                visited = True

                # we dont need any other path other than our own lead since the precursor is already visited
                if (optionStopAtVisited):
                    if (optionRevisitOneVistedLead):
                        # do we want to force a revisit of this one source?
                        # we are going to skip recursing here so we need to fill in some values
                        sourceItem["visited"] = True
                        sourceItem["tagsGained"] = []
                        #
                        ws = [sourceItem, leadItem]
                    else:
                        ws = [leadItem]
                    walkthroughs.append(ws)
                    continue

            # generate RECURSIVE walkthroughs to a new source node
            walthroughsToSource = findWalksthroughToLead(env, visitedLeads, sourceLead, sourceLinkTypeStr, visited)
            # now extend these the one step further to our target lead, and add to total list of walkthroughs
            for ws in walthroughsToSource:
                ws.append(leadItem)
                walkthroughs.append(ws)

    if (len(walkthroughs)==0):
        # no way to extend any unique source to leadItem, so result is just the single leadItem, exactly as if it were a standalone lead in the walkthrough
        return [[leadItem]]

    # return completed walkthroughts
    return walkthroughs


def chooseBestWalkthrough(env, subWalkthroughs):
    if (len(subWalkthroughs)==0):
        return None
    bestWalkthrough = None
    bestLen = 99999
    for w in subWalkthroughs:
        pathLen = 0
        for s in w:
            visited = s["visited"]
            if (not visited):
                pathLen += 1
        if (pathLen<bestLen):
            bestLen = pathLen
            bestWalkthrough = w
    return bestWalkthrough


def updateSubWalkthrough(env, subWalkthrough, visitedLeads, foundTags):
    for wstep in subWalkthrough:
        lead = wstep["lead"]
        tagsGained = wstep["tagsGained"]
        # add visited leads
        if (lead in visitedLeads):
            # this normally shouldnt happen because we should have stopped here, but we are experimenting with adding previously visited leads to walkthroughghs
            continue
        else:
            visitedLeads.append(lead)
        # add gained tags
        for t in tagsGained:
            if (t not in foundTags):
                foundTags.append(t)


def generateSubWalkthroughAsText(env, subWalkthrough):
    stepTextCombined = ""
    previousLinkTypeStr = ""
    for wstep in subWalkthrough:
        lead = wstep["lead"]
        tagsGained = wstep["tagsGained"]
        linkTypeStr = wstep["link"]
        visited = wstep["visited"]
        #
        leadToc = lead.getReportToc()
        #
        leadTime = lead.getTime()
        if (leadTime is not None) and (leadTime!="") and (leadTime!=-1):
            leadTimeStr = " ({} min)".format(leadTime)
        else:
            leadTimeStr = ""
        #
        if (visited):
            visitStr = "revisit"
        else:
            visitStr = "visit"
        if (previousLinkTypeStr==""):
            visitStr = visitStr.title()
        #
        stepText = "{}{} {}{}".format(previousLinkTypeStr, visitStr, leadToc, leadTimeStr)
        #
        if (linkTypeStr is None):
            previousLinkTypeStr = ""
        else:
            previousLinkTypeStr = linkTypeStr.title() + " "
        #
        if (len(tagsGained)>0):
            tagTexts = []
            for t in tagsGained:
                tagText = t.getNiceIdWithObfuscation()
                tagTexts.append(tagText)
            tagTextJoined = " | ".join(tagTexts)
            stepText += "; gain {}".format(tagTextJoined)
        stepTextCombined += "    * " + stepText + "\n"
    return stepTextCombined

# ---------------------------------------------------------------------------







# ---------------------------------------------------------------------------
def generateAddReportFingerprints(renderDoc, env, targetSection):
    typeFilter = ["fingerPrint","fingerPrintSet"]
    itemLabel = "Fingerprints"

    # create "lead" to hold this report
    from .cbrender import CbRenderLead

    id = "Fingerprint Report"
    label = None
    # create "lead" to hold this report
    reportLead = CbRenderLead(renderDoc, targetSection.getLevel()+1, targetSection, None, id, label, None, None, False)
    #
    # build text contents
    results = JrAstResultList()
    results.flatAdd("The following is a report of all image files used by this case book." + "\n")

    filteredNotes = env.getInterp().getNotesFiltered(None, typeFilter)
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

        doneList = []

        # SORT filtered notes by type and id
        filteredNotes.sort(key = lambda x: sortKeyFuncNotesForFingerprintReport(x))

        # one table for each (we could put them all in one big table with many rows but not sure what the benefit is)
        for note in filteredNotes:
            # make like a row with embedded image and text
            extras = note.getExtras()

            # get components
            imageLatex = "n/a"
            caption = jrfuncs.getDictValueOrDefault(extras,"caption", None)
            imageFullPath = jrfuncs.getDictValueOrDefault(extras, "filePath", None)
            fpLead = jrfuncs.getDictValueOrDefault(extras, "fpLead", "n/a")
            fpFinger = jrfuncs.getDictValueOrDefault(extras, "fpFinger", "n/a")
            typeStr = note.getTypeStr()

            doneId = calcFpDoneId(typeStr, fpLead, fpFinger)
            if (doneId in doneList):
                # already done
                continue
            else:
                doneList.append(doneId)

            #
            if (imageFullPath is None):
                if (caption is not None):
                    imageLatex = caption
            else:
                caption = jrfuncs.getDictValueOrDefault(extras,"caption", None)
                optionWrapText = False
                imageLatex = generateImageEmbedLatex(env, imageFullPath, widthStr, heightStr, borderWidth, padding, "left", "t", caption, None, None, False, optionWrapText)
            #
            if (typeStr == "fingerPrintSet"):
                labelLatex = "[ SET ID {} ]".format(fpLead)
            else:
                labelLatex = "[ ID {} / {} ]".format(fpLead, fpFinger)

            labelLatex += " " + typeStr + ": " + note.getMessageAsLatex()

            if (optionCalcImageSize) and (imageFullPath is not None):
                labelLatex += " (" + generateImageSizeLatex(imageFullPath) + ")"


            # new, we are going to collect ALL fingerprint refs in one place
            leadList = calcAllFpLeadRefs(filteredNotes, doneId)
            leadLinkLatex = ""
            for leadref in leadList:
                if (leadLinkLatex!=""):
                    leadLinkLatex += r" \par "
                if (leadref is not None):
                    leadLinkLatex += makeLatexReferenceToLead(leadref, "report", False)
                else:
                    leadLinkLatex += "[n/a lead]"

            if (True):
                # add info about whether there is a lead for this id
                fpLeadLatex = ""
                leadRef = renderDoc.findLeadByIdPath(fpLead, None)
                if (leadRef is None):
                    fpLeadLatex = r"{\color{red} WARNING: There is no lead for this fingerprint set!}"
                else:
                    leadRefLinkLatex = makeLatexReferenceToLead(leadRef, "report", False)
                    fpLeadLatex = "INFO LEAD: " + leadRefLinkLatex
                leadLinkLatex += r"\par " + fpLeadLatex + r"\par"

            if (True):
                variableList = env.getVariablesWithValue(fpLead)
                if (len(variableList)>0):
                    variableListStr = ", ".join(variableList.keys())
                    leadLinkLatex += r"\par Variables matching fingerprint lead id: " + variableListStr + r"\par"

            # wrap in tabular orientation
            latex = ""
            if (not optionLongTable):
                latex += r"\begin{tblr}{l X}" + "\n"
            

            latex += "{" + imageLatex + "} & {" + labelLatex + r":\par " + leadLinkLatex + "}\n"
            #latex += "{" + imageLatex + "} & {" + labelLatex + "} & {" + leadLinkLatex + "}\n"

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
    reportLead.setBlockList(results)
    #
    # add lead to section
    targetSection.processAndFileLead(renderDoc.getInterp(), env, reportLead, targetSection, renderDoc)



def calcFpDoneId(typeStr, fpLead, fpFinger):
    retv = "{}A_{}_{}".format(typeStr, fpLead, fpFinger)
    return retv

def calcAllFpLeadRefs(notes, matchDoneId):
    leadList = []
    for note in notes:
        extras = note.getExtras()
        fpLead = jrfuncs.getDictValueOrDefault(extras, "fpLead", "n/a")
        fpFinger = jrfuncs.getDictValueOrDefault(extras, "fpFinger", "n/a")
        typeStr = note.getTypeStr()
        doneId = calcFpDoneId(typeStr, fpLead, fpFinger)
        if (doneId == matchDoneId):
            leadRef = note.getLead()
            leadList.append(leadRef)
    return leadList

def sortKeyFuncNotesForFingerprintReport(note):
    extras = note.getExtras()
    # get components
    fpLead = jrfuncs.getDictValueOrDefault(extras, "fpLead", "n/a")
    fpFinger = jrfuncs.getDictValueOrDefault(extras, "fpFinger", "n/a")
    typeStr = note.getTypeStr()
    #
    return calcFpDoneId(typeStr, fpLead, fpFinger)
# ---------------------------------------------------------------------------
