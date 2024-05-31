# django
from django.utils import timezone
from django.contrib import messages
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.utils.safestring import mark_safe

# python modules
from datetime import datetime
import re
import uuid





def convertTimeStampToDateTimeDefaultNow(timeStamp):
    if (timeStamp is None):
        return timezone.now()
    return datetime.fromtimestamp(timeStamp)



def lookupDjangoChoiceLabel(enumKey, enumList):
    for enumItem in enumList:
        if (enumItem[0]==enumKey):
            return enumItem[1]
    # not found
    return enumKey






def addFlashMessage(request, str, flagIsError):
    if flagIsError or ("error" in str.lower()) or ("exception" in str.lower()):
        messages.add_message(request, messages.ERROR, str)
    else:
        messages.add_message(request, messages.INFO, str)


def addFlashMessages(request, strList):
    for str in strList:
        addFlashMessage(request, str, False)







# see https://djangosnippets.org/snippets/690/
def jrdUniquifySlug(instance, value, slug_field_name='slug', queryset=None, slug_separator='-'):
    # set object.slug to a unique slug value


    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """

    # ATTN: TODO
    # this is found code; one thing that seems bad about it is that it FORCES the slug to be changed to new value, even if it already has a unique one.. is this what we want?
    # put another way, say on our first save, we had a conflict, and so we assigned a -2 suffix.. later we resave and the conflict is gone, this will auto change our slug to the original tried value
    # but what if we dont WANT to change the slug once we've assigned it a valid unique value!

    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = jrd_slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len-len(end)]
            slug = jrd_slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def jrd_slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """

    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value








def shortUuidAsString():
    return str(uuid.uuid4())
def shortUuidAsStringWithPkPrefix():
    return "pk_" + str(uuid.uuid4())

def resolveSubDirName(subdirname, pk):
    if (subdirname.startswith("pk_")):
        # replace "pk_" with game.pk to make it easier to identify the directory
        subdirname=str(pk)+"-"+subdirname[3:]
    return subdirname




def validateName(value):
    regexValidName = re.compile(r'^[\w\-\_ ]+$')
    matches = regexValidName.match(value)
    if (matches is None):
        raise ValidationError("Can only contain letters, numbers, spaces, underscores, hyphens")





def jrPopoverLabels(model, field_strings):
    # see https://github.com/django-crispy-forms/django-crispy-forms/issues/389

    fields_html = {}
    for field_string in field_strings:
        try:
            field = model._meta.get_field(field_string)
        except FieldDoesNotExist:
            continue #if custom field we skip it

        html = field.verbose_name
        if(field.help_text != ""):
            # for icons see https://icons.getbootstrap.com/
            #html += '<a tabindex="0" role="button" data-toggle="popover" data-html="true" data-toggle="tooltip" data-trigger="hover" data-placement="auto" title="'+field.help_text+'">&nbsp;<i class="bi-info-circle" style="font-size: 0.75rem; color: cornflowerblue;"></i></a>'
            html += '<a tabindex="0" data-html="true" data-placement="auto" title="'+field.help_text+'">&nbsp;<i class="bi-info-circle" style="font-size: 0.75rem; color: cornflowerblue;"></i></a>'
            #html += '<button type="button" class="btn btn-secondary btn-xs" data-toggle="tooltip" data-placement="top" title="'+field.help_text+'" >?</button>'
        fields_html[field.name] = mark_safe(html)
    return fields_html


def jrBlankFields(model, field_strings):
    fields_text = {}
    for field_string in field_strings:
        try:
            field = model._meta.get_field(field_string)
        except FieldDoesNotExist:
            continue #if custom field we skip it

        fields_text[field.name] = ""
    return fields_text