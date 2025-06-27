# replacement mistletoe html renderer to disable numbered list automatics

import mistletoe.latex_token as latex_token
from mistletoe.base_renderer import BaseRenderer
from mistletoe import HtmlRenderer


import html
from itertools import chain
from urllib.parse import quote
import re

from mistletoe import block_token
from mistletoe import span_token
from mistletoe.block_token import HtmlBlock
from mistletoe.span_token import HtmlSpan
from mistletoe.base_renderer import BaseRenderer

# for underline support
from mistletoe.span_token import SpanToken, add_token
from mistletoe import span_token



# adding support for underline
class MyUnderline(SpanToken):
    pattern = re.compile(r'__(.+?)__')  # Use re.compile to define the regex pattern
    parse_inner = True  # Allows parsing of nested elements
    parse_group = 1  # Specifies which regex group contains the content

    def __init__(self, match):
        pass
    @classmethod
    def read(cls, match):
        return cls(target=match.group(1))


# register globally (does not work, calling below)
add_token(MyUnderline)
    
    
    
class JrHtmlRenderer(HtmlRenderer):
#    def __init__(self, *extras, html_escape_double_quotes=False, html_escape_single_quotes=False, process_html_tokens=True, **kwargs):
#        super().__init__(chain((), extras), html_escape_double_quotes, html_escape_single_quotes, process_html_tokens, **kwargs)

    def __init__(self, *extras, **kwargs):
        super().__init__(*extras, **kwargs)
        # underline support
        # doesnt seem to do anything
        self.render_map["MyUnderline"] = self.render_underline
        # needed?
        #self.document.add_token(MyUnderline) 


    # block automatic list numbering
    def render_list(self, token: block_token.List) -> str:
        template = '<{tag}{attr}>\n{inner}\n</{tag}>'
        if token.start is not None:
            if (True):
                tag = 'ul'
                attr = ''
            else:
                tag = 'ol'
                attr = ' start="{}"'.format(token.start) if token.start != 1 else ''
        else:
            tag = 'ul'
            attr = ''
        self._suppress_ptag_stack.append(not token.loose)
        inner = '\n'.join([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        return template.format(tag=tag, attr=attr, inner=inner)



    # block automatic list numbering
    def render_list_item(self, token: block_token.ListItem) -> str:
        if len(token.children) == 0:
            return '<li></li>'

        didSetInner = False
        if (True):
            leader = token.leader
            if (len(leader)>0) and (leader[0] in ['0','1','2','3','4','5','6','7','8','9']):
                didSetInner = True
                inner = '\n'.join([self.render(child) for child in token.children])
                inner = inner.replace('<p>', '<p>{} '.format(leader))

        if (not didSetInner):
            inner = '\n'.join([self.render(child) for child in token.children])


        inner_template = '\n{}\n'
        if self._suppress_ptag_stack[-1]:
            if token.children[0].__class__.__name__ == 'Paragraph':
                inner_template = inner_template[1:]
            if token.children[-1].__class__.__name__ == 'Paragraph':
                inner_template = inner_template[:-1]
        return '<li>{}</li>'.format(inner_template.format(inner))
    




    # block automatic list numbering
    def render_link(self, token: span_token.Link) -> str:
        template = '<a href="{target}"{title}>{inner}</a>'

        target = token.target
        if (target.endswith('+p')):
            target = target[0:len(target)-2]
            addPageNumberStyle = 'onpage'
        elif (target.endswith('+onpagelink')):
            # ATTN: todo implement this i didnt bother for html
            target = target[0:len(target)-11]
            addPageNumberStyle = 'onpage'
        elif (target.endswith('+pp')):
            target = target[0:len(target)-3]
            addPageNumberStyle = 'inparen'

        target = self.escape_url(target)

        if token.title:
            title = ' title="{}"'.format(html.escape(token.title))
        else:
            title = ''
        inner = self.render_inner(token)
        return template.format(target=target, title=title, inner=inner)




    def render_heading(self, token: block_token.Heading) -> str:
        template = '<h{level}>{inner}</h{level}>'
        inner = self.render_inner(token)

        addToToc = False
        if (inner.endswith('*')):
            # dont add to toc
            inner = inner[0:len(inner)-1]
            addToToc = False
        elif (token.level<=2):
            addToToc = True

        return template.format(level=token.level, inner=inner)



    def render_underline(self, token):
        return f"<u>{self.render_inner(token)}</u>"


