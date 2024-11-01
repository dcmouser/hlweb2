# default values that are often used in multiple places:
#  cbfuncs_core1.py (when invoking configuration functions)
#  jrastcbr.py (where data structure defaults are set)
#  cbtasks.py (where we have defaults for tasks overriding these)





# defines
DefCbVersionString = "v2.2 (10/22/24)"
DefCbBuildString = "Casebook " + DefCbVersionString
DefCbAuthorString = "Jesse Reichler <jessereichler@gmail.com>"

# image manager names
DefFileManagerNameImagesCase = "images_case"
DefFileManagerNameImagesShared = "images_shared"
DefFileManagerNamePdfsCase = "pdfs_case"
DefFileManagerNamePdfsShared = "pdfs_shared"
DefFileManagerNameSourceCase = "source_case"
DefFileManagerNameSourceShared = "source_shared"



# rendererData options
DefCbRenderDefault_latexFontSize = 10
DefCbRenderDefault_doubleSided = True
DefCbRenderDefault_latexPaperSize = "letter"
DefCbRenderDefault_latexPaperSizesAllowed = ["letter","A4","B6","A5"]
DefCbRenderDefault_latexPaperSize = 10
DefCbRenderDefault_autoStyleQuotes = False
#
DefCbRenderDefault_latexExtraRuns = 1
DefCbRenderDefault_latexQuietMode = True
DefCbRenderDefault_latexRunViaExePath = False
#
DefCbRenderDefault_outputSuffix = "_test"
DefCbRenderDefault_outputSubdir = "test"
DefCbRenderDefault_renderVariant = "report"
#
DefCbRenderDefault_DropCapLineSize = 4

#
DefCbTaskDefault_saveLeadJsons = True
DefCbTaskDefault_generateMindMap = True
DefCbTaskDefault_saveHtmlSource = True


# documentData options
DefCbDocumentDefault_defaultLocation = "back"
DefCbDocumentDefault_printLocation = "inline"
DefCbDocumentDefault_printStyle = "simple"


# game
DefCbGameDefault_clockMode = True



# fixed values
# not used currently but available for testing
# we do NOT let the user change this because doing so would be a security risk
DefCbDefine_latexExeFullPath = "C:/Users/jesse/AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe"


DefCbDefine_KludgeSharedMediaDirectory = r"E:\MyDocs\Programming\Python\lark\shared"