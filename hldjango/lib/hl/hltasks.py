# see https://huey.readthedocs.io/en/latest/consumer.html

from hueyconfig import huey
from lib.hl import hlparser



# module global funcs
@huey.task()
def queueTaskBuildStoryPdf(gameModelPk, text, optionsDirPath, overrideOptions):
    # this may take a long time to run (minutes)

    # create hl parser
    hlParser = hlparser.HlParser(optionsDirPath, overrideOptions)

    # parse text
    hlParser.parseStoryTextIntoBlocks(text, 'hlweb2')

    # run pdf generation
    hlParser.runAllSteps()

    # now store result in game model instance gameModelPk
    pass
