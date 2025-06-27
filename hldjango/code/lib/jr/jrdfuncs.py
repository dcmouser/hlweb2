# django
from django.utils import timezone
from django.contrib import messages
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.utils.safestring import mark_safe
from django.conf import settings
from django.http import StreamingHttpResponse
import django


# my modules
from lib.jr import jrfuncs, jrdfuncs
from lib.jr.jrfuncs import jrprint, setLogFileAnnounceString

# python modules
from datetime import datetime
import re
import uuid
import logging




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


def jrd_slug_strip(value, divider='-'):
    """
    Cleans up a slug by removing slug divider characters that occur at the
    beginning or end of a slug.

    If an alternate divider is used, it will also replace any instances of
    the default '-' divider with the new divider.
    """

    divider = divider or ''
    if divider == '-' or not divider:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(divider)
    # Remove multiple instances and if an alternate divider is provided,
    # replace the default '-' divider.
    if divider != re_sep:
        value = re.sub('%s+' % re_sep, divider, value)
    # Remove divider from the beginning and end of the slug.
    if divider:
        if divider != '-':
            re_sep = re.escape(divider)
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




# ATTN: THIS IS NOT CALLED ON MY NORMAL TEST LOCAL SERVER STARTUP
def announceDjangoAndSettingsVersion(buildStr):
    now = datetime.now().strftime("%B %d, %Y - %X")
    version = django.get_version()

    if (settings.DEBUG):
        version += " (DEBUG)"

    msg = f"Starting up Django version {version}, using settings {settings.SETTINGS_MODULE!r}" + "; " + buildStr
    msg = f"{now}" + "\n" + msg
    jrfuncs.setLogFileAnnounceString(msg)
    # log
    logger = logging.getLogger("app")
    logger.info(msg)







# ---------------------------------------------------------------------------
def addUserToGroups(user, groupNameList):
    try:
        from django.contrib.auth.models import Group
        for groupName in groupNameList:
            group = Group.objects.get(name=groupName)
            user.groups.add(group)
        user.save()
    except Exception as e:
        print("Error adding user to groups ({}); Exception:".format(groupNameList))
        print(e)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def createDjangoGroupAndPermission(permissionCodename, permissionLabel, groupName, contentModel):
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType

    # create group
    print("hlweb Checking for custom Django group {} with permission {} ({})..".format(groupName, permissionCodename, permissionLabel))
    group, created = Group.objects.get_or_create(name=groupName)
    if (created or True):
        # we now do this even if it wasnt just created, in case this code changes
        # authoring permission for games
        try:
            # create permission
            permission = Permission.objects.create(
                codename=permissionCodename,
                name=permissionLabel,
                content_type = ContentType.objects.get_for_model(contentModel),
            )
        except:
            print(" * Permission {} ({}) already exists; does not need to be added".format(permissionCodename, permissionLabel))
            permission = Permission.objects.get(codename=permissionCodename)
        # now give the author permission to the authorGroup
        if permission in group.permissions.all():
            print(" * Permission {} ({}) already assigned to group {}; does not need to be added.".format(permissionCodename, permissionLabel, groupName))
        else:
            group.permissions.add(permission)
            print(" * Added permission {} ({}) to group {}.".format(permissionCodename, permissionLabel, groupName))
    else:
        print(" * Group {} already exists: Leaving as is; assuming that permission {} ({}) has ALREADY been assigned".format(groupName, permissionCodename, permissionLabel))
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
def requestUserIsAuthenticatedAndGadmin(request):
    return userIsAuthenticatedAndGadmin(request.user)

def userIsAuthenticatedAndGadmin(user):
    return (user.is_authenticated) and (user.get_is_gadmin())


def userOwnsObjectOrStrongerPermission(obj, user):
    # ATTN: should we be testing pk instead?
    if (not user.is_authenticated):
        return False
    if (obj.owner.pk == user.pk):
        return True
    if (jrdfuncs.userIsAuthenticatedAndGadmin(user)):
        return True

    # ATTN: new 12/30/24
    if (user in obj.editors.all()):
        return True

    return False
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
def streamFileRequest(path, contentType):
    chunk_size=8192
    # Generator function that reads the file in small chunks
    def file_iterator(file_name, chunk_size=8192):
        with open(file_name, 'rb') as file:
            while True:
                data = file.read(chunk_size)
                if not data:
                    break
                yield data

    # Streaming the file
    response = StreamingHttpResponse(file_iterator(path))
    if (contentType == "attachment"):
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(path.split('/')[-1])
    else:
        response['Content-Type'] = contentType
    return response



def streamFileTailRequest(path, lineCount=10):
    #lines = fileTailLines(path, lineCount)
    # build first line info
    currentDateString = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #fileModString = jrfuncs.calcModificationDateOfFileAsNiceString(path)
    oldness = jrfuncs.calcHowLongAgoFileModifiedAsNiceString(path)
    firstLine = "Tailing file {} at {} (last modified {} ago):\n\n".format(path, currentDateString, oldness)
    lines = fileTailLines2(path, lineCount)
    # Create a generator that yields each line as bytes
    def generate():
        yield firstLine
        lineIndex = 0
        for line in lines:
            lineIndex += 1
            if (lineIndex==lineCount):
                yield "...\n"
                continue
            elif (lineIndex>lineCount):
                break
            #yield line.encode('utf-8') + b'\n'
            yield line.encode('utf-8')
    # Return a streaming response
    response = StreamingHttpResponse(generate(), content_type="text/plain")
    return response



# thanks to chatgpt
def fileTailLines(filename, lineCount):
    with open(filename, 'r', encoding='utf-8') as file:
        # Move to the end of the file
        file.seek(0, 2)
        end_position = file.tell()
        buffer_size = 1024
        block = -1
        lines_to_go = lineCount
        block_end = end_position
        lines = []

        while lines_to_go > 0 and block_end > 0:
            if (block_end - buffer_size > 0):
                # Move the pointer back a block size
                file.seek(block * buffer_size, 2)
                block_data = file.read(buffer_size)
            else:
                # Move to the beginning of the file
                file.seek(0,0)
                block_data = file.read(block_end)

            # Add the data from the block to our lines array
            lines.extend(block_data.splitlines())

            # Update the count of lines still to go
            lines_to_go -= block_data.count('\n')
            block -= 1
            block_end = file.tell()

        # We may have read more lines than needed, trim the list
        return lines[-lineCount:][::-1]
    return None



# see https://stackoverflow.com/questions/12523044/how-can-i-tail-a-log-file-in-python
def fileTailLines2(path, lineCount):
    batch_size=1024
    keepends=True
    encoding = 'utf-8'

    bytesio = open(path, 'rb')

    bytesio.seek(0, 2)
    end = bytesio.tell()

    buf = b""
    for p in reversed(range(0, end, batch_size)):
        bytesio.seek(p)
        lines = []
        remain = min(end-p, batch_size)
        while remain > 0:
            line = bytesio.readline()[:remain]
            lines.append(line)
            remain -= len(line)

        cut, *parsed = lines
        for line in reversed(parsed):
            if buf:
                line += buf
                buf = b""
            if encoding:
                line = line.decode(encoding)
            yield from reversed(line.splitlines(keepends))
        buf = cut + buf
    
    if path:
        bytesio.close()

    if encoding:
        buf = buf.decode(encoding)

    yield from reversed(buf.splitlines(keepends))
# ---------------------------------------------------------------------------
