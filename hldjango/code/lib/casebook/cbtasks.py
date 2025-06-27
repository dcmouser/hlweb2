# casebook stuff
from .cblrender import CblRenderDoc

# ast modules
from .cbtask import CbTask, DefRmodeRun, DefRmodeRender
from .casebookDefines import *

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint

# python modules
import logging
import json


# task helpers

class CbTaskLatex(CbTask):
    def __init__(self, interp, taskOptionsIn):
        super().__init__(interp, "latex", taskOptionsIn, DefRmodeRender)

        # set task render mode
        self.setRenderFormat("latex")

        # render options defaults
        taskOptionDefaults = {
            # note that SOME Of these options are Renderer options passed to the renderer object, which has its own defaults
		    "latexRunViaExePath": DefCbRenderDefault_latexRunViaExePath,
		    "latexExtraRuns": DefCbRenderDefault_latexExtraRuns,
            "latexQuietMode": DefCbRenderDefault_latexQuietMode,
            "latexCompiler": DefCbRenderDefault_latexCompiler,
            # 
            "outputSuffix": DefCbRenderDefault_outputSuffix,
            "outputSubdir": DefCbRenderDefault_outputSubdir,
            "renderVariant": DefCbRenderDefault_renderVariant,
            #
            "taskSaveLeadJsons": DefCbTaskDefault_saveLeadJsons,
            "taskGenerateMindMap": DefCbTaskDefault_generateMindMap,
            "taskSaveHtmlSource": DefCbTaskDefault_saveHtmlSource,
	    }
        # merge in options on top of defaults
        jrfuncs.deepMergeMissingKeysFromBIntoA(self.taskOptions, taskOptionDefaults)

        # create renderer (set options now)
        renderDoc = CblRenderDoc(self.getInterp())
        renderDoc.taskSetOptions(self.taskOptions)
        self.setRenderer(renderDoc)


    def renderToPdf(self, suffixedOutputPath, suffixedBaseFileName, flagDebug, renderSectionName):

        logger = logging.getLogger("app")
        msg = "Running renderToPdf {}/{}".format(suffixedOutputPath, suffixedBaseFileName)
        logger.debug(msg)

        # now run the renderer
        renderDoc = self.getRenderer()
        # set options AGAIN; this will OVERWRITE any options set by casebook code that got executed during interpret build stage before rendering, and allow the task to overwrite those values
        renderDoc.taskSetOptions(self.taskOptions)

        # do the render
        [retv, fileList] = renderDoc.renderToPdf(suffixedOutputPath, suffixedBaseFileName, flagDebug, renderSectionName)
        for filePath in fileList:
            self.getInterp().addGeneratedFile(filePath)

        return [retv, fileList]


    def getTaskOptions(self):
        return self.taskOptions










class CbTaskFastParseGameInfo(CbTask):
    def __init__(self, interp, taskOptionsIn):
        super().__init__(interp, "", taskOptionsIn, DefRmodeRender)

        # nothing to do
    
    def debugPrint(self):
        env = self.getEnvironment()
        info = env.getEnvValueUnwrapped(None, "info", None)
        jrprint("Parsed game info:")
        jrprint(info)



class CbTaskZipFiles(CbTask):
    def __init__(self, interp, taskOptionsIn):
        super().__init__(interp, "", taskOptionsIn, DefRmodeRender)
        # nothing to do

