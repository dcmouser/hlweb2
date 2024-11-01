# helper class that maintains a simple global dictionary of default or environmental values
# we use this to coordinate settings values so we can override them in any order

import os


class JrGlobalEnv:
    def __init__(self):
        self.explicitValues = {}
        self.defaultValues = {}

    def getValue(self, key, defaultVal=None):
        # check if its explicitly set
        if (key in self.explicitValues):
            return self.explicitValues[key]
        # is it set in environment
        envValue = self.getSmartEnvironmentValue(key)
        if (envValue is not None):
            return envValue
        # is it default set?
        if (key in self.defaultValues):
            return self.defaultValues[key]
        # otherwise return caller default
        return defaultVal

    def setDefault(self, key, val):
        self.defaultValues[key] = val
    
    def setValue(self, key, val):
        self.explicitValues[key] = val

    def getSmartEnvironmentValue(self, key):
        val = os.getenv(key)
        if (val is not None):
            # smart conversion from strings
            if (type(val) is str):
                valLower = val.lower()
                if (valLower in ['true','1','yes']):
                    val = True
                elif (valLower in ['false','0','no']):
                    val = False
        return val


# module global
jrGlobalEnv = JrGlobalEnv()
