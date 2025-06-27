from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint

from pdf2image import convert_from_path


def convertPdfFileToImageFile(sourcePdfFilePath, destinationImageFilePath, outputExtension, convertDpi):
    dpi = convertDpi

    # TEST kludge for windows
    poppler_path = r"C:/ProgramFiles/poppler/Library/bin"
    if (not jrfuncs.pathExists(poppler_path)):
        poppler_path = None

    #jrprint("Converting from {} to {}.".format(sourcePdfFilePath, destinationImageFilePath))

    outputExtensionFormat = outputExtension
    if (outputExtensionFormat=="jpg"):
        outputExtensionFormat = "jpeg"

    # create teh IMAGES (this will not save them yet)
    #retv = convert_from_path(sourcePdfFilePath, dpi, None, 0, 0, outputExtension, poppler_path=poppler_path)
    timeoutSecs = 10
    retv = convert_from_path(sourcePdfFilePath, dpi, poppler_path=poppler_path, first_page=1, last_page=1, timeout=timeoutSecs)
    if (len(retv)>0):
        img = retv[0]
        jrfuncs.deleteFilePathIfExists(destinationImageFilePath)
        retvSave = img.save(destinationImageFilePath, outputExtensionFormat)
        # no return value, will throw excetption
        retvFileExists = jrfuncs.pathExists(destinationImageFilePath)
        return retvFileExists
    return False

