# my libs
from lib.jr.jrfuncs import jrprint
from lib.jr import jrfuncs

# python
import re
import html


def createHtmlFromCbSourceFile(hlapi, hlapiPrev, sourceFilePath, sourceFileText, outFilePath, flagDebug):
    # the generation of html from source is extremely useful for one reason, it can be copied and pasted into a google doc to preserve some useful formatting
    # the idea is to preserve only the source text from the casebook source file, and introduce no other text, but to add some formatting that will be preserved in the google doc

    encoding = "utf-8"

    regexHeader = re.compile(r"^(#*) (.*)$")
    regexLeadHeader = re.compile(r"^##\s([^\s]+)(\s.*)?$")
    regexHlApiLine = re.compile(r"^\/\/ [^\s\:]*:\s(.+)")
    regexCommentLine = re.compile(r"^[\s]*\/\/")

    regexCommentLineSection = re.compile(r"^[\s]*\/\/ SECTION\:\s*(.*)$")

    fileOut = open(outFilePath, "w", encoding=encoding)
    if (flagDebug):
        jrprint("Creating '{}' from '{}'.".format(outFilePath, sourceFilePath))

    fileOut.write("""
<head>
  <meta charset="UTF-8">
</head>
""")

    fileOut.write("""<!--
This html file should be opened in a web browser where you can select all text (Ctrl+A) and then PASTE it into a google docs document.  This should result in a google doc which has some minor markup of section headers while still preserving the plain-text nature of the document, allowing you to edit the document and then copy and paste the google doc back into the casebook builder tool.
-->
""")

    fileOut.write("""
    <style>
	h1 { font-size: 14pt; page-break-before: always;}
	h2 { font-size: 12pt; }
	body { font-size: 10pt; }
</style>
                  
""")

    if (sourceFilePath is not None):
        text = jrfuncs.loadTxtFromFile(sourceFilePath, True, encoding)
    else:
        text = sourceFileText
    #
    if (True):
        lines = text.split("\n")
        lineCount = len(lines)
        for index, line in enumerate(lines):
            if (index==lineCount-1):
                isLastLine = True
            else:
                isLastLine = False
            #
            line = escapeTextForHtml(line)

            matches = regexHeader.match(line)
            if (matches is not None):
                poundText = matches.group(1)
                hText = "h" + str(len(poundText))
                lineOut = "<" + hText + ">" + line + "</" + hText + ">\n"
                if (False):
                    numBrs = 3 - len(poundText)
                    if (numBrs>0):
                        lineOut = ("<br/>\n" * numBrs) + lineOut
                # now we are going to check if its potentially a LEAD HEADER with a # that we can look up in hlapi, BUT ONLY if there is not already a comment with this info
                matches = regexLeadHeader.match(line)
                if (matches is not None):
                    infoLinePrefix = "// "
                    if (isLastLine) or (regexHlApiLine.match(lines[index+1]) is None):
                        leadId = matches.group(1)
                        leadId = jrfuncs.removeQuotesAround(leadId)
                        # see if hlapi can find it
                        [leadRow, sourceKey] = hlapi.findLeadRowByLeadId(leadId)
                        if (leadRow is not None):
                            dataVersion = hlapi.getVersion()
                        if (leadRow is None) and (hlapiPrev is not None):
                            [leadRow, sourceKey] = hlapiPrev.findLeadRowByLeadId(leadId)
                            if (leadRow is not None):
                                dataVersion = hlapiPrev.getVersion()
                        if (leadRow is not None):
                            # found it
                            fullLabel = hlapi.getNiceFullLabelWithAddress(leadRow)
                            leadInfoLine = "<i>" + infoLinePrefix + dataVersion + ": " + fullLabel + "</i><br/>\n"
                            lineOut += leadInfoLine
            else:
                #  COMMENT LINES as italics, and with some other special comment cases
                if (regexCommentLine.match(line) is not None):
                    # its a comment line
                    lineOut = ""
                    if (regexCommentLineSection.match(line)):
                        # its a SECTION comment which is like a subsection within a categore that the user dellineates with pagebreaks, etc.,
                        # page break before the comment
                        lineOut += '<div style="page-break-after: always;">\n'
                        # make the comment a section
                        lineOut += "<h2><i>" + line + "</i></h2>"
                    else:
                        # italics the comment lines
                        lineOut += "<i>" + line + "</i>"
                    #
                else:
                    lineOut = line
                #
                if (not isLastLine):
                    lineOut = lineOut + "<br/>\n"

            # write line
            fileOut.write(lineOut)
    
    fileOut.close()

    # success
    return True



def escapeTextForHtml(textLine):
    textLine = html.escape(textLine)
    textLine = re.sub(r"  +", convertSpaces, textLine)
    textLine = re.sub(r"^ ", "&nbsp;", textLine)
    textLine = re.sub(r" $", "&nbsp;", textLine)
    return textLine

def convertSpaces(matchObj):
    grp = matchObj.group(0)
    repStr = "&nbsp;" * len(grp)
    return repStr








def fastKludgeParseGameInfoFromFile(sourceFilePath, encoding, errorList):
    text = jrfuncs.loadTxtFromFile(sourceFilePath, True, encoding)
    return fastKludgeParseGameSettingsFromText(text, errorList)


def fastKludgeParseGameSettingsFromText(text, errorList):
    settings = {}
    settings["info"] = fastKludgeParseConfigureArgsFromText("configureGameInfo", text, ["name", "title", "subtitle", "authors", "version", "versionDate", "status", "difficulty", "duration"], errorList)
    settings["summary"] = fastKludgeParseConfigureArgsFromText("configureGameSummary", text, ["summary"], errorList)
    settings["infoExtra"] = fastKludgeParseConfigureArgsFromText("configureGameInfoExtra", text, ["cautions", "url", "copyright", "extraCredits", "keywords", "gameSystem", "gameDate"], errorList)
    settings["campaign"] = fastKludgeParseConfigureArgsFromText("configureCampaign", text, ["campaignName", "campaignPosition"], errorList)

    return settings


def fastKludgeParseConfigureArgsFromText(funcName, text, paramList, errorList):
    # fast kludgey attempt to get source file game settings dictionary using regex and pattern matching rather than intepretting the full file

    # get the text using regex
    searchString = r"[\r\n]+\$" + funcName + r"\((.*?)\)[\r\n]+"
    matches = re.search(searchString, text, flags=re.DOTALL)
    if (matches is None):
        return None
    configureLine = matches.group(1)
    # newlines 
    remainderText = configureLine.replace("\n", " ")
    # now split into [key=val,] pairs, with val possibly in double, single, or unicode quotes
    assignmentDict = {}
    paramIndex = 0
    errorMsg = None
    while(True):
        paramNameImplicit = paramList[paramIndex] if (paramIndex<len(paramList)) else None
        #
        [key, val, remainderText] = fastKludgeParseGameInfoFromTextSplitLeftAssignment(funcName, remainderText, paramIndex, paramNameImplicit, errorList)
        if (key is not None):
            assignmentDict[key] = val
            paramIndex += 1
        if (remainderText is None) or (remainderText==""):
            break
        configureLine = remainderText
    return assignmentDict


def fastKludgeParseGameInfoFromTextSplitLeftAssignment(funcName, text, paramIndex, paramNameImplicit, errorList):
    text = text.strip()
    if (len(text)==0):
        return [None, None, None]
    c = text[0]
    if (c==","):
        return [None, None, text[1:]]
    if (paramNameImplicit is None):
        paramErrorLabel = "unnamed parameter at index {}".format(paramIndex+1)
    else:
        paramErrorLabel = "implicit parameter '{}' at index {}".format(paramNameImplicit, paramIndex+1)
    #
    [firstPart, isAssignment, remainderText, errorText, errorPosition] = fastKludgeParseGameInfoFromTextSplitLeftValue(text)
    if (errorText is not None):
        errorList.append("While parsing settings function {}(...) encountered error in {} at position {}: {}.".format(funcName, paramErrorLabel, errorPosition+1, errorText))
        return [None, None, None]
    elif (isAssignment):
        # we have a keyword
        key = firstPart
        # get value for assignment
        [val, isAssignment, remainderText, errorText, errorPosition] = fastKludgeParseGameInfoFromTextSplitLeftValue(remainderText)
        if (errorText is not None):
            errorList.append("While parsing settings function {}(...), the assignment of argument '{}' (index {}) was not understood at position {}: {}.".format(funcName, key, paramIndex+1, errorPosition+1, errorText))
            return [None, None, None]
        if (isAssignment):
            errorList.append("While parsing settings function {}(...), unexpectedly found assignment twice in parsing argument name '{}' at index {}".format(funcName, key, paramIndex+1))
    else:
        # just a value
        if (paramNameImplicit is None):
            # error
            errorList.append("While parsing settings function {}(...) got unexpected parameter at index {}; something was passed without an argument assignment, but there is no implicit argument for this function at this index.  Make sure you check for matching double quotes, etc.".format(funcName, paramIndex+1))
            return [None, None, None]
        key = paramNameImplicit
        val = firstPart
    return [key, val, remainderText]


def fastKludgeParseGameInfoFromTextSplitLeftValue(text):
    # grab leftmost value and return it with remainder
    text = text.strip()
    textLen = len(text)
    if (textLen==0):
        return [None, ""]
    # first character tells us what kind of quote
    firstC = text[0]
    quoteDouble = "\""
    quoteSingle = "'"
    quoteLeft = "“"
    quoteRight = "”"
    if (firstC in [quoteDouble, quoteSingle, quoteLeft, quoteRight]):
        quoted = True
    else:
        quoted = False
    inQuote = quoted
    if (not quoted):
        word = firstC
    else:
        word = ""
    #
    isAssignment = False
    isError = False
    errorPosition = 0
    errorText = None

    #
    i = 0
    if (i==textLen-1):
        # end of line, so jump past end so we reset remainderText
        i += 1
    while (i<textLen-1):
        i += 1
        c = text[i]
        if (inQuote):
            if (c=="\\"):
                # escape
                if (textLen==i-1):
                    # error
                    return [None, None]
                word += text[i+1]
                continue
            if (firstC == quoteDouble) and (c == quoteDouble):
                # end quote
                i += 1
                inQuote = False
                break
            if (firstC == quoteSingle) and (c == quoteSingle):
                # end quote
                i += 1
                inQuote = False
                break
            if (firstC == quoteLeft) and (c == quoteRight):
                # end quote
                i += 1
                inQuote = False
                break
            #
            word += c
        else:
            if (c in ["="]):
                isAssignment = True
                break
            if (c in [","," ",")"]):
                break
            if (c in [quoteDouble, quoteSingle, quoteLeft, quoteRight]):
                # we got another quote but we did not expect it; error
                isError = True
                errorPosition = i
                errorText = "Encountered an unexpected quote character ({}) while parsing argument.".format(c)
                break
            word += c
    if (i<textLen):
        while (text[i] in [","," ","="]):
            i += 1
        remainder = text[i:].strip()
    else:
        remainder = ""
    #
    word = word.strip()

    if (inQuote):
        # ended parse STILL in quote(!); this is an error
        quoteError = True
        errorPosition = i-1
        errorText = "Attempting to parse argument but quote ({}) was not closed properly.".format(firstC)

    return [word, isAssignment, remainder, errorText, errorPosition]