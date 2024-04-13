# The main class that handles parsing of storybooks, and interfaces with pdf generator

# python modules
import re
import json
import os

# user modules
from lib.jr.jrfuncs import jrprint
from lib.jr import jrfuncs
from lib.hl import hlparser

from lib.hl.hltasks import queueTaskBuildStoryPdf



class HlStory:
    def __init__(self):
        self.text = None
        self.settings = {}
        self.buildOptions = {}

    def setText(self, text):
        self.text = text
    def setBuildOptions(self, buildOptions):
        self.buildOptions = buildOptions


    def extractSettingsDictionary(self, inText=None):
        # we might normally extract settings during parsing, but we want to have a quick way to do it.
        # ATTN: TODO: Note that this code uses a regex to extract the settings, compared to how the settings might be extracted during full processing, which may be able to ignore comment lines, etc
        # so it is possible that this version may error out in ways that the full function won't

        if (inText is not None):
            self.setText(inText)
        #
        settings = {}
        # extract json settings
        #regexSettings = re.compile(r'#\s*options\s*\n(\{[\S\s]*?\})(\n+#)', re.MULTILINE | re.IGNORECASE)
        #regexSettings = re.compile(r'#\s*options\s*\n(\{[\S\s]*?\})(\n+#)', re.MULTILINE)
        text = self.text
        # evilness
        text = jrfuncs.fixupUtfQuotesEtc(text)
        #
        regexSettings = re.compile(r'#\s*options\s*\n(\{[\S\s]*?\})(\n+#)', re.MULTILINE | re.IGNORECASE)
        #regexSettings = re.compile(r'#\s*options\s*\n(\{[\S\s]*\})(\n+#)', re.MULTILINE | re.IGNORECASE)
        matches = regexSettings.search(text)
        if (matches):
            settingsString = matches[1]
            settings = json.loads(settingsString)
        else:
            raise Exception("No options block found in text.")
        #
        self.settings = settings
        return self.settings








    def buildGame(self, gameModelPk, buildOptions, inText=None):
        # compile the story text into pdfs, etc.
        result = {}
        if (inText is not None):
            self.setText(inText)
        self.setBuildOptions(buildOptions)

        # build options
        buildDir = self.buildOptions['buildDir']
        imageDir = self.buildOptions['imageDir']

        # create build directory if it doesn't exist yet
        jrfuncs.createDirIfMissing(buildDir)

        # save text to file leads.txt, though we don't currently need to use this
        leadsFilePath = buildDir + '/leads.txt'
        jrfuncs.saveTxtToFile(leadsFilePath, self.text, "utf-8")

        # create options
        hlDirPath = os.path.abspath(os.path.dirname(__file__))
        optionsDirPath = hlDirPath + "/options"
        dataDirPath = hlDirPath + "/hldata"
        templateDirPath = hlDirPath + "/templates"
        overrideOptions = {
            "workingdir": buildDir,
            "storyDirectories": ["$workingdir"],
            "hlDataDir": dataDirPath,
            "templatedir": templateDirPath,
            "savedir": buildDir,
            "imagedir": imageDir,
            }
        
        # build story
        queueTaskBuildStoryPdf(gameModelPk, self.text, optionsDirPath, overrideOptions)

        # store message for caller
        result['message'] = "Queued story compilation to '{}' with images at '{}'.".format(buildDir, imageDir)

        return result


