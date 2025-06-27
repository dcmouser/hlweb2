# represents a virtual finger

import random
import hashlib



class VirtualFinger:
    # a virtual finger consists of a unique id, a clean (rolled) image, one or more noisy images, and other properties, especially the fingerprint CLASS
    def __init__(self, fingerId, fingerProps, person):
        self.fingerUniqueId = fingerId
        self.props = fingerProps
        self.caption = None
        self.ucaption = ""
        self.person = person
        #
        self.impressions = {}

    def getFingerProps(self):
        return self.props
    def getFingerPropClassType(self):
        return self.props["type"]
    def getImpressionByIndex(self, impressionIndex):
        return self.impressions[str(impressionIndex)]

    def getFingerId(self):
        return self.fingerUniqueId
    def setCaption(self, caption):
        self.caption = caption
    def getCaption(self):
        return self.caption

    def getPlayerCaption(self):
        if (not self.getIsAnonymous()):
            return self.getCaption()
        # ATTN: it might be nice to return a unique id like FingerNumberPersonNumber obfuscated, just to help give unique print ids of the form like "UNK343"
        # we could generate this by using a fixed random table that maps finger#1-10 and person#1-50 to a number in range 000-999
        optionUseUniqueUnkownCaptions = True
        if (optionUseUniqueUnkownCaptions):
            return self.getUCaption()
            #return self.getUniqueUnknownCaption()
        else:
            return "UNKNOWN"

    def getPlayerCaptionPlus(self):
        # combine real ID and UNK
        caption = self.getPlayerCaption()
        if self.getIsAnonymous():
            caption = self.getCaption() + " (" + caption + ")"
        return caption


    def getUCaption(self):
        return self.ucaption

    def clearUcaption(self):
        self.ucaption = ""

    def setCalcUcaption(self, person, fingerId):
        # first get anonymous person number
        personDname = person.getDname()
        # we expect this to be "AP##"
        if (not personDname.startswith("AP")):
            raise Exception("Unexpected person dname in getUniqueUnknownCaption for virtualfinger")
        personDnameNumber = int(personDname[2:])+1
        # now unique finger number
        indexInRange = (personDnameNumber * 10) + (fingerId)
        uniqueUnkId = generateObfuscatedUnk(indexInRange)
        self.ucaption = uniqueUnkId


    def getIsAnonymous(self):
        return self.person.getIsAnonymous()
    
    def addImpression(self, impressionId, filePath):
        self.impressions[impressionId] = {"path": filePath}


    def serializeData(self):
        data = {"fingerUniqueId": self.fingerUniqueId, "props": self.props, "caption": self.caption, "ucaption": self.ucaption, "impressions": self.impressions}
        return data

    @staticmethod
    def unSerializeData(fingerId, data, person):
        # unserialize person data
        props = data["props"]
        fingerUniqueId = data["fingerUniqueId"]
        finger = VirtualFinger(fingerUniqueId, props, person)
        finger.impressions = data["impressions"]
        finger.caption = data["caption"]
        finger.ucaption = data["ucaption"]
        return finger


    def findImpressionByKey(self, impressionKey):
        if (impressionKey in self.impressions):
            return self.impressions[impressionKey]
        # not found
        return None














class VirtualFingerManager:
    def __init__(self):
        self.fingers = {}

    def storeFingerprintImageFile(self, fingerUniqueId, impressionId, filePath, fingerProps):
        # create dictionary entry if not found already
        if (fingerUniqueId not in self.fingers):
            # add it
            finger = VirtualFinger(fingerUniqueId, fingerProps, None)
            self.fingers[fingerUniqueId] = finger
        else:
            finger = self.fingers[fingerUniqueId]
            # sanity check
            if (True):
                props = self.fingers[fingerUniqueId].getFingerProps()
                if (props["type"] != fingerProps["type"]):
                    raise Exception ("Mismatch in finger props type {} vs {}.".format(props["type"], fingerProps["type"]))
        # add impression to finger
        finger.addImpression(impressionId, filePath)


    def buildClassFingerDict(self):
        # build hierarchical dict of fingers
        fingerClassDicts = {}
        # walk fingers
        for fingerId,finger in self.fingers.items():
            classType = finger.getFingerPropClassType()
            if (classType not in fingerClassDicts):
                fingerClassDicts[classType] = [ finger ]
            else:
                fingerClassDicts[classType].append(finger)
        return fingerClassDicts






# ---------------------------------------------------------------------------
unkList = None
def generateObfuscatedUnk(index):
    global unkList
    if (unkList is None):
        # initialize it
        unkList = []
        for i in range(1,1000):
            unkid = str(i).zfill(3)
            unkList.append(unkid)
        # repeatable shuffle
        repeatable_shuffle(unkList, "randUnkKey1234")
    # now get by index
    return "UNK" + unkList[index]


def repeatable_shuffle(lst, key):
    """
    Returns a new list with the elements of `lst` shuffled using a deterministic key.
    """
    # Convert key to a seedable integer via SHA256 (ensures consistent behavior)
    if isinstance(key, str):
        key_bytes = key.encode('utf-8')
        seed = int(hashlib.sha256(key_bytes).hexdigest(), 16)
    elif isinstance(key, int):
        seed = key
    else:
        raise TypeError("Key must be str or int")

    rng = random.Random(seed)
    rng.shuffle(lst)
# ---------------------------------------------------------------------------
