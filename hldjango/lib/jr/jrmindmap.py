# imports
from lib.jr import jrfuncs
from lib.jr import jroptions
from lib.jr.jrfuncs import jrprint
from lib.jr.jrfuncs import jrException

# python imports
import os
import pathlib
import json
import re

# graphviz
import graphviz


# ---------------------------------------------------------------------------
class JrMindMap:
    def __init__(self, options={}):
        self.options = options
        #
        self.nodes = {}
        # test
        os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'




# ---------------------------------------------------------------------------
    def debug(self):
        jrprint('JrMindMap debug nodes:\n')
        for id, node in self.nodes.items():
            jrprint(' Node {} ({})'.format(node['id'], node['props']['mtype']))
            for linkFrom in node['from']:
                nodeFrom = linkFrom['from']
                jrprint('    from node {} ({}) via {}'.format(nodeFrom['id'], nodeFrom['props']['mtype'], linkFrom['props']['mtype']))
            for linkTo in node['to']:
                nodeTo = linkTo['to']
                jrprint('    to node {} ({}) via {}'.format(nodeTo['id'], nodeTo['props']['mtype'], linkTo['props']['mtype']))
        jrprint('\n\n')
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def getNodes(self):
        return self.nodes
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def findNodeById(self, id):
        if (id in self.nodes):
            return self.nodes[id]
        return None
    
    def addNode(self, node):
        nodeId = node['id']
        self.nodes[nodeId] = node
    
    def addLink(self, link):
        fromNode = link['from']
        toNode = link['to']
        fromNode['to'].append(link)
        toNode['from'].append(link)

    def annotateNode(self, node, attributes):
        for k,v in attributes.items():
            node['props'][k] = v
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
    def createNode(self, id, props):
        node = {'id': id, 'from': [], 'to': [], 'props': props}
        return node


    def createLink(self, fromNode, toNode, props):
        link = {'from': fromNode, 'to': toNode, 'props': props}
        return link
# ---------------------------------------------------------------------------
            


# ---------------------------------------------------------------------------
    def renderToDotText(self):
        self.buildGraphViz()
        return self.dot.source


    def renderToDotFile(self, outFilePath, encoding='utf-8'):
        dotText = self.renderToDotText()
        with open(outFilePath, 'w', encoding=encoding) as outfile:
            outfile.write(dotText)


    def renderToDotImageFile(self, outFilePath):
        jrprint('Drawing graphizualization to: {}'.format(outFilePath))
        self.buildGraphViz()
        self.dot.render(outFilePath)
# ---------------------------------------------------------------------------
 



# ---------------------------------------------------------------------------
    def buildGraphViz(self):
        jrprint('Building graphiviz structure...')

        # main graph
        dot = graphviz.Digraph(comment='Story')
        dot.attr(rankdir='LR')

        if (False):
            dot.attr(layout="neato")
            dot.attr(scale="2")


        # graphviz colors, etc.:
        # https://graphviz.org/doc/info/colors.html


        # add all nodes
        for id, node in self.nodes.items():
            # add nodes
            nodeId = node['id']
            nodeProps = node['props']
            label = nodeProps['label'] if ('label' in nodeProps and nodeProps['label']!='' and nodeProps['label'] is not None) else nodeId
            mtype = nodeProps['mtype']

            # shapes see https://graphviz.org/doc/info/shapes.html
            color = 'black'
            penwidth = '1'
            shape = 'rectangle'
            #
            if (mtype is None):
                shape = 'diamond'
                color = 'red'
                penwidth = '4'
            elif (mtype=='tag'):
                shape = 'ellipse'
            elif (mtype=='day'):
                shape = 'circle'
                penwidth = '2'
            elif (mtype in ['cond','check']):
                shape = 'ellipse'
                color = 'purple'
            elif (mtype in ['trophy','decoy']):
                shape = 'ellipse'
                color = 'yellow'
            elif (mtype in ['hint']):
                shape = 'hexagon'
                color = 'purple'
            elif (mtype=='task'):
                shape = 'hexagon'
                color = 'blue'
            elif (mtype=='idea'):
                shape = 'ellipse'
                color = 'darkorange'
                penwidth = '2'
            elif ('inline' in mtype):
                shape='rectangle'
                color = 'lightgreen'
            elif (mtype=='lead.person'):
                shape = 'hexagon'
            elif (mtype=='lead.yellow'):
                shape = 'house'

            elif (mtype=='doc'):
                shape = 'note'
                color = 'red'
            #
            # relevance
            if ('relevance' in nodeProps) and (nodeProps['relevance']<0):
                color = 'pink'
            #
            dot.node(nodeId, label, shape=shape, color=color, penwidth=penwidth)


        # add all links
        for id, node in self.nodes.items():
            nodeId = node['id']
            for link in node['to']:
                toNode = link['to']
                toNodeId = toNode['id']
                linkType = link['props']['mtype']
                isInline = link['props']['inline'] if ('inline' in link['props']) else False
                # label
                dotEdgeLabel = link['props']['label'] if ('label' in link['props'] and link['props']['label']!='' and link['props']['label'] is not None) else linkType

                # default
                color = 'black'
                penwidth = '1'
                if (isInline):
                    color = 'green'

                if (linkType=='goto'):
                    pass
                elif (dotEdgeLabel == 'mentions'):
                    penwidth = '3.5'
                elif (dotEdgeLabel == 'implies'):
                    penwidth = '2'
                elif (dotEdgeLabel=='suggests'):
                    penwidth = '1'
                elif (dotEdgeLabel=='informs'):
                    color = 'blue'
                elif (dotEdgeLabel=='provides'):
                    color = 'red'
                    penwidth = '2'
                elif (dotEdgeLabel=='hint'):
                    color = 'purple'
                #
                dot.edge(nodeId, toNodeId, dotEdgeLabel, color=color, penwidth=penwidth)

        # store it
        self.dot = dot
# ---------------------------------------------------------------------------
 

 

