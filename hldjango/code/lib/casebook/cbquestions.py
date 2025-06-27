from .cbfuncs_core_support import buildFormElementTextLatex, generateFormTextLatex, addResultsToResults
from .jrastfuncs import getUnsafeDictValueAsString, makeLatexLinkToRid, vouchForLatexString



class CbQuestionManager:
    def __init__(self):
        self.questions = {}
        return

    def defineQuestion(self, id, summary, points, typeStr, lines, sizeStr, choices, questionContent):
        if (id in self.questions):
            raise Exception("Attempt to redefine question with id '{}'.".format(id))
        #
        question = CbQuestion(id, summary, points, typeStr, lines, sizeStr, choices, questionContent)
        self.questions[id] = question
        return question

    def findQuestionById(self, id):
        return self.questions[id]

    def calcTotalPoints(self):
        totalPoints = 0
        for q,v in self.questions.items():
            totalPoints += v.getPoints()
        return totalPoints





class CbQuestion:
    def __init__(self, id, summary, points, typeStr, lines, sizeVal, choices, questionContent):
        self.id = id
        self.summary = summary
        self.points = points
        self.typeStr = typeStr
        self.lines = lines
        self.sizeVal = sizeVal
        self.choices = choices
        self.questionContent = questionContent

    def getId(self):
        return self.id
    def getSummary(self):
        return self.summary
    def getPoints(self):
        return self.points
    def getType(self):
        return self.type
    def getLines(self):
        return self.lines
    def getSizeVal(self):
        return self.sizeVal
    def getQuestionContent(self):
        return self.questionContent




    def addToResultsAsQuestion(self, env, results):
        # this fucntions presents question text content asking it as a question, with form fields, etc

        # main line of question
        self.AddToResultsMainLine(env, results, None, False)

        # newline
        results.flatAddBlankLine()

        # question text
        questionContent = self.getQuestionContent()
        if (questionContent is not None):
            addResultsToResults(results, questionContent, True)

        # form part
        if (False):
            # old form types
            [text, latex] = buildFormElementTextLatex(self.typeStr, self.lines, self.sizeVal, self.choices)
        else:
            # new form multiple lines (if lines not specified thent he content of the question will inlcude the form)
            pt = 0.5
            lines = self.getLines()
            if (lines is not None) and (lines>0):
                latex = generateFormTextLatex(lines, self.getSizeVal(), pt)
                result = vouchForLatexString(latex, False)
                results.flatAdd(result)




    def addToResultsAsAnswer(self, env, results, summary):
        # this fucntions presents question text summary before the author presents the answer, repeating the score info, etc.

        # main line of question
        self.AddToResultsMainLine(env, results, summary, True)




    def AddToResultsMainLine(self, env, results, summary, flagAddScoreLineAfter):
        # build line line ID. TEXT
        text = "**{}**. ".format(self.getId())

        # add summary
        if (summary is None):
            summary = self.getSummary()
        #
        if (summary is not None):
            text += summary

        # points
        points = self.getPoints()
        if (points!=0):
            if (points>1):
                points = "max. " + str(points)
            #
            text += " (**{} points**)".format(points)
        #
        renderer = env.getRenderer()
        latexPartA = renderer.convertMarkdownToLatexDontVouch(text, False, False)

        if (flagAddScoreLineAfter):
            # line for user to put total
            safeWidthStr = "0.5in"
            pt = 1
            latex = "\\cbFormLine{" + safeWidthStr + "}" + "{" + str(pt) + "pt}"
            latexPartB = latex
        else:
            latexPartB = None

        #
        if (latexPartB is not None):
            # use a function to right align form part
            latex = r"\jrledline{" + latexPartA + "}{" + latexPartB + "}\n"
        else:
            latex = latexPartA + "\n"

        # add it
        results.flatAdd(vouchForLatexString(latex, False))


    def AddToResultsMainLineOLD(self, env, results, flagAddScoreLineAfter):
        # build line line ID. TEXT
        results.flatAdd("**{}**. ".format(self.getId()))
        if (self.getSummary() is not None):
            results.flatAdd(self.getSummary())

        # points
        points = self.getPoints()
        if (points>1):
            points = "max " + str(points)
        #
        pointsText = "(**{} points**)".format(points)
        #
        results.flatAdd(" " + pointsText)

        if (flagAddScoreLineAfter):
            results.flatAdd(": ")
            # line for user to put total
            safeWidthStr = "0.5in"
            pt = 1
            latex = "\\cbFormLine{" + safeWidthStr + "}" + "{" + str(pt) + "pt}"
            results.flatAdd(vouchForLatexString(latex, True))

        # newline
        results.flatAddBlankLine()
