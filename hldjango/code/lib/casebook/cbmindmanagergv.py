from .cbmindmanager import CbMindManager

# helpers
from .jriexception import *
from lib.jr import jrfuncs

# python
import os
import pathlib
import json


if (True):
    # GRAPHVIZ GENERATES A TON OF WARNINGS ABOUT DEPRECATED CALLS
    import logging
    # Get the logger for Graphviz (you might need to adjust the logger name based on the library specifics)
    graphviz_logger = logging.getLogger('graphviz')
    # Set the logger level to ERROR to suppress warnings and below
    graphviz_logger.setLevel(logging.ERROR)

# graphviz
import graphviz








































# VISUALIZATION via graphviz




class CbMindManagerGv(CbMindManager):
    def __init__(self):
        super().__init__()
        #
        self.dot = None
        # kludgey test
        if (not 'Graphviz' in os.environ["PATH"]):
            os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'




# ---------------------------------------------------------------------------
    def renderToDotText(self):
        self.buildGraphViz()
        return self.dot.source


    def renderToDotFile(self, outFilePath, encoding='utf-8'):
        dotText = self.renderToDotText()
        with open(outFilePath, 'w', encoding=encoding) as outfile:
            outfile.write(dotText)


    def renderToDotImageFile(self, outputDirPath, baseFilename, flagDebug):
        #
        outFilePath = outputDirPath + "/" + baseFilename + "_mindmap.dot"
        outFilePathPdfExpected = outFilePath + '.pdf'
        outFilePathPdfFinal = outFilePath.replace('.dot', '.pdf')
        if (flagDebug):
            jrprint('Drawing mind map vizualization to: {}'.format(outFilePathPdfFinal))
        #
        jrfuncs.deleteFilePathIfExists(outFilePath)
        jrfuncs.deleteFilePathIfExists(outFilePathPdfExpected)
        jrfuncs.deleteFilePathIfExists(outFilePathPdfFinal)
        #
        self.buildGraphViz()
        self.dot.render(outFilePath)
        #
        fileSuccessfullyCreated = jrfuncs.pathExists(outFilePathPdfExpected)
        if (True) and (fileSuccessfullyCreated) and (outFilePathPdfExpected != outFilePathPdfFinal):
            jrfuncs.renameFile(outFilePathPdfExpected, outFilePathPdfFinal)
            fileSuccessfullyCreated = jrfuncs.pathExists(outFilePathPdfFinal)
            if (fileSuccessfullyCreated):
                # delete the .dot file
                jrfuncs.deleteFilePathIfExists(outFilePath)
        #
        return [fileSuccessfullyCreated, outFilePathPdfFinal]
# ---------------------------------------------------------------------------








# ---------------------------------------------------------------------------
    def buildGraphViz(self):
        #jrprint('Building graphiviz structure...')

        # main graph
        dot = graphviz.Digraph(comment='Story')
        dot.attr(rankdir='LR')

        if (False):
            dot.attr(layout="neato")
            dot.attr(scale="2")


        # graphviz colors, etc.:
        # https://graphviz.org/doc/info/colors.html


        # NODES
        for id, node in self.nodeHash.items():
            # skip drawing it?
            if (self.shouldSkipDrawingNode(node)):
                continue

            # add nodes
            nodeId = node['id']

            #
            label = node['label'] if ('label' in node and node['label']!='' and node['label'] is not None) else nodeId
            mtype = node['type']
            subtype = node['subtype'] if ('subtype' in node) else None
            mStyle = node['mStyle'] if ('mStyle' in node) else None

            # shapes see https://graphviz.org/doc/info/shapes.html
            color = 'black'
            penwidth = '1'
            shape = 'rectangle'
            #
            if (mtype=='tag'):
                if (subtype=="check"):
                    shape = 'ellipse'
                    color = 'firebrick1'
                    penwidth = '2'
                elif (subtype in ['cond']):
                    shape = 'ellipse'
                    color = 'brown2'
                    penwidth = '2'
                elif (subtype in ['trophy','decoy']):
                    shape = 'ellipse'
                    color = 'olive'
                elif (subtype=='doc'):
                    shape = 'note'
                    color = 'red'
                else:
                    shape = 'hexagon'
                    color = 'red'
            elif (mtype=='concept'):
                shape='cylinder'
                color = 'blue'
                penwidth = '2'
            elif (mtype=='day'):
                shape = 'circle'
                penwidth = '2'
            elif (mtype=='lead'):
                shape='rectangle'
                color = 'blue'
            elif (mtype=='entry'):
                shape='hexagon'
                color = 'blue'
                penwidth = '2'
            else:
                shape = 'diamond'
                color = 'red'
                penwidth = '4'

            if (mStyle is not None) and (mtype!='entry'):
                # we dont obey this for ENTRIES since we want them to look distinct
                if (mStyle in ["research", "ally","contact"]):
                    # contact/research nodes more dramatic; these are places the player may just go to, so we dont nesc. expect them to have links into them
                    shape= 'house'
                    color = 'deepskyblue'
                    penwidth = '2'
                if (mStyle in ["fingerprint", "crimehistory"]):
                    # contact/research nodes more dramatic; these are places the player may just go to, so we dont nesc. expect them to have links into them
                    shape = 'component'
                    color = 'dodgerblue3'
                    penwidth = '2'
                elif (mStyle=="hint"):
                    shape = 'egg'
                    penwidth = '2'
                    color = "chocolate2"
                elif (mStyle=="inline"):
                    color = "darkcyan"
                else:
                    # complain?
                    pass
            #
            if ("LEADS" in nodeId) or ("LEADS" in label):
                jrprint("ATTN:DEBUG BREAK")
            #
            dot.node(nodeId, label, shape=shape, color=color, penwidth=penwidth)


        # LINKS
        for link in self.links:
            arrowDirection = "forward"
            sourceNodeId = link.sourceHash
            targetNodeId = link.targetHash
            #
            if (sourceNodeId is None) or (targetNodeId is None):
                # ATTN: TODO support these kind of attribute labels
                continue

            # skip drawing it?
            if (self.shouldSkipDrawingNodeById(sourceNodeId)):
                continue
            if (self.shouldSkipDrawingNodeById(targetNodeId)):
                continue
            #
            linkType = link.typeStr
            #
            dotEdgeLabel = link.label
            if (dotEdgeLabel is None) or (dotEdgeLabel==""):
                dotEdgeLabel = link.typeStr

            # default
            color = 'black'
            penwidth = '1'

            # logic
            if (linkType in ['mentions','implies','suggests','informs','refers']):
                color = 'purple'
                penwidth = '1'
            elif (linkType in ['follows']):
                color = 'brown'
                penwidth = '2'
                arrowDirection = "reverse"
                # reverse direction, requires change label
                if (dotEdgeLabel == 'follows'):
                    dotEdgeLabel = 'followed by'
            elif (linkType in ['followed', 'proceed']):
                color = 'brown'
                penwidth = '2'
            elif (linkType=='provides'):
                color = 'red'
                penwidth = '2'
            elif (linkType=='irp'):
                color = 'blue'
                penwidth = '1'
            #
            # travel
            elif (linkType=='embeds'):
                color = 'darkcyan'
                #arrowDirection = 'reverse'
            elif (linkType=='inlines'):
                color = 'darkcyan'
            elif (linkType in ['inlineb', 'eventInline']):
                color = 'darkcyan'
                #arrowDirection = "both"
            elif (linkType=='returns'):
                color = 'darkcyan'
            elif (linkType=='go'):
                color = 'brown'
            elif (linkType=='event'):
                color = 'brown'
            elif (linkType=='irp'):
                color = 'brown'
            #
            # tags
            elif (jrfuncs.startsWithAny(linkType, ['gain', 'circle', 'underline', 'strike'])):
                color = 'darkgreen'
            elif (jrfuncs.startsWithAny(linkType, ['has','require','check','missing'])):
                color = 'red'
                arrowDirection = "reverse"
            # days
            elif (linkType in ['on', 'before', 'after']):
                color = 'royalblue'
                penwidth = '2'
                arrowDirection = "reverse"
            elif (linkType == 'deadline'):
                color = 'crimson'
                penwidth = '2'                     

            # ATTN: UNUSED so far
            elif (linkType=='hint'):
                color = 'purple'

            elif (linkType.startswith('concept')):
                color = 'deeppink'
                penwidth = '2'

            # unknoiwn
            else:
                color = "red"
                penwidth = '5'
            #

            if (arrowDirection == "forward"):
                dot.edge(sourceNodeId, targetNodeId, dotEdgeLabel, color=color, penwidth=penwidth)
            elif (arrowDirection == "both"):
                dot.edge(targetNodeId, sourceNodeId, dotEdgeLabel, color=color, dir="both", penwidth=penwidth)
            else:
                dot.edge(targetNodeId, sourceNodeId, dotEdgeLabel, color=color, penwidth=penwidth)

        # store it
        self.dot = dot
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
    def shouldSkipDrawingNode(self, node):
        if (node is None):
            return True
        nodeId = node["id"]
        nodeLabel = node["label"]
        showDefault = node["showDefault"]

        # individual mStyle can be set to hide to hide it
        mStyle = jrfuncs.getDictValueOrDefault(node, 'mStyle', None)
        if (mStyle=="hide"):
            return True

        # if set to show by default then dont hide it
        if (showDefault):
            return False

        #if (node["type"]=="entry"):
            # entries (not leads but the basis for leads) we ONLY show if they are linked to

        # if something connects to it then dont hide it
        if (self.doesAnyLinkConnectToNodeId(node["id"])):
            return False

        # nothing connects and it doesnt show by default, so hide it
        return True


    def shouldSkipDrawingNodeById(self, nodeId):
        node = self.findNodeById(nodeId)
        if (node is None):
            return True
        return self.shouldSkipDrawingNode(node)


    def findNodeById(self, nodeId):
        if (nodeId in self.nodeHash):
            return self.nodeHash[nodeId]
        return None


    def doesAnyLinkConnectToNodeId(self, nodeId):
        for link in self.links:
            if (link.sourceHash == nodeId) or (link.targetHash == nodeId):
                return True
        return False
# ---------------------------------------------------------------------------
