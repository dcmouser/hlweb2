from django import template
from django.template.defaultfilters import stringfilter

# borrowed from active_links
from django import VERSION as DJANGO_VERSION
from django import template
from django.conf import settings
from django.urls import reverse, NoReverseMatch
from django.utils.encoding import escape_uri_path

# python modules
import os

from lib.jr import jrdfuncs


# register template tags / functions
register = template.Library()



@register.filter
@stringfilter
def isImageFilePath(filepath):
    """Return true if the path ends in image file extension; note that this is not meant to be secure its just to help decide whether to show an image on a client side page so there is no harm if it is wrong"""
    ext = os.path.splitext(filepath)[1]  # [0] returns path+filename
    imageFileExtensions = ['.png', '.jpg', '.jpeg', 'webp']
    if ext.lower() in imageFileExtensions:
        return True
    return False







# borrowed from active_links django 3rd party tool
@register.simple_tag(takes_context=True)
def jrActiveLink(context, viewnames, css_class=None, inactive_class='', strict=None, *args, **kwargs):
    """
    Renders the given CSS class if the request path matches the path of the view.
    :param context: The context where the tag was called. Used to access the request object.
    :param viewnames: The name of the view or views separated by || (include namespaces if any).
    :param css_class: The CSS class to render.
    :param inactive_class: The CSS class to render if the views is not active.
    :param strict: If True, the tag will perform an exact match with the request path.
    :return:
    """
    if css_class is None:
        css_class = getattr(settings, 'ACTIVE_LINK_CSS_CLASS', 'active')

    if strict is None:
        strict = getattr(settings, 'ACTIVE_LINK_STRICT', False)

    request = context.get('request')
    if request is None:
        # Can't work without the request object.
        return ''
    active = False
    views = viewnames.split('||')
    for viewname in views:
        try:
            path = reverse(viewname.strip(), args=args, kwargs=kwargs)
        except NoReverseMatch:
            continue
        request_path = escape_uri_path(request.path)
        if strict:
            active = request_path == path
        else:
            active = request_path.find(path) == 0
        if active:
            break

    if active:
        return css_class

    return inactive_class




# borrowed from active_links
@register.simple_tag(takes_context=True)
def jrActiveUrl(context, urlPartials, css_class=None, inactive_class='', strict=None, *args, **kwargs):
    """
    Renders the given CSS class if the request path matches the path of the view.
    :param context: The context where the tag was called. Used to access the request object.
    :param viewnames: The name of the view or views separated by || (include namespaces if any).
    :param css_class: The CSS class to render.
    :param inactive_class: The CSS class to render if the views is not active.
    :param strict: If True, the tag will perform an exact match with the request path.
    :return:
    """
    if css_class is None:
        css_class = getattr(settings, 'ACTIVE_LINK_CSS_CLASS', 'active')

    request = context.get('request')
    if request is None:
        # Can't work without the request object.
        return ''
    active = False
    urlPaths = urlPartials.split('||')
    for urlPart in urlPaths:
        request_path = escape_uri_path(request.path)
        active = (urlPart in request_path)
    if active:
        return css_class
    return inactive_class




@register.filter
def justfilename(value):
    return os.path.basename(value)

@register.filter
def userIsAuthenticatedAndGadmin(user):
    # Implement your logic here
    return jrdfuncs.userIsAuthenticatedAndGadmin(user)

