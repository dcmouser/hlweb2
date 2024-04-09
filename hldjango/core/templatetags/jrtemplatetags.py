from django import template
from django.template.defaultfilters import stringfilter

import os


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

