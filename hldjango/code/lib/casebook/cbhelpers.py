# my libs
from lib.jr.jrfuncs import jrprint
from lib.jr import jrfuncs

# python
import re
import html


def createHtmlFromCbSourceFile(sourceFilePath, sourceFileText, outFilePath, flagDebug):
    encoding = "utf-8"

    regexHeader = re.compile(r"^(#*) (.*)$")

    fileOut = open(outFilePath, "w", encoding=encoding)
    if (flagDebug):
        jrprint("Creating '{}' from '{}'.".format(outFilePath, sourceFilePath))

    fileOut.write("""<!--
This html file should be opened in a web browser where you can select all text (Ctrl+A) and then PASTE it into a google docs document.  This should result in a google doc which has some minor markup of section headers while still preserving the plain-text nature of the document, allowing you to edit the document and then copy and paste the google doc back into the casebook builder tool.
-->
""")

    fileOut.write("""<style>
	h1 { font-size: 14pt; }
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
            else:
                if (not isLastLine):
                    lineOut = line + "<br/>\n"
                else:
                    lineOut = line

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
    settings["info"] = fastKludgeParseConfigureArgsFromText("configureGameInfo", text, ["name", "title", "subtitle", "authors", "version", "versionDate", "difficulty", "duration"], errorList)
    settings["summary"] = fastKludgeParseConfigureArgsFromText("configureGameSummary", text, ["summary"], errorList)
    settings["infoExtra"] = fastKludgeParseConfigureArgsFromText("configureGameInfoExtra", text, ["cautions", "url", "extraCredits", "keywords"], errorList)

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
        [key, val, remainderText] = fastKludgeParseGameInfoFromTextSplitLeftAssignment(remainderText, paramIndex, paramNameImplicit, errorList)
        if (key is not None):
            assignmentDict[key] = val
            paramIndex += 1
        if (remainderText is None) or (remainderText==""):
            break
        configureLine = remainderText
    return assignmentDict


def fastKludgeParseGameInfoFromTextSplitLeftAssignment(text, paramIndex, paramNameImplicit, errorList):
    text = text.strip()
    if (len(text)==0):
        return [None, None, None]
    c = text[0]
    if (c==","):
        return [None, None, text[1:]]
    [firstPart, isAssignment, remainderText] = fastKludgeParseGameInfoFromTextSplitLeftValue(text)
    if (isAssignment):
        # we have a keyword
        key = firstPart
        # get value for assignment
        [val, isAssignment, remainderText] = fastKludgeParseGameInfoFromTextSplitLeftValue(remainderText)
        if (isAssignment):
            errorList.append("Unexpectedly found assignment twice in parsing parameter name '{}' index {}".format(key, paramIndex))
    else:
        # just a value
        if (paramNameImplicit is None):
            # error
            errorList.append("Parameter name for index {} not found and not implicit".format(paramIndex))
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
    if (not quoted):
        word = firstC
    else:
        word = ""
    isAssignment = False
    i = 0
    if (i==textLen-1):
        # end of line, so jump past end so we reset remainderText
        i += 1
    while (i<textLen-1):
        i += 1
        c = text[i]
        if (quoted):
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
                break
            if (firstC == quoteSingle) and (c == quoteSingle):
                # end quote
                i += 1
                break
            if (firstC == quoteLeft) and (c == quoteRight):
                # end quote
                i += 1
                break
            word += c
        else:
            if (c in ["="]):
                isAssignment = True
                break
            if (c in [","," ",")"]):
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
    return [word, isAssignment, remainder]