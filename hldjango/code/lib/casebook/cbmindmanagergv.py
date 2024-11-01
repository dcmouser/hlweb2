from .cbmindmanager import CbMindManager

# helpers
from .jriexception import *
from lib.jr import jrfuncs

# python
import os
import pathlib
import json

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
                elif (subtype=="cond"):
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

            if (mStyle is not None):
                if (mStyle=="research"):
                    # research nodes more dramatic
                    color = 'deepskyblue'
                    penwidth = '3'
                elif (mStyle=="hint"):
                    penwidth = '2'
                    color = "purple"
                elif (mStyle=="inline"):
                    color = "darkcyan"
                else:
                    # complain?
                    pass
            #
            dot.node(nodeId, label, shape=shape, color=color, penwidth=penwidth)


        # LINKS
        for link in self.links:
            arrowDirection = "forward"
            sourceNodeId = link.source
            targetNodeId = link.target
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
                penwidth = '3'
                arrowDirection = "reverse"
            elif (linkType=='provides'):
                color = 'red'
                penwidth = '2'
            #
            # travel
            elif (linkType=='embeds'):
                color = 'darkcyan'
                arrowDirection = 'reverse'
            elif (linkType=='inlines'):
                color = 'darkcyan'
            elif (linkType=='inlineb'):
                color = 'darkcyan'
                #arrowDirection = "both"
            elif (linkType=='returns'):
                color = 'darkcyan'
            elif (linkType=='go'):
                color = 'brown'
            #
            # tags
            elif (linkType=='gain'):
                color = 'darkgreen'
            elif (linkType in ['has','require','check','missing']):
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
        # skip drawing it?
        if (nodeLabel=="BLANK"):
            return True

        mStyle = node['mStyle'] if ('mStyle' in node) else None
        if (mStyle=="hide"):
            return True

        if (node["type"]=="entry"):
            # entries we ONLY show if they are linked to
            if (self.linkConnectsToNodeId(node["id"])):
                return False
            return True

        # by default dont skip
        return False


    def shouldSkipDrawingNodeById(self, nodeId):
        node = self.findNodeById(nodeId)
        if (node is None):
            return True
        return self.shouldSkipDrawingNode(node)


    def findNodeById(self, nodeId):
        if (nodeId in self.nodeHash):
            return self.nodeHash[nodeId]
        return None


    def linkConnectsToNodeId(self, nodeId):
        for link in self.links:
            if (link.source == nodeId) or (link.target == nodeId):
                return True
        return False
# ---------------------------------------------------------------------------
