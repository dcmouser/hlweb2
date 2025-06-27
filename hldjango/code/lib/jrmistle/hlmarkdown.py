
# mistletoe markdown to html and latex
import mistletoe
from mistletoe.latex_renderer import LaTeXRenderer

from .pylatexrenderer import PyLaTeXRenderer
from .jrhtmlrenderer import JrHtmlRenderer
from .jrmistletoedoc import JrFixedMistletoeDocument

# pylatex latex library
import pylatex
from pylatex.utils import NoEscape

# other python libs
import json
import re


# 4/23/25 FUCKED KLUDGE
# we were losing an occaional line starting with latex spaces ~~~~ it turns out the CodeFence token in mistletoe markdown parser is absorbing this as a CodeFence token with a comment
# so we have to kill the token, which is very kludgey at least in this version of mistletoe (1.40)
origAll = mistletoe.block_token.__all__
#mistletoe.block_token.__all__ = ['BlockCode', 'Heading', 'Quote', 'CodeFence', 'ThematicBreak', 'List', 'Table', 'Footnote', 'Paragraph']
#mistletoe.block_token.__all__ = ['BlockCode', 'Heading', 'Quote', 'ThematicBreak', 'List', 'Table', 'Footnote', 'Paragraph']
#mistletoe.block_token.reset_tokens()
mistletoe.block_token.remove_token(mistletoe.block_token.CodeFence)


class HlMarkdown:
    def __init__(self, hlParserRef):
        self.parserRef = hlParserRef
        self.options = None
    
    def setOptions(self, options):
        self.options = options

    def renderMarkdown(self, text, renderFormat, flagSnippetVsWholeDocument):
        origText = text
        extras = {}

        if ("ATTN FUCK OFF" in text):
            print("DEBUG BREAK")


        if (self.options['forceLinebreaks']):
            text = text.replace('\n','\n\n')

        if (renderFormat=='html'):
            text = text + '\n\n'

            #renderer = JrHtmlRenderer()
            #text = renderer.render(mistletoe.Document(text))
            text = mistletoe.markdown(text, renderer=JrHtmlRenderer)
            #text = Markdown(text, renderer=JrHtmlRenderer)

            # kludgey bugfix needed for newlines
            text = text.replace('<p>\\</p>','<p>&nbsp;</p>')
            text = text.replace('<p>~</p>','<p>&nbsp;</p>')

            #text = mistletoe.markdown(text)
            text = text.strip()


        elif (renderFormat=='latex'):
            #text = mistletoe.markdown(text, LaTeXRenderer)
            #renderer = LaTeXRenderer()
            #text = mistletoe.markdown(text, PyLaTeXRenderer)

            renderer = PyLaTeXRenderer(self.parserRef)
            # packages
            renderer.addPackage('fontenc', ['T1'])
            renderer.addPackage('inputenc', ['utf8'])
            renderer.addPackage('lmodern')
            renderer.addPackage('textcomp')
            renderer.addPackage('lastpage')
            renderer.addPackage('FiraSans')
            renderer.addPackage('librebaskerville')
            renderer.addPackage('setspace')
            renderer.addPackage('graphicx')
            renderer.addPackage('amssymb')
            # for divider symbols, etc.
            renderer.addPackage('amsthm')
            renderer.addPackage('MnSymbol')

            # paragraph spacing (NOW MOVED AFTER TOCLOFT SEE https://tex.stackexchange.com/questions/395779/using-tocloft-and-parskip-generates-a-warning-about-redefining-starttoc)
            #renderer.addPackage('parskip')


            # page numbers
            renderer.addPackage('scrlayer-scrpage')
            # table of contents font customization (mono)
            renderer.addPackage('tocloft')

            # paragraph spacing
            renderer.addPackage('parskip')

            # multi-column support
            renderer.addPackage('multicol')
            # this should add automatically but in case now
            renderer.addPackageHyperref()
            # clock symbols
            renderer.addPackage('tikz')
            renderer.addPackage('clock')
            renderer.addPackage('ifsym',['clock'])
            renderer.addPackage('fontawesome5')
            # ornamental horizontal rules
            renderer.addPackage('pgfornament')
            # color?
            #renderer.addPackage('xcolor',['dvipsnames'])
            # shadowbox
            renderer.addPackage('fancybox')
            # quoting
            #renderer.addPackage('quoting', ['font=itshape'])

            # embedded pdf
            renderer.addPackage('pdfpages')

            # fonts
            # script https://ctan.org/pkg/aurical
            renderer.addPackage('aurical')


            # MARKDOWN options (no longer used by jrinterp, etc.)
            # fancy automatic open and close quotes -- doesnt find sty?
            # but this triggers errors which are impossible to track down: "Package csquotes Error: Unbalanced groups or invalid nesting.""
            if (False):
                if (self.options['autoStyleQuotes']):
                    #renderer.addPackage('quote')
                    renderer.addPackage('babel', ['english'])
                    renderer.addPackage('csquotes', ['autostyle', 'english = american'])
                    # see below in wrapMistletoeLatexDoc for additional command
                    #\MakeOuterQuote{"}
                else:
                    renderer.addPackage('csquotes', [])
                    pass






            if (flagSnippetVsWholeDocument):
                #
                [prews, postws] = self.detectPrePostWs(text)
                # we worry that snippets look like they start on a new line, which can confuse mistletoe (ie it will think a line begins with .)
                if (False):
                    DefMidLineKludgePrefix = "MIDLINEKLUDGEPREFIX"
                    text = DefMidLineKludgePrefix + text


            #
            if (False):
                mdoc = JrFixedMistletoeDocument(text)
                text = renderer.render(mdoc)
            else:
                # old way
                mdoc = mistletoe.Document(text)
                text = renderer.render(mdoc)

            # for normal rendering 
            if (flagSnippetVsWholeDocument):
                [text, extras] = self.unwrapMistletoeLatexDoc(text)

                if (False):
                    if (text.startswith(DefMidLineKludgePrefix)):
                        text = text[len(DefMidLineKludgePrefix):]
                    else:
                        raise Exception("Expected snipped to have prefix text to remove")

                text = prews + text + postws
            else:
                # in our casebook code we do not render full document just excerpts
                pass
        else:
            raise Exception('Not understood output format for mistletoe markdown library.')
        #
        return [text, extras]


    def detectPrePostWs(self, text):
        # use regex to detect leading and trailing ws so we can reconstruct it since it gets lost in latex conversion process
        wsRegex = re.compile(r'^(\s*)[^\s].*[^\s](\s*)$', flags=re.DOTALL)
        matches = wsRegex.match(text)
        if (matches is not None):
            prews = matches.group(1)
            postws = matches.group(2)
            return [prews, postws]
        # handle single character case better
        wsRegex = re.compile(r'^(\s*)[^\s](\s*)$', flags=re.DOTALL)
        matches = wsRegex.match(text)
        if (matches is not None):
            prews = matches.group(1)
            postws = matches.group(2)
            return [prews, postws]
        return ["",""]


    def unwrapMistletoeLatexDoc(self, text):
        # clean off some initial mistletoe container text that we dont want when using snippets

        wrappedRegex = re.compile(r'^\s*\\documentclass\{[^\}]*\}\s*(.*)\\begin\{document\}\s*(.*)\s*\\end\{document\}\s*$', flags=re.DOTALL)
        matches = wrappedRegex.match(text)
        if (matches is not None):
            # got it
            text = matches.group(2)
            text = text.strip()
            preText = matches.group(1).strip()
            extras = {'latexDocClassLines': preText}
        else:
            extras = {}
            raise Exception('Did not find find expected pattern on mistletoe output to remove wrapper: {} '.format(text))
        #
        return [text, extras]


    def wrapMistletoeLatexDoc(self, text, context, preambleLatex, renderOptions):
        # add some deferred stuff stored in context during rendering of snippets
        # package classes, etc.
        addText = ''
        #addText += '\\documentclass{report}\n'

        # note the use of twoside vs oneside for double sided pages, needed to get page numbers alternating properly
        flagDoubleSided = renderOptions['doubleSided'] if ('doubleSided' in renderOptions) else False
        if (flagDoubleSided):
            sideText = 'twoside=semi'
        else:
            sideText = 'oneside'
        paperSize = renderOptions['paperSize']
        fontSize = renderOptions['fontSize']
        addText += '\\documentclass[' + sideText + ', openany, ' + fontSize + ', paper=' + paperSize + ', DIV=15]{scrbook}%\n'

        # save funcs before hyperref wraps them so we can bypass link adding
        addText += '\\let\\origaddcontentsline\\addcontentsline\n'
        addText += '\\let\\origcftaddtitleline\\cftaddtitleline\n'

        #
        if ('latexDocClassLines' in context):
            for line in context['latexDocClassLines']:
                addText += line + '\n'


        # other stuff (water)
        addText += '\\setlength{\\columnsep}{1cm}%\n'
        addText += '\\onehalfspacing%\n'
        addText += '\\setlength{\\parindent}{0pt}%\n'

        # remove extra spacing above chapter headers
        addText += '\\RedeclareSectionCommand[beforeskip=0pt,afterskip=0.5cm]{chapter}\n'
        # spacing of top chapter title
        addText += '\\renewcommand*{\\chapterheadstartvskip}{\\vspace*{-1.0cm}}\n'
        addText += '\\renewcommand*{\\chapterheadendvskip}{\\vspace*{0.5cm}}\n'
        # big chapter titles
        addText += '\\addtokomafont{chapter}{\\fontsize{50}{60}\\selectfont}'
        # mono fonts for lead toc
        addText += '\\renewcommand{\\cftchapfont}{\\ttfamily}\n'
        addText += '\\renewcommand{\\cftsecfont}{\\ttfamily}\n'
        addText += '\\renewcommand{\\cftsubsecfont}{\\ttfamily}\n'
        addText += '\\renewcommand{\\cftsubsubsecfont}{\\ttfamily}\n'
        addText += '\\renewcommand{\\cftchappagefont}{\\ttfamily}\n'
        addText += '\\renewcommand{\\cftsecpagefont}{\\ttfamily}\n'

        # fix for table of contents SUB section not getting proper font of ttfamily set above
        addText += "\\DeclareTOCStyleEntry[entryformat=\\ttfamily, pagenumberformat=\\ttfamily]{tocline}{subsection}\n"

        # title font of "Contents" line
        addText += '\\renewcommand{\\cfttoctitlefont}{\\fontsize{25}{30}\\selectfont\\bfseries\\scshape}\n'
        addText += '\\setkomafont{disposition}{\\bfseries}'

        # remove extra margin at top of table of contents
        addText += '\\setlength{\\cftbeforetoctitleskip}{0pt}\n'
        addText += '\\setlength{\\cftaftertoctitleskip}{30pt}\n'


        addText += '\\renewcommand\\cftchapafterpnum{\\vskip-2pt}\n'
        addText += '\\renewcommand\\cftsecafterpnum{\\vskip-2pt}\n'

        # for csquotes nice auto quots
        if False and (self.options['autoStyleQuotes']):
            addText += '\\MakeOuterQuote{"}\n'
        else:
            pass

        addText += preambleLatex

        # begin document
        addText += '\\begin{document}\n'

        # other stuff
        addText += '\\normalsize%\n'

        # footer page numbers
        #addText += '\\fancyfoot[RO,RE]{\\thepage}\n'
        addText += '\\clearpairofpagestyles\n'

        addText += '\\rofoot*{\\textbf{\\pagemark}}\n'
        addText += '\\lefoot*{\\textbf{\\pagemark}}\n'

        # has to be done after begin
        addText += '\\renewcommand{\\contentsname}{Contents}\n'

        #addText += '\\newfontfamily{\\FA}{FontAwesome}[Scale=3.0]\n'


        text = addText + '\n' + text
        return text



    def escapeLatex(self, text):
        return pylatex.escape_latex(text)




# ---------------------------------------------------------------------------
    def escapeForSafeMarkdown(self, text):
        # escape text for latext markdown
        return self.escapeLatex(text)

    def latexDivider(self):
        return '\n\\cbDividerlead\n'
        #return '\n$\\hfill\\blacksquare$%\n'
# ---------------------------------------------------------------------------
    

