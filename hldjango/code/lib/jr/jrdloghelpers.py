import logging
import re
from lib.jr import jrfuncs




# ---------------------------------------------------------------------------
# use ipware more elaborate ip detection
optionUseIpWare = False

# kludge for grabbing ip from gunicorn log messages, etc.
ipStartOfStringPattern = re.compile(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})([\s\-]*)(.*)')
# helper for getting request path from combined log line
requestFromMessageLog = re.compile(r'^[^\]]*]\s*\"(?:GET|POST)\s*(\/[^\"]*)\s[^\s]*\"(?:.*)')
requestFromMessagePlain = re.compile(r'^\"(?:GET|POST)\s*(\/[^\"]*)\s[^\s]*\"(?:.*)')
#
# ignored patterns
ignorePathsApiGameModDate = re.compile(r'^\/games\/api\/game\/moddatebyid.*')
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
class JrAddClientIpFilter(logging.Filter):
    # this filter tries in various ways to get the correct IP of the client, which can be hidden in the record in various ways, especially when using a proxy helper for nginx, etc.
    def filter(self, record):
        record.ip = None
        if (not optionUseIpWare):
            self.filterSimple(record)
        else:
            self.filterUsingIpWare(record)

        if (record.ip is None):
            # we have to set it to something
            # for gunicorn logs, we dont seem to get request but the ip is at the head of the message
            # we can ask gunicorn to even included the forwarded ip from nginx which should be the secret sauce
            # (see wsgi_gunicorn_config_nginxhelper.py which sets access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
            recordip = self.parseIpFromFrontOfMessage(record, True)
            if (recordip is not None):
                # set it
                record.ip = recordip
            else:
                record.ip = "ipUnknown"
        #
        return True


    def filterSimple(self, record):
        #print("-----------------------------------\nIn filterSimple debugging..")
        #print("Record")
        #jrfuncs.print_serializable_attributes(record)
        if hasattr(record, 'request'):
            request = record.request
            #print("Rquest")
            #jrfuncs.print_serializable_attributes(request)
            if hasattr(request, 'META'):
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if (not x_forwarded_for):
                    # try this in case its case sensitive
                    x_forwarded_for = request.META.get('X-forwarded-for')
                    if (x_forwarded_for):
                        #print("ATTN: CASE SENSITIVE FORWARDED FOR WTF")
                        pass
                #
                if x_forwarded_for:
                    #print("ATTN: DEBUG got META FORWARDED FOR: {}.".format( x_forwarded_for))
                    record.ip = x_forwarded_for.split(',')[0]
                    return True
                else:
                    record.ip = request.META.get('REMOTE_ADDR')
                    #print("ATTN: DEBUG3 got META REMOTE_ADDR: {}.".format(record.ip))
                    return True
            else:
                #print("ATTN: DEBUG 5 no meta attr.")
                record.ip = self.parseIpFromSocketRequest(request)
                return True
        else:
            #print("ATTN: DEBUG 4 no request attr.")
            pass
        #
        return False


    def filterUsingIpWare(self, record):
        from ipware import get_client_ip
        if hasattr(record, 'request'):
            request = record.request
            if (not hasattr(request, 'META')):
                # this is a problem im not sure why its happening
                record.ip = self.parseIpFromSocketRequest(request)
                return True
            else:
                client_ip, is_routable = get_client_ip(request)
                if client_ip is not None:
                    # Store the IP on the request object
                    record.ip = str(client_ip)
                    return True
        return False


    def parseIpFromSocketRequest(self, request):
        # does this only happen on websocket local runserver servers?
        if (hasattr(request, 'getpeername')):
            try:
                client_ip = request.getpeername()[0]
                return client_ip
            except Exception as e:
                pass
        return None


    def parseIpFromFrontOfMessage(self, record, optionRemoveIp):
        ip = None
        message = getRecordMessage(record)
        if (message is not None):
            match = ipStartOfStringPattern.match(message)
            if (match is not None):
                ip = match.group(1)
                if (optionRemoveIp):
                    # REMOVE ip and set back message; NOTE: it's very important that when we SET the record.msg to something new, that we CLEAR the .args of the message or we may get exception on future getMessage()
                    message = match.group(3)
                    # SET IT safely using my new helper function
                    setRecordMessaege(record, message)
        #
        return ip
# ---------------------------------------------------------------------------








# ---------------------------------------------------------------------------
# reject requests we dont care about
class jrRejectIgnorableRequestsFilter(logging.Filter):
    def filter(self, record):
        reqPath = getRequestPathFromRecord(record)
        if (reqPath is None):
            # no path could be found, just return true
            return True

        # ok let's test path for stuff we want to ignore
        # see also nginx_config.conf for regex to ignore
        if (ignorePathsApiGameModDate.match(reqPath)):
            # ignore it
            return False

        # don't ignore it
        return True
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
# KLUDGE WORKAROUND should no longer be needed as of 3/5/25
# ok here's the idea:  For some reason gunicorn log records are coming in and they are having their record message ARGS trying to be replaced twice
# this results in exceptions being thrown when we try to log them if there is a % in the request; i can't find any solution to this though this is closest to describing the problem: https://stackoverflow.com/questions/47694878/gunicorn-access-log-format
# my kludge fix is to add a filter to logging requests that checks if the message starts with '[' which will be true when gunicorn messages have had their args replaced
# in this case i CLEAR the args field of the record, which results in glogging.py not trying to resolve them again
# hit this url to test: https://nynoir.org/cgi-bin/luci/%3Bstok%3D/locale
# ATTN: 3/5/25 - i just realized that I was to blame for needing this kludge, because my other code was setting record .msg directly to a modified value of getMessage() which resulted in double evaluation of the record message on subsequent getMessage()
# this problem all goes away if i use my own setRecordMessage() helper function and clear args to None after modifying .msg
# SO this should no longer be needed
class jrProcessGunicornFilterKludgeFixMessage(logging.Filter):
    def filter(self, record):
        # ATTN: UNFINISHED
        # SEE https://stackoverflow.com/questions/47694878/gunicorn-access-log-format
        # this is an attempt to fix gunicorn logging errors
        # i think the problem is the log is already formatted, so we get around this by CLEARING args so that python logging does not try to replace it again
        #print("ATTN: DEBUG from jrProcessGunicornFilterRealUnicorn: '{}'.".format(record.msg[0:30]))
        if (record.msg.startswith("%({X-Forwarded-For}i)s")):
            # not yet resolved, so resolve it ONCE
            #print("Resolving once")
            messageResolved = record.getMessage()
            # now force it to the RESOLVED version so it wont have to resolve again
            setRecordMessaege(record, messageResolved)
        # keep it
        return True
# ---------------------------------------------------------------------------















    






# ---------------------------------------------------------------------------
def getRecordMessage(record):
    if (True):
        return record.getMessage()
    else:
        # old workaround that i needed because i failed to understand reprecussions of setting .msg directly elsewhere
        try:
            message = record.getMessage()
        except Exception as e:
            # we were seeing an odd ValueError: unsupported format character 'A' (0x41) at index 38, so we'll just return NONE in this case
            try:
                # lets try to get it explicitly
                message = record.msg
            except Exception as e2:
                return None
        return message


def setRecordMessaege(record, message):
    # helper function to set message -- its very important we set message this way otherwise we get exceptions on a future getMessage
    record.msg = message
    # this is key -- otherwise it will try to REEXPAND the message, and cause exceptions complaining about not-understood formatter characters
    record.args = None



def getRequestPathFromRecord(record):
    reqPath = None
    if hasattr(record, 'request'):
        request = record.request
        if (request is not None) and (hasattr(request, 'path')):
            reqPath = request.path
    if (reqPath is None):
        # just get the message and strip off the request
        reqPath = getRequestFromLogRecordMessage(record)
    return reqPath



def getRequestFromLogRecordMessage(record):
    message = getRecordMessage(record)
    if (message is None):
        return None
    match = requestFromMessageLog.match(message)
    if (match is not None):
        return match.group(1)
    match = requestFromMessagePlain.match(message)
    if (match is not None):
        return match.group(1)
    return None
# ---------------------------------------------------------------------------
