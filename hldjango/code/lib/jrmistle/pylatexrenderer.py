# -*- coding: utf-8 -*-

"""
LaTeX renderer for mistletoe with pylatex.
"""

from .jrhtmlrenderer import MyUnderline

#from mistletoe import Markdown
#from mistletoe.block_token import CodeFence, BlockToken, Heading, Quote, ThematicBreak, List, Table

import mistletoe.latex_token as latex_token
from mistletoe.base_renderer import BaseRenderer
from mistletoe.latex_renderer import LaTeXRenderer

from pylatex import *
from pylatex.base_classes import *
from pylatex.utils import *

# python modules
from itertools import chain
from urllib.parse import quote
import json
import re



# see https://github.com/miyuchina/mistletoe/blob/master/mistletoe/latex_renderer.py

class PyLaTeXRenderer(LaTeXRenderer):
    def __init__(self, hlParserRef, *extras, **kwargs):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
        """
        self.parserRef = hlParserRef
        #
        tokens = self._tokens_from_module(latex_token)
        self.packages = {}
        super().__init__(*chain(tokens, extras), **kwargs)

        # underline support
        # doesnt seem to do anything
        self.render_map["MyUnderline"] = self.render_underline
        # needed?
        #self.add_token(MyUnderline) 




# here i start with a COPY of the base latex class, so that I can see that functions exist and do what
# eventually we will delete any functions that are left unchanged in the base class


    def addPackage(self, name, options = []):
        self.packages[name] = options

    def addPackageHyperref(self):
        self.packages['hyperref'] = ['pdfusetitle,colorlinks=true,linkcolor=blue,filecolor=magenta,urlcolor=cyan']




    def render_strong(self, token):
        return '\\textbf{{{}}}'.format(self.render_inner(token))

    def render_emphasis(self, token):
        return '\\textit{{{}}}'.format(self.render_inner(token))

    def render_inline_code(self, token):
        content = self.render_raw_text(token.children[0], escape=False)

        # search for delimiter not present in content
        for delimiter in self.verb_delimiters:
            if delimiter not in content:
                break

        if delimiter in content:  # no delimiter found
            raise RuntimeError('Unable to find delimiter for verb macro')

        template = '\\verb{delimiter}{content}{delimiter}'
        return template.format(delimiter=delimiter, content=content)

    def render_strikethrough(self, token):
        self.packages['ulem'] = ['normalem']
        return '\\sout{{{}}}'.format(self.render_inner(token))

    def render_image(self, token):
        raise Exception("Latex mistletoe markdown image support is disabled (see pylatexrenderer.py).")
        self.packages['graphicx'] = []
        # ATTN: jr 2/11/24 support for heigh and width
        imageSource = token.src
        extra = ''
        matches = re.match(r'([^\|]*)\|(.*)', imageSource)
        if (matches is not None):
            imageSource = matches.group(1)

            imageOptions = '|' + matches.group(2) + '|'
            # image options, most common are height and width
            width='1.0'
            height=''
            #matches = re.match(r'width\s*=\s*(.*)\s*|\s*height\s*=\s*(.*)', imageOptions)
            #if (matches is not None):
            #    width = matches.group(1)
            #    height = matches.group(2)
            matches = re.match(r'.*\|width=([^|]*)\|.*', imageOptions)
            if (matches is not None):
                width = matches.group(1)
            matches = re.match(r'.*\|height=([^|]*)\|.*', imageOptions)
            if (matches is not None):
                height = matches.group(1)
            if (width!='') and (height!=''):
                #extra += 'width={}, height={}'.format(width,height)
                extra += 'width={}\\columnwidth, height={}'.format(width,height)
            elif (width!=''):
                #extra += 'width={}'.format(width)
                extra += 'width={}\\columnwidth'.format(width)
            elif (height!=''):
                extra += 'height={}'.format(height)
            else:
                extra += 'width={}, height={}'.format('\\columnwidth','\\textheight')
            if (extra !=''):
                extra += ',keepaspectratio'
                extra = '[' + extra + ']'
            #[width=1in, height=1in
        else:
            # always force it to width height
            extra += 'width={}, height={}'.format('\\columnwidth','\\textheight')
            extra += ',keepaspectratio'
            extra = '[' + extra + ']'
        #
        # new, we INSIST the image be found in our authorized image dirs via helper
        try:
            imageSourceResolved = self.safelyResolveImageSource(imageSource)
        except Exception as e:
            #parent = token.parent
            #lineNumber = token.line_number
            #tokenLocInfoStr = json.dumps(token)
            #raise Exception('Exception generating latex while trying to include image at location {}: {}'.format(tokenLocInfoStr,str(e)))
            raise Exception('Exception generating latex while trying to include image: {}'.format(str(e)))
        #
        retv = '\\includegraphics{}{{{}}}'.format(extra, imageSourceResolved)
        retv = '\\begin{center}' + retv + '\\end{center}'
        retv = '\n' + retv + '\n'
        return retv







    def render_math(self, token):
        # math symbol paragraphs this called stuff like $ and messes up so we need it escaped
        if (True):
            return self.render_raw_text(token)
        #
        self.packages['amsmath'] = []
        self.packages['amsfonts'] = []
        self.packages['amssymb'] = []
        return token.content

    def render_escape_sequence(self, token):
        return self.render_inner(token)

    def render_raw_text(self, token, escape=True):
        tokenContent = token.content
        if escape:
            tokenContent = tokenContent.replace('$', '\\$').replace('#', '\\#').replace('{', '\\{').replace('}', '\\}').replace('&', '\\&').replace('_', '\\_').replace('%', '\\%')
        return tokenContent



    def render_quote(self, token):
        #self.packages['csquotes'] = []
        template = '\\begin{{displayquote}}\n{inner}\\end{{displayquote}}\n'
        return template.format(inner=self.render_inner(token))

    def render_paragraph(self, token):
        return '\n{}\n'.format(self.render_inner(token))

    def render_block_code(self, token):
        if (False):
            # ATTN: 2/2/25 this seems to cause problems with newspaper and or indented blocks
            self.packages['listings'] = []
            template = ('\n\\begin{{lstlisting}}[language={}]\n'
                        '{}'
                        '\\end{{lstlisting}}\n')
            inner = self.render_raw_text(token.children[0], False)
            retv = template.format(token.language, inner)
        else:
            # ATTN: we need to ESCAPE this text
            retv = self.render_raw_text(token.children[0], True)
        return retv

    def render_list(self, token):
        self.packages['listings'] = []
        template = '\\begin{{{tag}}}\n{inner}\\end{{{tag}}}\n'
        tag = 'enumerate' if token.start is not None else 'itemize'
        if (False):
            if (tag=='enumerate'):
                # ATTN: jr - bypass enumerated lists
                inner = self.render_inner(token)
                return inner
        inner = self.render_inner(token)
        return template.format(tag=tag, inner=inner)

    def render_list_item(self, token):
        inner = self.render_inner(token)
        # ATTN: jr - bypass enumerated lists
        if (False):
            leader = token.leader
            if (len(leader)>0) and (leader[0] in ['0','1','2','3','4','5','6','7','8','9']):
                return '\n' + leader + ' ' + inner.strip() + '\n'
        return '\\item {}\n'.format(inner)


    def render_table(self, token):
        def render_align(column_align):
            if column_align != [None]:
                cols = [get_align(col) for col in token.column_align]
                return '{{{}}}'.format(' '.join(cols))
            else:
                return ''

        def get_align(col):
            if col is None:
                return 'l'
            elif col == 0:
                return 'c'
            elif col == 1:
                return 'r'
            raise RuntimeError('Unrecognized align option: ' + col)

        template = ('\\begin{{tabular}}{align}\n'
                    '{inner}'
                    '\\end{{tabular}}\n')
        if hasattr(token, 'header'):
            head_template = '{inner}\\hline\n'
            head_inner = self.render_table_row(token.header)
            head_rendered = head_template.format(inner=head_inner)
        else:
            head_rendered = ''
        inner = self.render_inner(token)
        align = render_align(token.column_align)
        return template.format(inner=head_rendered + inner, align=align)

    def render_table_row(self, token):
        cells = [self.render(child) for child in token.children]
        return ' & '.join(cells) + ' \\\\\n'

    def render_table_cell(self, token):
        return self.render_inner(token)

    @staticmethod
    def render_thematic_break(token):
        #return '\\hrulefill\n'
        return '\n\\hrulefill\n'

    @staticmethod
    def render_line_break(token):
        return '\n' if token.soft else '\\newline\n'



    def render_document(self, token):
        # ATTN: jr - in hlparser we actually strip this out and replace it, so see there if you want to change the report options, etc.
        template = ('\\documentclass{{report}}\n'
                    '{packages}'
                    '\\begin{{document}}\n'
                    '{inner}'
                    '\\end{{document}}\n')
        self.footnotes.update(token.footnotes)
        return template.format(inner=self.render_inner(token),
                               packages=self.render_packages())

    @staticmethod
    def escape_url(raw: str) -> str:
        """
        Quote unsafe chars in urls & escape as needed for LaTeX's hyperref.

        %-escapes all characters that are neither in the unreserved chars
        ("always safe" as per RFC 2396 or RFC 3986) nor in the chars set
        '/#:()*?=%@+,&;'

        Subsequently, LaTeX-escapes '%' and '#' for hyperref's \\url{} to also
        work if used within macros like \\multicolumn. if \\url{} with urls
        containing '%' or '#' is used outside of multicolumn-macros, they work
        regardless of whether these characters are escaped, and the result
        remains the same (at least for pdflatex from TeX Live 2019).
        """
        quoted_url = quote(raw, safe='/#:()*?=%@+,&;')
        return quoted_url.replace('%', '\\%') \
                         .replace('#', '\\#')







    def render_packages(self):
        pattern = '\\usepackage{options}{{{package}}}\n'
        # ATTN: jr - latex choking on options because base class seems to build option strings with quotes because options passed as a list of strings and base class asks python to convert list to string, so instead we build it
        # return ''.join(pattern.format(options=options or '', package=package) for package, options in self.packages.items())
        #
        allPackageString = ''
        for k,v in self.packages.items():
            optionString = ','.join(v)
            if (optionString!=''):
                optionString = '[{}]'.format(optionString)
            allPackageString += pattern.format(package=k, options=optionString)
        return allPackageString




    def render_link(self, token):
        self.addPackageHyperref()

        # ATTN: jr - internal links should use \hyperlink 
        # we can test this by looking for a starting # or by absence of :
        if (':' not in token.target):
            # create label just as we would when making section to let the pylatex.Section function decide on the label for us

            # target and page number sty;e
            addPageNumberStyle = False
            target = token.target
            if (target.endswith('+p')):
                target = target[0:len(target)-2]
                addPageNumberStyle = 'onpage'
            if (target.endswith('+pp')):
                target = target[0:len(target)-3]
                addPageNumberStyle = 'inparen'
            if (target.endswith('+onpagelink')):
                target = target[0:len(target)-11]
                addPageNumberStyle = 'onpagelink'
            #
            pyl = pylatex.Section(target, numbering=False, label=True)
            targetLink = pyl.label.marker.dumps()

            # label
            label = self.render_inner(token)
            labelEscaped = pylatex.escape_latex(label)

            if (addPageNumberStyle == 'onpagelink'):
                #escapedLabel = pylatex.escape_latex(targetLink)
                # the problem is we need to NOESCAPE this page number part
                labelEscaped += ' on p.\\pageref*{{{target}}}'.format(target=targetLink)

            # create a hyper ref internal link to the section label
            if (False) and (addPageNumberStyle != 'onpagelink'):
                # using pylatex to generate hyperlink
                pyl = pylatex.Hyperref(targetLink, label)
                retv = pyl.dumps()
            else:
                # our own hand made way
                # OK THIS IS NOW WORKING FOR ALL CASES
                #retv = pylatex.NoEscape(r'\hyperref[' + targetLink + ']{' + labelEscaped + '}')
                targetLinkForHr = pylatex.escape_latex(targetLink)
                retv = '\\hyperref[' + targetLinkForHr + ']{' + labelEscaped + '}'

            # add page number?
            if (addPageNumberStyle == 'onpage'):
                escapedLabel = pylatex.escape_latex(targetLink)
                retv += ' on p.\\pageref*{{{target}}}'.format(target=escapedLabel)
            elif (addPageNumberStyle == 'inparen'):
                escapedLabel = pylatex.escape_latex(targetLink)
                retv += ' (p.\\pageref*{{{target}}})'.format(target=escapedLabel)


            # wrap in mono font?
            if (False):
                retv = '{\\fontfamily{\ttfamily}\\selectfont' + retv + '}'

            # return it
            return retv

        # fallback original link code
        template = '\\href{{{target}}}{{{inner}}}'
        #
        inner = self.render_inner(token)
        retv = template.format(target=self.escape_url(token.target), inner=inner)
        return retv


    def render_auto_link(self, token):
        self.packages['hyperref'] = ['colorlinks=true,linkcolor=blue,filecolor=magenta,urlcolor=cyan']
        return '\\url{{{}}}'.format(self.escape_url(token.target))



    def render_heading(self, token):
        # ATTN: jr - we want to add labels that we can jump to and list in TOC
        inner = self.render_inner(token)

        addToToc = False
        if (inner.endswith('*')):
            # dont add to toc
            inner = inner[0:len(inner)-1]
            addToToc = False
        elif (token.level<=2):
            addToToc = True
        #
        sectionText = inner

        # section header
        if token.level == 1:
            retv = '\n\\chapter*{{{}}}%\n\n'.format(inner)
            # we would like to make top sections in TOC but not links
            # see https://tex.stackexchange.com/questions/8351/what-do-makeatletter-and-makeatother-do
            # note we use origaddcontentsline here to avoid adding chapter hyperlinks to TOC
            if (addToToc):
                if (True):
                    # no page numbers custom 
                    # hours of experimentation to make this work
                    #retv += r'\addtocontents{toc}{\protect\contentsline {chapter}{\protect\\numberline{}' + sectionText + '}{}{}}'
                    retv += r'\addtocontents{toc}{\protect\contentsline {chapter}{\protect\numberline{}' + sectionText + '}{}{}}' + '\n'
                else:
                    retv += '\\origaddcontentsline{toc}{chapter}{\\protect\\numberline{}' + sectionText + '}\n'
        elif token.level == 1+1:
            retv = '\n\\section*{{{}}}%\n\n'.format(inner)
            # we would like to make top sections in TOC but not links
            # see https://tex.stackexchange.com/questions/8351/what-do-makeatletter-and-makeatother-do
            #retv += '\\addcontentsline{toc}{section}{\\protect\\numberline{}' + sectionText + '}\n'
            if (addToToc):
                retv += '\\addcontentsline{toc}{section}{~~' + sectionText + '}\n'
        elif (token.level == 2+1) and (False):
            retv = '\n\\subsection*{{{}}}%\n\n'.format(inner)
            retv += '\\addcontentsline{toc}{subsection}{\\protect\\numberline{}' + sectionText + '}\n'
        else:
            # this is just a bolded bit of text, not a proper section
            #retv = '\\textbf{{{}}}%\n\n'.format(inner)
            retv = '\n\\textbf{{{}}}%\n\n'.format(inner)
            #retv = '\n\\subsubsection{{{}}}'.format(inner)

        # add label that can be target of a hyperref
        if (token.level<=2):
            # should be a cleaner way to do this
            pyl = pylatex.Section(inner, numbering=False, label=True)
            retv += pyl.label.dumps()
        return retv


    def safelyResolveImageSource(self, filePath):
        # throw error if we can't resolve it to a known image
        filePathResolved = self.parserRef.safelyResolveImageSource(filePath)
        return filePathResolved



    def render_underline(self, token):
        inner = self.render_inner(token)
        return "\\underline{" + inner + "}"
