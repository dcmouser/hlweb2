# lark
import lark

# jrast
from .jriexception import *










# for tracking source location of tokens
class JrSourceLocation:
    def __init__(self, sloc=None):
        #
        self.copyFrom(sloc)

    def clearLocation(self):
        self.start_pos = -1
        self.end_pos = -1
        self.line = -1
        self.column = -1
        self.end_line = -1
        self.end_column = -1

    def copyFrom(self, fromObj):
        if (fromObj is None):
            # blank
            self.clearLocation()
            return
        
        if (isinstance(fromObj, lark.Tree)):
            # lark tree has token as data
            sloc = fromObj.meta

        if (not hasattr(fromObj,"start_pos") and (hasattr(fromObj,"meta"))):
            fromObj = fromObj.meta

        if (hasattr(fromObj,"start_pos")):
            # already a JrSourceLocation; copy from it?
            # or its a lark token type see https://lark-parser.readthedocs.io/en/latest/classes.html#token
            self.line = fromObj.line
            self.start_pos = fromObj.start_pos
            self.end_pos = fromObj.end_pos
            self.column = fromObj.column
            self.end_line = fromObj.end_line
            self.end_column = fromObj.end_column
            return
        if (hasattr(fromObj,"getSourceLine")):
            # already a JrSourceLocation; copy from it?
            # or its a lark token type see https://lark-parser.readthedocs.io/en/latest/classes.html#token
            self.line = fromObj.getSourceLine()
            self.start_pos = fromObj.getSourceStartPos()
            self.end_pos = fromObj.getSourceEndPos()
            self.column = fromObj.getSourceColumn()
            self.end_line = fromObj.getSourceEndLine()
            self.end_column = fromObj.getSourceEndColumn()
            return

        
        if (isinstance(fromObj, lark.Token) or isinstance(fromObj, lark.tree.Meta)):
            # no line number attribues for this particular token it seems
            self.clearLocation()
            return

        # error and we don't know how to report where the problem is
        msg = "Internal interpretter error; sloc info was not understood ({}).".format(fromObj)
        raise makeJriException(msg, None)

    def debugString(self):
        str = "line {}:{}".format(self.line, self.column)
        return str

    
    def getSourceLine(self):
        return self.line
    def getSourceStartPos(self):
        return self.start_pos
    def getSourceEndPos(self):
        return self.end_pos
    def getSourceColumn(self):
        return self.column
    def getSourceEndLine(self):
        return self.end_line
    def getSourceEndColumn(self):
        return self.end_column









# Helper class for reporting quote imbalance problems
# Idea is to try to detect problems with double quotes or unicode quotes and try to give the author location information to find them
class QuoteBalance:
    def __init__(self):
        self.textLines = []
        self.inDoubleQuote = False
        self.unicodeQuoteDepth = 0
        self.doubleQuoteList = []
        self.unicodeQuoteList = []
        self.unicodeLeftQuoteList = []
        self.unicodeRightQuoteList = []
        self.errorList = None
        self.startingUnicodeQuoteDepth = None


    def getProblemList(self):
        msgList = []
        if (self.inDoubleQuote):
            msgList.append( {"msg": "Unbalanced/improper double quotes", "locs": self.doubleQuoteList} )
            # now warnings about lines that have an unueven number of double quotes on them, which may not be an error, but good likelihood
            self.buildOddLineWarnings("doublequotes", msgList, self.doubleQuoteList)
        if (self.unicodeQuoteDepth!=0):
            msgList.append( {"msg": "Unbalanced/improper unicode left-vs-right quotes", "locs": self.unicodeQuoteList} )
            self.buildOddLineWarnings("unicode quotes", msgList, self.unicodeQuoteList)
        if (self.errorList is not None):
            for err in self.errorList:
                msgList.append(err)
        return msgList



    def buildOddLineWarnings(self, typeStr, msgList, quoteList):
        ldict = {}
        for q in quoteList:
            source = q["source"]
            line = q["line"]
            linePos = q["linepos"]
            if (source not in ldict):
                ldict[source] = {}
            if (line not in ldict[source]):
                ldict[source][line] = 1
            else:
                ldict[source][line] += 1
        #
        for source, sourceDict in ldict.items():
            for line, quoteCount in sourceDict.items():
                if (quoteCount%2 == 1):
                    # odd quote count on line
                    lineText = self.textLines[line]
                    msgList.append( {"msg": "Odd number ({}) of {} in source '{}' on line {}: {}".format(quoteCount, typeStr, source, line, lineText)})
            



    def addError(self, text, msg, sourceName, realLineCount, realLinePos, offsetLineCount, offsetLinePos):
        if (self.errorList is None):
            self.errorList = []
        locString = "In [{}] at line {} pos {}".format(sourceName, realLineCount, realLinePos)
        # show them where
        lines = text.split("\n")
        eline = lines[offsetLineCount]
        highlightDist = 20
        startp = offsetLinePos - highlightDist
        endp = offsetLinePos + highlightDist
        if (startp<0):
            startp = 0
        if (endp>len(eline)):
            endp = len(eline)
        errorLine = eline[startp:endp]
        epos = offsetLinePos-startp

        errDict = {"msg": msg, "locString": locString, "errorLine": errorLine, "epos": epos}
        self.errorList.append(errDict)


    def scanAndAdjustCounts(self, text, sourceName, sourceOffsetLine, sourceOffsetLinePos):
        # adjust counters based on text
        self.textLines = text.split("\n")
        offset = -1
        offsetLinePos = -1
        offsetLineCount = 0
        for c in text:
            offset += 1
            offsetLinePos += 1
            if (c=='\n'):
                offsetLineCount += 1
                offsetLinePos = 0
            #
            realLineCount = sourceOffsetLine + offsetLineCount
            realLinePos = sourceOffsetLinePos + offsetLinePos
            #
            if (c=='"'):
                # for double quotes
                self.inDoubleQuote = (not self.inDoubleQuote)
                cpos = {"source": sourceName, "line": realLineCount, "linepos": realLinePos}
                self.doubleQuoteList.append(cpos)
                if (self.inDoubleQuote):
                    self.startingUnicodeQuoteDepth = self.unicodeQuoteDepth
                else:
                    if (self.startingUnicodeQuoteDepth != self.unicodeQuoteDepth):
                        self.addError(text, "Double quote string contains imbalanced unicode quotes", sourceName, realLineCount, realLinePos, offsetLineCount, offsetLinePos)
            #
            if (c=='“'):
                # for unicode quotes, most of what we do is keep track of balance, and occurences
                self.unicodeQuoteDepth += 1
                cpos = {"source": sourceName, "line": realLineCount, "linepos": realLinePos}
                self.unicodeLeftQuoteList.append(cpos)
                self.unicodeQuoteList.append(cpos)
                if (self.unicodeQuoteDepth>1):
                    self.addError(text, "Nested unicode left quote", sourceName, realLineCount, realLinePos, offsetLineCount, offsetLinePos)
            #
            if (c=='”'):
                # for unicode quotes, most of what we do is keep track of balance, and occurences
                self.unicodeQuoteDepth -= 1
                cpos = {"source": sourceName, "line": realLineCount, "linepos": realLinePos}
                self.unicodeRightQuoteList.append(cpos)
                self.unicodeQuoteList.append(cpos)
                if (self.unicodeQuoteDepth<0):
                    self.addError(text, "Unbalanced extra unicode right quote", sourceName, realLineCount, realLinePos, offsetLineCount, offsetLinePos)
                if (self.unicodeQuoteDepth==0):
                    if (self.inDoubleQuote):
                        self.addError(text, "Unicode quote string contains imbalanced double quotes", sourceName, realLineCount, realLinePos, offsetLineCount, offsetLinePos)






class JrINote:
    # for keeping track of WARNINGS and miscelaneous occurences that might be included in a report
    def __init__(self, typeStr, lead, msg, msgLatex, extras):
        self.typeStr = typeStr
        self.lead = lead
        self.msg = msg
        self.msgLatex = msgLatex
        self.extras = extras
    def getMessage(self):
        return self.msg
    def getMessageAsLatex(self):
        return self.msgLatex
    def getLead(self):
        return self.lead
    def getExtras(self):
        return self.extras
    def getTypeStr(self):
        return self.typeStr


