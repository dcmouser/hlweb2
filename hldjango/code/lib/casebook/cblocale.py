# translation helper functions

# my libs
from .jriexception import *

# gettext translation/localization library
import gettext

# pytho modules
import os




# init
currentLanguage = None
cachedTranslations = {}


# ATTN: pygettext complains about this line when parsign for strings; thats ok.
def _(msg):
    return currentLanguage.gettext(msg)

def changeLanguage(language):
    # module global
    global currentLanguage
    #
    localeDir = os.path.join(os.path.dirname(__file__), "locale")
    #
    if (language is None):
        language = "en"
    if (language not in cachedTranslations):
        try:
            cachedTranslations[language] = gettext.translation("casebook", localeDir, languages=[language])    
        except Exception as e:
            languageList = getLanguageList("casebook", localeDir)
            msg = "Failed to set translation language to '{}'; available language codes are: {}".format(language, languageList)
            raise makeJriExceptionFromException(msg, e, None, None)
    currentLanguage = cachedTranslations[language]
    # kludge trick to force gettext to save translation files as utf-8
    diacriticalUtf8Force = _("ÑËW ŸØRK NÖIR")
    #diacriticalUtf8Force = _("ASCII")


def setDefaultLanguage():
    changeLanguage("en")


def getLanguageList(domain, localeDir):
    moFileName = domain + ".mo"
    # final all language codes
    language_codes = []
    if os.path.exists(localeDir):
        for name in os.listdir(localeDir):
            lc_messages_path = os.path.join(localeDir, name, 'LC_MESSAGES')
            moFilePath = os.path.join(lc_messages_path, moFileName)
            # Check if the .mo file exists in this path
            if os.path.exists(moFilePath):
                language_codes.append(name)
    return language_codes




# one-time setup on module load
setDefaultLanguage()
