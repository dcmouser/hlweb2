# for special effect processing on images

import subprocess
import shutil

from lib.jr import jrfuncs



effectDictionary = {
    "bwDither4": { "engine": "magick", "effect": "BwDither", "suffixShort": "_bwdither", "suffixLong": "_bwdither4", "label": "Black & White dithered", "overwrite": True, "size": 4},
    "bwDither6": { "engine": "magick", "effect": "BwDither", "suffixShort": "_bwdither", "suffixLong": "_bwdither6", "label": "Black & White dithered", "overwrite": True, "size": 6},
    "bwDither8": { "engine": "magick", "effect": "BwDither", "suffixShort": "_bwdither", "suffixLong": "_bwdither8", "label": "Black & White dithered", "overwrite": True, "size": 8},
    "colorDither4": {  "engine": "magick", "effect": "ColorDither", "suffixShort": "_dither", "suffixLong": "_dither4", "label": "Color dithered", "overwrite": True, "size": 4},
    "colorDither6": {  "engine": "magick", "effect": "ColorDither", "suffixShort": "_dither", "suffixLong": "_dither6", "label": "Color dithered", "overwrite": True, "size": 6},
    "colorDither8": {  "engine": "magick", "effect": "ColorDither", "suffixShort": "_dither", "suffixLong": "_dither8", "label": "Color dithered", "overwrite": True, "size": 8},
    "flatAlpha": {  "engine": "magick", "effect": "flatten", "suffixShort": "_flat", "suffixLong": "_flat", "label": "flattened alpha", "overwrite": True, "size": 8},
}





class JrImageEffects:
    def __init__(self):
        pass

    def calcEffectOptionsByKey(self, effectKey):
        if (effectKey not in effectDictionary):
            return None
        return effectDictionary[effectKey]


    def suffixFilePath(self, path, effectKey, suffixKey):
        suffixedPath = jrfuncs.addSuffixToPath(path, effectDictionary[effectKey][suffixKey])
        return suffixedPath

    def run(self, path, outPath, effectOptions):
        engine = effectOptions["engine"]
        if (engine=="magick"):
            return self.runImageMagick(path, outPath, effectOptions)
        #
        return {"success": False, "message": "Unknown jreffect engine '{}'.".format(engine)}



    def runImageMagick(self, path, outPath, effectOptions):
        
        # try to guess executable name of imageMagick; if we can't find it we still try first to throw an error later
        executableNamesToTry = ["magick", "magick.exe", "convert"]
        executablePath = executableNamesToTry[0]
        for executableName in executableNamesToTry:
            if (shutil.which(executableName) is not None):
                executablePath = executableName
                break

        effect = effectOptions["effect"]
        sizeStr = str(jrfuncs.getDictValueOrDefault(effectOptions, "size", 6))
        argDict = {
            "BwDither": ["convert", path, "-colorspace", "Gray", "-ordered-dither", "h{}x{}a".format(sizeStr,sizeStr), outPath],
            "ColorDither": ["convert", path, "-ordered-dither", "h{}x{}a".format(sizeStr,sizeStr), outPath],
            "flatten": [path, "-background", "white", "-alpha", "remove", "-alpha", "off", outPath],
        }
        if (effect not in argDict):
            return {"success": False, "message": "Unknown ImageMagick jreffect '{}'.".format(effect)}
        args = argDict[effect]

        retv = self.runCommandLine(executablePath, args, outPath)
        return retv


    def runCommandLine(self, executablePath, args, expectedOutPut):
        
        # ATTN: as of 2/23/25 on my docker ubuntu imagemagick throws an error about "no decode delegate" even when it works, so i will kludge a workaround
        oldFileTime = jrfuncs.calcModificationDateOfFileOrZero(expectedOutPut)
        try:
            command = [executablePath] + args
            # Run the command and capture the output
            result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            message = "Successfully ran {}: {}".format(command, result.stdout)
            retv = True
        except subprocess.CalledProcessError as e:
            eStdErr = e.stderr
            if ("no decode delegate for this image format" in eStdErr):
                # ATTN: kludge here - if we see this error, we check if file was actually created
                newFileTime = jrfuncs.calcModificationDateOfFileOrZero(expectedOutPut)
                if (newFileTime>oldFileTime):
                    retv = {"success": True, "message": "Appears to have completed as expected."}
                    return retv
            #
            message = jrfuncs.exceptionPlusSimpleTraceback(e, "Error while running jreffect commandline: {} with {}; details = {}.".format(executablePath, args, eStdErr))
            retv = False
        except Exception as e:
            message = jrfuncs.exceptionPlusSimpleTraceback(e, "Error while running jreffect commandline: {} with {}.".format(executablePath, args))
            retv = False
        #
        retv = {"success": retv, "message": message}
        return retv
