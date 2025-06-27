# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint



# NEW exception which includes source location
class JriException(Exception):
    def __init__(self, message, slocs, severity, msgExtra = None):
        self.message = message
        self.slocs = slocs
        self.severity = severity
        self.msgExtra = msgExtra

    def __str__(self):
        # create string representation of message in a primitive way, without access to outside info
        slocs = self.slocs
        if (slocs is None):
            # no location info
            return self.message
        else:
            msgs = [self.message]
            if (isinstance(slocs, list)):
                index = 1
                for sloc in slocs:
                    if (sloc is not None):
                        msgs.append("{}. {}".format(index, self.slocInfoStr(sloc)))
                        index += 1
            else:
                sloc = slocs
                if (sloc is not None):
                    msgs.append(self.slocInfoStr(slocs))
        retStr = ";\n".join(msgs)

        # add extra
        if (self.msgExtra is not None) and (self.msgExtra!=""):
            retStr += "\n" + self.msgExtra

        return retStr


    def slocInfoStr(self, sloc):
        return makeSlocStringWithNodeTokenDebugInfo(sloc)


    def prettyPrint(self):
        return self.__str__()





def makeJriException(msg, sloc, msgExtra = None):
    # add node information
    return JriException(msg, sloc, 1, msgExtra)

def makeJriExceptionFromException(msgPrefix, e, sloc, msgExtra):
    # add node information
    if (msgPrefix is not None) and (msgPrefix!=""):
        msg = msgPrefix + ": " + str(e)
    else:
        msg = str(e)

    newException = JriException(msg, sloc, 1, msgExtra).with_traceback(e.__traceback__)
    # is recording the original_exception sufficient to preserve traceback?
    newException.original_exception = e
    #
    return newException



def makeModifyJriExceptionAddLocIfNeeded(e, sloc, msgExtra):
    # given an exception if its already a jri exception with an sloc then do nothing,
    # otherwise convert any exception to a jri exception and add pass loc
    if (isinstance(e, JriException)):
        # already a jri exception, just check loc
        if (e.slocs is None):
            e.slocs = sloc
        # return same object
        return e
    # its a standard exception, so we need to wrap it
    return makeJriExceptionFromException(None, e, sloc, msgExtra)




def logJriWarning(msg, sloc, env):
    # make an exception, but then just display it instead of raising it
    # ATTN: we pass env because we want access to global context so that we can log warnings properly eventually, etc.
    # ATTN: TODO we would like to 
    jri = JriException(msg, sloc, 0)
    jrprint("JRI WARNING:" + msg)




def makeSlocStringWithNodeTokenDebugInfo(sloc):
    from .jrastutilclasses import JrSourceLocation
    from .jrastvals import JrAst

    line = None
    deepSourceDebugMsg = None
    #
    msg = None
    if (sloc is not None):
        if (isinstance(sloc, JrAst)):
            # our jrast tracks this info (using an attached sourceloc)
            line = sloc.getSourceLine()
            start_pos = sloc.getSourceStartPos()
            end_pos = sloc.getSourceEndPos()
            column = sloc.getSourceColumn()
            msg = "AstNode"
            # because we are reporting a JrAst we can get the source line and info
            deepSourceDebugMsg = sloc.getRootDeepSourceHighlightedLineDebugMessage(start_pos, end_pos)
            #
        # below here we have less information about the source of the error
        elif (isinstance(sloc, JrSourceLocation)):
            # get it from sourceloc object
            line = sloc.getSourceLine()
            start_pos = sloc.getSourceStartPos()
            column = sloc.getSourceColumn()
            msg = "Sloc"        
        #
        elif (hasattr(sloc, "_meta")):
            nodeMeta = sloc._meta
            line = nodeMeta.line
            start_pos = nodeMeta.start_pos
            column = nodeMeta.column
            #
            msg = "Token"
            nodeData = sloc.data
            if (hasattr(nodeData,"type")):
                msg += " '{}'".format(nodeData.type)
            elif (type(nodeData) is str):
                msg += "({})".format(nodeData)
            #
            if (hasattr(nodeData,"value")):
                msg += ":'{}'".format(nodeData.value)
        #
        if (line is not None):
            msg += " at line {}, col {}".format(line, column)

    # add debug
    if (msg is None):
        msg = "[No source location information available]"
    else:
        if (deepSourceDebugMsg is not None):
            msg += "\n" + deepSourceDebugMsg
    #
    return msg




