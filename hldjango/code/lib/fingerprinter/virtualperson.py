# represents a virtual person

from .virtualfinger import VirtualFingerManager, VirtualFinger

from lib.jr import jrfuncs



class VirtualPerson:
    # A virtual person is a dictionary of virtual fingers, plus an id
    def __init__(self, personId, leadId, dName, pcat):
        self.uniqueId = str(personId)
        self.leadId = leadId
        self.dName = dName
        self.pcat = pcat
        self.fingers = {}

    def assignFinger(self, fingerNum, finger):
        self.fingers[fingerNum] = finger
    
    def getFingers(self):
        return self.fingers
    def getUniqueId(self):
        return self.uniqueId
    def getLeadId(self):
        return self.leadId
    def getCaption(self):
        return self.getLeadId()
    def getPlayerCaption(self):
        if (not self.getIsAnonymous()):
            return self.getLeadId()
        return "UNKNOWN"

    def getDname(self):
        return self.dName


    def serializeData(self):
        data = {"uniqueId": self.uniqueId, "leadId": self.leadId, "dName": self.dName, "pcat": self.pcat}
        data["fingerData"] = {}
        for fingerId, finger in self.fingers.items():
            data["fingerData"][fingerId] = finger.serializeData()
        return data

    def getIsAnonymous(self):
        if (self.dName.startswith("A")):
            return True
        return False

    def setFingerCaptions(self):
        person = self
        isPersonUnknown = person.getIsAnonymous()
        for fingerId, finger in person.getFingers().items():
            fingerType = finger.getFingerPropClassType()
            finger.setCaption(person.getCaption())
            if (isPersonUnknown):
                finger.setCalcUcaption(person, fingerId)
            else:
                finger.clearUcaption()


    @staticmethod
    def unSerializeData(data, personId):
        # unserialize person data
        uniqueId = data["uniqueId"]
        leadId = data["leadId"]
        dName = data["dName"]
        pcat = data["pcat"]
        person = VirtualPerson(personId, leadId, dName, pcat)
        person.uniqueId = uniqueId
        # now fingers..
        fingersData = data["fingerData"]
        person.fingers = {}
        for fingerId, fingerData in fingersData.items():
            person.fingers[int(fingerId)] = VirtualFinger.unSerializeData(fingerId, fingerData, person)
        return person


    def findFingerById(self, fingerId):
        # convert L1,L2...R5 to a finger Key(0-9)
        fingerIdMap = {
            "L1": 0,
            "L2": 1,
            "L3": 2,
            "L4": 3,
            "L5": 4,
            "R1": 5,
            "R2": 6,
            "R3": 7,
            "R4": 8,
            "R5": 9,
        }
        if (fingerId not in fingerIdMap):
            return None
        fingerKey = fingerIdMap[fingerId]
        if (fingerKey in self.fingers):
            return self.fingers[fingerKey]
        # not found
        return None






class VirtualPersonManager:
    def __init__(self):
        self.persons = {}

    def addPerson(self, person, personId):
        self.persons[personId] = person

    def getPersons(self):
        return self.persons

    def buildAndOwnUsedFingersMatchingClassType(self, classTypeString):
        # walk all people, own the fingers and build a list of them
        fingers = []
        for personId, person in self.persons.items():
            isPersonUnknown = person.getIsAnonymous()
            for fingerId, finger in person.getFingers().items():
                fingerType = finger.getFingerPropClassType()
                if (fingerType == classTypeString):
                    # got one
                    # own it (set caption for it)
                    finger.setCaption(person.getCaption())
                    # add it
                    fingers.append(finger)
        return fingers


    def sortByLeadId(self):
        sorted_data = sorted(self.persons.items(), key=lambda x: x[1].getLeadId())
        sortedDict = dict(sorted_data)
        self.persons = sortedDict



    def serializeData(self):
        data = {}
        for personId, person in self.persons.items():
            person.setFingerCaptions()
            data[personId] = person.serializeData()
        return data

    def unSerializeData(self, data):
        self.persons = {}
        for personId, personData in data.items():
            person = VirtualPerson.unSerializeData(personData, personId)
            self.persons[personId] = person








    def findPersonByLeadId(self, leadId):
        for personId, person in self.persons.items():
            if (person.getLeadId() == leadId):
                return person
        # not found
        return None



    def checkForProblems(self):
        # sanity check unique ucaptions
        ucaptions = []
        for personId, person in self.persons.items():
            for fingerId, finger in person.getFingers().items():
                ucaption = finger.getUCaption()
                if (ucaption==""):
                    continue
                if (ucaption in ucaptions):
                    raise Exception("Found duplicate ucaption: {}.".format(ucaption))
                ucaptions.append(ucaption)
        # all good