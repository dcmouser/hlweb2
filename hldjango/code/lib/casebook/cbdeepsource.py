# The CbDeepSource class is a support class that allows us to perform MACRO operations like INCLUDE one source file from another (or expand a macro), creating one big uber source text
# that gets passed to the parser as a simble big block of text BUT where we can still recover where each line came from, so that we can report errors with useful info.
# Ie if parser represents an error at text offset 1234 then we want to be able to report that this error is really from file "abc.txt" at offset 100, aka "abc.txt" line 10 position 5.

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint

# python modules
import re

from .jrastutilclasses import JrINote



class CbDeepSource:
    def __init__(self):
        self.chunks = []
        self.sources = []
        self.fileManagerList = []
        self.fullText = ""


    def insertSource(self, newSource, overallStartPos, overallEndPos):
        # a section of our full text is being replaced by a new trackedSource text
        # so we find the block where we are expanding from, split that into 2 chunks, insert the new one as a chunk inside it
        # this call is made to insert a new source into the overall text
        #
        if (overallStartPos==0) and (overallEndPos==0) and (len(self.chunks)==0):
            return self.appendSource(newSource)
        chunkStartPos = 0
        index = -1
        for chunk in self.chunks:
            index += 1
            chunkLen = chunk.getLength()
            chunkEndPos = chunkStartPos + chunkLen
            if (chunkStartPos<=overallStartPos) and (chunkEndPos >= overallStartPos):
                # ok we found the chunk we are inside
                chunkOffsetStart = overallStartPos - chunkStartPos
                chunkOffsetEnd = overallEndPos - chunkStartPos
                # ok now we split the current chunk into two parts
                chunkA = chunk.splitLeft(chunkOffsetStart)
                chunkC = chunk.splitRight(chunkOffsetEnd)
                # and then our new chunk in the middle
                chunkB = CbDeepSourceChunk(newSource)
                # now remove the chunk we are splitting
                del self.chunks[index]
                # and insert the new three
                self.chunks.insert(index, chunkA)
                self.chunks.insert(index+1, chunkB)
                self.chunks.insert(index+2, chunkC)
                # insert ACTUAL text of rouce
                self.insertTextIntoFullText(newSource.getText(), overallStartPos, overallEndPos)
                return chunkB
            else:
                # advance to next chunk
                chunkStartPos += chunkLen
        #
        return None

    def insertSourceIntoSpecificSource(self, newSource, targetSource, relativeStartPos, relativeEndPos):
        # a section of our full text is being replaced by a new trackedSource text
        # so we find the block where we are expanding from, split that into 2 chunks, insert the new one as a chunk inside it
        # this call is made to insert a new source into a specific source by relative address
        # when we insert a source we find the target CHINK, split that into two chunks, and insert one new chunk into it
        #
        overallPos = 0
        index = -1
        for chunk in self.chunks:
            index += 1
            chunkSource = chunk.getSourcep()
            if (chunkSource!=targetSource):
                # this chunk is not our target
                continue
            # offset into this source
            chunkSourceStartPos = chunk.getSourceStartPos()
            chunkLen = chunk.getLength()
            chunkEndPos = chunkSourceStartPos + chunkLen
            if (chunkSourceStartPos <= relativeStartPos) and (chunkEndPos >= relativeEndPos):
                # ok we found the chunk we are inside
                chunkOffsetStart = relativeStartPos - chunkSourceStartPos
                chunkOffsetEnd = relativeEndPos - chunkSourceStartPos
                # convert to our main insert function so we only have one place we do this
                overallStartPos = overallPos + chunkOffsetStart
                overallEndPos = overallPos + chunkOffsetEnd
                return self.insertSource(newSource, targetSource, overallStartPos, overallEndPos)
            else:
                # advance to next chunk
                overallPos += chunkLen
        #
        return None

    def insertTextIntoFullText(self, newText, positionStart, positionEnd):
        self.fullText = self.fullText[0:positionStart] + newText + self.fullText[positionEnd:]

    def appendSource(self, source):
        # just add source to end
        chunk = CbDeepSourceChunk(source)
        self.chunks.append(chunk)
        # add full text
        self.fullText += source.getText()
        # return chunk
        return chunk
 
    def calculateBlame(self, overallStartPos, overallEndPos):
        # return a line for debug display
        return "ATTN: NOT IMPLEMENTED YET"

    def setIncludeFileManagers(self, fileManagerList):
        self.fileManagerList = fileManagerList


    def loadSourceFromFilePathOrText(self, sourceFilePath, sourceFileText, encoding, comment):
        # load text from file into a source
        if (sourceFilePath is not None):
            source = createDeepSourceFromFile(sourceFilePath, encoding, comment)
        else:
            source = createDeepSourceFromText(sourceFileText, encoding, comment)
        # add the source to us
        self.appendSource(source)




    def getFullText(self):
        return self.fullText


    def runMacros(self, env):
        # walk text and run expansions
        regexInclude = re.compile(r"^\$macro\.include\(\"([^\"]*)\"\)", re.MULTILINE)
        #
        maxReplaces = 1000
        replaceCount = 0
        encoding = "utf-8"
        #
        while (True):
            if (replaceCount > maxReplaces):
                raise Exception("Too many (recursive) includes in source; aborting.")
            #
            text = self.getFullText()
            matches = regexInclude.search(text)
            if (matches is None):
                break

            # replace
            fileNameRelative = matches.group(1)

            # note we pass None to say we will add our own use note so we can add more info
            [filePath, warningText] = env.locateManagerFileWithUseNote(env.calcManagerIdListSource(), fileNameRelative, None, None, None, env, None, False)
            # make source from file contents
            comment = "macro included file (name unknown)"
            newSource = createDeepSourceFromFile(filePath, encoding, comment)
            # now INSERT it in
            match1= matches.span()
            matchSpanStartPos = match1[0]
            matchSpanEndPos = match1[1]
            self.insertSource(newSource, matchSpanStartPos, matchSpanEndPos)

            # add note for debug report
            locDict = self.extractHighlightedSourceLineDictAtPos(matchSpanStartPos, matchSpanEndPos)
            locationText = locDict["highlightedSourceTrueLocation"]
            chunkFilePath = locDict["path"]
            chunkLineNumber = locDict["lineNumber"]
            chunkLineOffsetPos = locDict["lineOffsetPos"]
            chunkComment = locDict["comment"]
            msg = 'Including casebook source file: "{}" at location {}'.format(fileNameRelative, locationText)
            msgLatex = 'Including casebook source file: "\\path{' + fileNameRelative + '}" at location ' + '\\path{' + chunkFilePath + '} ' + 'at line \\#{} position {}'.format(chunkLineNumber, chunkLineOffsetPos)
            note = JrINote("embedSource", None, msg, msgLatex, None)
            env.addNote(note)

            # increment
            replaceCount += 1



































# ATTN: we want to replace this to use our new trackedSource class that supports #includes etc

    # ATTN: NEW -- let us format a nice debug message instead of returning a dictionary as below
    def extractHighlightedLineDebugMessageAtPos(self, startPos, endPos):
        locDict = self.extractHighlightedSourceLineDictAtPos(startPos, endPos)
        if (locDict is None):
            return "Internal Error: No source location available."
        #
        highlightedSourceTrueLocation = locDict["highlightedSourceTrueLocation"]
        highlightedSourceLineText = locDict["highlightedSourceLineText"]
        highlightedSourceLinePos = locDict["highlightedSourceLinePos"]
        highlightedSourceLineEndPos = locDict["highlightedSourceLineEndPos"]
        #
        fromStr = "[{}]".format(highlightedSourceTrueLocation)
        msg = ""
        msg += fromStr + ":\n"
        extraIndent = 2
        msg += "  "
        #
        msg += highlightedSourceLineText
        highSpaceStr = " " * (highlightedSourceLinePos + extraIndent)
        highStr = "^" * (highlightedSourceLineEndPos - highlightedSourceLinePos)
        msg += "\n" + highSpaceStr + highStr
        #
        return msg


    def extractHighlightedSourceLineDictAtPos(self, startPos, endPos):
        # part 1 we want to pick out the LINE in our full text where start and end are, so we can highlight the section of the line
        text = self.getFullText()
        retDict = {}
        # start from pos and get the newlines to left and right
        leftPos = text.rfind("\n", 0, startPos)
        rightPos = text.find("\n", startPos)
        if (leftPos==-1):
            leftPost = 0
        if (rightPos==-1):
            rightPos = len(text)
        lineText = text[leftPos+1:rightPos]
        retDict["highlightedSourceLineText"] = lineText
        startHighlightPos = (startPos - leftPos)-1
        endHighlightPos = (endPos - leftPos)-1
        if (startHighlightPos<0):
            startHighlightPos = 0
        if (endHighlightPos>len(lineText)):
            endHighlightPos = startHighlightPos+1
        retDict["highlightedSourceLinePos"] = startHighlightPos
        retDict["highlightedSourceLineEndPos"] = endHighlightPos
        #
        # now it's a little more tricky in the case where this is a deep source that has been included from another, or an expanded macro, etc.
        # so we want to report the original SOURCE FILE and LINE (AND ORIGINAL MACRO LINE IF RELEVANT) 
        highlightedChunkDict = self.findChunkHighlight(startPos)
        chunkFilePath = highlightedChunkDict["path"]
        chunkLineNumber = highlightedChunkDict["lineNumber"]
        chunkLineOffsetPos = highlightedChunkDict["lineOffsetPos"]
        chunkComment = highlightedChunkDict["comment"]
        trueLocation = "{} line={} pos={}".format(chunkFilePath, chunkLineNumber, chunkLineOffsetPos)
        if (chunkComment is not None) and (chunkComment != ""):
            trueLocation += " ({})".format(chunkComment)
        retDict["path"] = highlightedChunkDict["path"]
        retDict["lineNumber"] = highlightedChunkDict["lineNumber"]
        retDict["lineOffsetPos"] = highlightedChunkDict["lineOffsetPos"]
        retDict["comment"] = highlightedChunkDict["comment"]

        retDict["highlightedSourceTrueLocation"] = trueLocation
        #
        return retDict



    def findChunkHighlight(self, startPos):
        # figure out what chunk the position is in
        chunkStartPos = 0
        index = -1
        chunkDict = {}
        for chunk in self.chunks:
            index += 1
            chunkLen = chunk.getLength()
            chunkEndPos = chunkStartPos + chunkLen
            if (chunkStartPos<=startPos) and (chunkEndPos >= startPos):
                # ok we found the chunk we are inside
                chunkOffsetStart = startPos - chunkStartPos
                # ok now lets get the source this chunk refers to
                source = chunk.getSourcep()
                sourceStartPos = chunk.getSourceStartPos()
                chunkDict["path"] = source.getPath()
                chunkDict["comment"] = source.getComment()
                sourcePos = sourceStartPos + chunkOffsetStart
                chunkDict["sourcePos"] = sourcePos
                # now we need LINE number and LINE offset
                [lineNumber, lineOffsetPos] = source.calculateLineNumberAndOffsetOfPos(sourcePos)
                chunkDict["lineNumber"] = lineNumber
                chunkDict["lineOffsetPos"] = lineOffsetPos
                #
                return chunkDict
            else:
                # advance to next chunk
                chunkStartPos += chunkLen

        # not found
        return None

































class CbDeepSourceChunk:
    def __init__(self, sourcep):
        # create a chunk out of the whole source
        self.trackedSource = sourcep
        self.sourceStartPos = 0
        self.chunkLength = sourcep.getLength()
    def getLength(self):
        return self.chunkLength
    def getSourcep(self):
        return self.trackedSource
    def getSourceStartPos(self):
        return self.sourceStartPos

    def splitLeft(self, offset):
        newChunk = CbDeepSourceChunk(self.trackedSource)
        newChunk.sourceStartPos = self.sourceStartPos
        newChunk.chunkLength = offset
        return newChunk
    def splitRight(self, offset):
        newChunk = CbDeepSourceChunk(self.trackedSource)
        newChunk.sourceStartPos = self.sourceStartPos + offset
        newChunk.chunkLength = self.chunkLength - offset
        return newChunk



class CbDeepSourceSource:
    def __init__(self, text):
        self.path = None
        self.comment = None
        self.text = text
        self.sourceLength = len(text)
    def getLength(self):
        return self.sourceLength
    def getText(self):
        return self.text
    def getPath(self):
        return self.path
    def getComment(self):
        return self.comment


    def setInfo(self, sourceFilePath, comment):
        self.path = sourceFilePath
        self.comment = comment

    def calculateLineNumberAndOffsetOfPos(self, sourcePos):
        # given a position, calculate the line number and offset into line
        text = self.text
        #
        leftPos = text.rfind("\n", 0, sourcePos)
        if (leftPos==-1):
            leftPost = 0
        # offset into line
        lineOffsetPos = sourcePos-leftPos
        # count linebreaks before our position
        lineBreaksBefore = text.count("\n", 0, leftPos) + 1 + 1
        return [lineBreaksBefore, lineOffsetPos]








def createDeepSourceFromFile(sourceFilePath, encoding, comment=None):
    # load text
    text = jrfuncs.loadTxtFromFile(sourceFilePath, True, encoding=encoding)
    # create deep source
    source = CbDeepSourceSource(text)
    # set info
    source.setInfo(sourceFilePath, comment)
    #
    return source


def createDeepSourceFromText(sourceFileText, encoding, comment=None):
    # create deep source
    source = CbDeepSourceSource(sourceFileText)
    # set info
    source.setInfo("casebook source code", comment)
    return source
