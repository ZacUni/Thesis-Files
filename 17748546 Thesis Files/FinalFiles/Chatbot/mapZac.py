from common import getType, getReduced, socialStoryDic, reducedList, getSynonymAIPOV, standardise
from ai import *
from grammarManager import GrammarManager
from grammarToMap import GrammarToMap
import numpy as np
import nltk

class Summit(object):
    def __init__(self, attributes = {}):
        self.attributes = attributes
        self.distance = None
        self.isNew = True

    def __lt__(self, other):
        return self.distance < other.distance

    def __gt__(self, other):
        return self.distance > other.distance

    def __str__(self):
        print("attributes", self.attributes)
        return ""

class Map(object):
    def __init__(self):
        self.summits = []
        self.questions = {
            'person': [{"searchKey": "relationship", "questionBuildWords": {"interrogative": "who", "verb": "is", "sbj": "/", "answerExamples": "your mother? your friend?"}}],
            'activity': ['likePlace'],
            'place': ['which color is'],
            'family': ['mother'],
            'city': ['likeCity'],
            'room': ['likeRoom'],
            'friendGroup': ['friends']
            }
        self.csgd = {}
        self.socialStorySummits = {}

    def __str__(self):
        for summit in self.summits:
            print(summit)
        print(self.csgd)
        return ""

class MapManager(object):
    def __init__(self, preMap = False):
        self.map = Map()
        self.previousSummit = None
        self.currentSummit = None
        self.question = None
        self.formulDic = None
        self.searchKey = None
        self.nextId = 0
        self.nextCsi = 0
        self.ssName = None
        self.predecessor = None
        self.priorityQueue = None
        self.newQuestionFound = False
        self.prevCsg = None
        self.priming = False
        if preMap:
            self.preMap()

    def preMap(self):
        s0 = Summit({"id": ["0"], "type": ["universe"], "adjList": [{"destId": "1", "hierar": "destLower"}]})
        s1 = Summit({"id": ["1"], "type": ["galaxy"], "adjList": [{"destId": "2", "hierar": "destLower"}, {"destId": "1", "hierar": "destHigher"}]})
        s2 = Summit({"id": ["2"], "type": ["solar system"], "adjList": [{"destId": "3", "hierar": "destLower"}, {"destId": "4", "hierar": "destLower"}, {"destId": "2", "hierar": "destHigher"}]})
        s3 = Summit({"id": ["3"], "type": ["earth"], "adjList": [{"destId": "5", "hierar": "destLower"}, {"destId": "6", "hierar": "destLower"}, {"destId": "2", "hierar": "destHigher"}]})
        s4 = Summit({"id": ["4"], "type": ["sun"], "adjList": [{"destId": "2", "hierar": "destHigher"}]})
        s5 = Summit({"id": ["5"], "type": ["oceania"], "adjList": [{"destId": "7", "hierar": "destLower"}, {"destId": "3", "hierar": "destHigher"}]})
        s6 = Summit({"id": ["6"], "type": ["europe"], "adjList": [{"destId": "3", "hierar": "destHigher"}]})
        s7 = Summit({"id": ["7"], "type": ["australia"], "adjList": [{"destId": "8", "hierar": "destLower"}, {"destId": "5", "hierar": "destHigher"}]})
        s8 = Summit({"id": ["8"], "type": ["perth"], "adjList": [{"destId": "7", "hierar": "destHigher"}]})

        self.addSummit(s0)
        self.addSummit(s1)
        self.addSummit(s2)
        self.addSummit(s3)
        self.addSummit(s4)
        self.addSummit(s5)
        self.addSummit(s6)
        self.addSummit(s7)
        self.addSummit(s8)

        self.nextId = 9
        
    def relax(self, sA, sB):
        try:
            defaultDistance = 1.0
            if sB.distance > sA.distance + defaultDistance:
                sB.distance = sA.distance + defaultDistance
                self.predecessor[sB.attributes["id"][0]] = sA.attributes["id"][0]
        except Exception:
            pass

    def getPredecessor(self):
        #Dijkstra Algorithm
        inf = 50
        self.predecessor = {}
        self.priorityQueue = []

        for summitId in range(self.nextId):
            s = self.getSummit(str(summitId))
            valid = True
            try:
                if s.attributes["stem"][0] in ["be", "have"]:
                    valid = False
            except Exception:
                pass
            if valid:
                s.distance = inf
                self.priorityQueue += [s]
        self.currentSummit.distance = 0.0

        while len(self.priorityQueue) > 0:
            active = min(self.priorityQueue)
            self.priorityQueue.remove(active)
            for elem in active.attributes["adjList"]:
                s = self.getSummit(elem["destId"])
                self.relax(active, s)

    def entityAlreadyExists(self, entity, entityKey = None):
        out = False
        undeterminedSubject = ["he", "she", "it", "we", "they"]
        undeterminedObject = ["him", "her", "it", "us", "them"]
        if entity in undeterminedObject + undeterminedSubject:
            try:
                self.prevCsg[entityKey]
                out = True
            except Exception:
                pass
        else:
            idList = [s.attributes['id'][0] for s in self.map.summits]
            synList = []
            for s in self.map.summits:
                try:
                    synList += s.attributes['synonym']
                except Exception:
                    pass
                try:
                    synList += s.attributes['synonymContingent']
                except Exception:
                    pass
            if entity in idList + synList:
                out = True
        return out

    def getSummit(self, entity, entityKey = None):
        undeterminedSubject = ["he", "she", "it", "we", "they"]
        undeterminedObject = ["him", "her", "it", "us", "them"]
        if entity in undeterminedObject + undeterminedSubject:
            try:
                s = self.getSummit(self.prevCsg[entityKey])
            except Exception:
                pass
        else:
            keepOn = True
            i = 0
            try:
                while keepOn:
                    s = self.map.summits[i]
                    try:
                        tmp = s.attributes['id'] + s.attributes['synonym']
                    except Exception:
                        tmp = s.attributes['id']
                    try:
                        tmp += s.attributes['synonymContingent']
                    except Exception:
                        pass
                    if entity in tmp:
                        keepOn = False
                    else:
                        i += 1
            except Exception:
                print("entity: ", entity, ": No Summit Found")
                s = None
        return s

    def addSummit(self, summit):
        self.map.summits += [summit]

    def getSocialStory(self, reduced):
        keepOn = True
        i = 0
        while keepOn:
            try:
                ssName = list(socialStoryDic.keys())[i]
                if reduced in socialStoryDic[ssName]["topics"]:
                    keepOn = False
                i += 1
            except Exception:
                keepOn = False
                ssName = None
        return ssName

    def checkSocialStoryLinks(self, summit):
        reducedEntity = []
        try:
            reducedEntity += summit.attributes["reduced"]
        except Exception:
            pass
        try:
            reducedEntity += summit.attributes["stem"]
        except Exception:
            pass
        for reduced in reducedEntity:
            if reduced in reducedList:
                ssName = self.getSocialStory(reduced)
                if ssName != None:
                    try:
                        self.map.socialStorySummits[summit.attributes["id"][0]] += [ssName]
                    except Exception:
                        self.map.socialStorySummits[summit.attributes["id"][0]] = [ssName]


    def setSummit(self, entityKey, entity):
        entityType = getType(entityKey, entity)
        entityId = self.nextId
        self.nextId += 1
        synonymAIPOV = getSynonymAIPOV(entityKey, entity)
        synonym = entity
        reduced = getSynonymAIPOV(entityKey, getReduced(entity))
        if entityKey in ["subject", "do"]:
            attributes = {'id': [str(entityId)], 'type': [entityType], 'synonym': [synonym], 'synonymAIPOV': [synonymAIPOV], 'reduced': [reduced]}
        else:
            synonymContingent = synonym
            synAIPOVContingent = synonymAIPOV
            synonym = standardise(synonymContingent)
            synonymAIPOV = standardise(synAIPOVContingent)
            attributes = {'id': [str(entityId)], 'type': [entityType], 'synonym': [synonym], 'synonymAIPOV': [synonymAIPOV], 'reduced': [reduced]}
            attributes['synonymContingent'] = [synonymContingent]
            attributes['synAIPOVContingent'] = [synAIPOVContingent]
        if entityType == "verb":
            try:
                stem = GrammarManager().stem(entity)
                attributes["stem"] = [stem]
            except Exception:
                print("stem failure")
        s = Summit()
        s.attributes = attributes
        self.checkSocialStoryLinks(s)
        self.addSummit(s)
        return s

    def grammarToSummit(self, grammAnalysis):
        self.activeSummits = {}
        self.csg = {}
        for entityKey in grammAnalysis.keys():
            entity = grammAnalysis[entityKey]
            ###
            if entity == "sa":
                self.stateVerbOn = True
            if entity == "do":
                self.stateVerbOn = False
            ###
            if self.entityAlreadyExists(entity, entityKey):
                s = self.getSummit(entity, entityKey)
            else:
                s = self.setSummit(entityKey, entity)
            self.activeSummits[entityKey] = s
            self.csg[entityKey] = s.attributes['id'][0]

    def csgAlreadyExists(self):
        out = False
        if self.csg in list(self.map.csgd.values()):
            out = True
        return out

    def setLinks(self):
        entityKeys = list(self.activeSummits.keys())
        for i in range(len(entityKeys) - 1):
            for j in range(i + 1, len(entityKeys)):
                entityKey1 = entityKeys[i]
                entityKey2 = entityKeys[j]
                s1 = self.activeSummits[entityKey1]
                s2 = self.activeSummits[entityKey2]
                tmpDic1 = {"destId": s2.attributes["id"][0], "csi": self.csi}
                tmpDic2 = {"destId": s1.attributes["id"][0], "csi": self.csi}
                ###
                """
                if entityKey1 == "subject" and entityKey2 == "sa":
                    tmpDic1["themeHierar"] = "destHigher"
                    tmpDic2["themeHierar"] = "destLower"
                if entityKey1 == "subject" and entityKey2 == "where" and self.stateVerbOn:
                    tmpDic1["structHierar"] = "destHigher"
                    tmpDic2["structHierar"] = "destLower"
                """
                ###
                try:
                    s1.attributes["adjList"] += [tmpDic1]
                except Exception:
                    s1.attributes["adjList"] = [tmpDic1]
                try:
                    s2.attributes["adjList"] += [tmpDic2]
                except Exception:
                    s2.attributes["adjList"] = [tmpDic2]

    def updateMap(self):
        if self.csgAlreadyExists() == False:
            self.csi = self.nextCsi
            self.nextCsi += 1
            self.map.csgd[self.csi] = self.csg
            self.setLinks()

    def setCurrentSummit(self):
        if (self.currentSummit in self.activeSummits.values()) == False:
            keepOn = True
            while keepOn:
                entityKeys = list(self.activeSummits.keys())
                r = np.random.randint(len(entityKeys))
                randKey = entityKeys[r]
                #if randKey != "verb":
                self.currentSummit = self.activeSummits[randKey]
                keepOn = False

    def getPath(self, finalDestId):
        print("destination: ",finalDestId)
        path = [finalDestId]
        currentId = finalDestId
        keepOn = True
        while keepOn:
            try:
                predId = self.predecessor[currentId]
                if predId != self.currentSummit.attributes["id"][0]:
                    path += [predId]
                    currentId = predId
                else:
                    keepOn = False
            except Exception:
                print("Sounds like there is no predecessor for summit id: ", currentId)
                keepOn = False
                path = None
        return path

    def goToNeighbour(self):
        self.getPredecessor()
        ssSummitId = np.random.choice(list(self.map.socialStorySummits.keys()))
        path = self.getPath(ssSummitId)
        if path:
            print("path found, path: ", path)
            destId = path[-1]
            self.previousSummit = self.currentSummit
            self.currentSummit = self.getSummit(destId)
        else:
            print("no path found")
            notPrevious = False
            while notPrevious == False:
                dest = np.random.choice(self.currentSummit.attributes["adjList"])
                try:
                    notPrevious = (dest["destId"] != self.currentSummit.attributes["id"][0])
                except Exception:
                    notPrevious = True
            self.previousSummit = self.currentSummit
            self.currentSummit = self.getSummit(dest["destId"])
    """
    def typeQuestion(self):
        currentType = self.currentSummit.attributes['type'][0]
        i = 0
        keepOn = True
        anyQuestion = False
        while keepOn:
            try:
                searchKey = self.map.questions[currentType][i]["searchKey"]
                if (searchKey in self.currentSummit.attributes.keys()) == False:
                    anyQuestion = True
                    keepOn = False
                else:
                    i += 1
            except Exception:
                keepOn = False
        if anyQuestion:
            self.searchKey = searchKey
            self.formulDic = self.map.questions[currentType][i]["questionBuildWords"]
            self.formulate()
        else:
            print("No question for this type")
    """
    def formulate(self):
        #print("MARKER 6")
        self.question = ""
        if self.formulDic["questType"] == "yn":
            sbjId = self.csg["subject"]
            if self.getSummit(sbjId).attributes["synonym"][0] in ["I", "me", "myself"]:
                self.question += "do you"
                for key in self.csg.keys():
                    if key != "subject":
                        tmpId = self.csg[key]
                        tmpEntity = self.getSummit(tmpId).attributes["synonymAIPOV"][0]
                        self.question += " " + tmpEntity
                        self.newQuestionFound = True
                print(self.question + "?")
        if self.formulDic["questType"] == "whElse":
            interrogative = "what"
            searchKey = self.formulDic["entityKey"]
            tmpId = self.csg[searchKey]
            searchType = self.getSummit(tmpId).attributes["type"][0]
            if searchType == "person":
                interrogative = "who"
            elif searchType == "place":
                interrogative = "where"
            self.question = interrogative + " else do"
            for key in self.csg.keys():
                if key != searchKey:
                    tmpId = self.csg[key]
                    tmpEntity = self.getSummit(tmpId).attributes["synonymAIPOV"][0]
                    self.question += " " + tmpEntity
                    self.newQuestionFound = True
            print(self.question + "?")
        #self.formulDic["interest"] = np.random.choice(self.currentSummit.attributes["synonymAIPOV"])
        """
        for key in self.formulDic:
            try:
                if key != "answerExamples":
                    if self.formulDic[key] == "/":
                        self.formulDic[key] = np.random.choice(self.currentSummit.attributes["synonymAIPOV"])
                    self.question += self.formulDic[key] + " "
                else:
                    self.question += "? " + self.formulDic[key]
            except Exception:
                pass
        """

    def getSummitEntityKey(self, csg):
        keepOn = True
        i = 0
        while keepOn:
            try:
                entityKey = list(csg.keys())[i]
                tmpId = csg[entityKey]
                #print("tmpId: ", tmpId)
                if tmpId == self.currentSummit.attributes["id"][0]:
                    keepOn = False
                i += 1
            except Exception:
                entityKey = None
                keepOn = False
        return entityKey

    def getSentence(self, entityKey):
        keepOn = True
        i = 0
        while keepOn:
            #r = np.random.randint(len(self.currentSummit.attributes["adjList"]))
            try:
                csi = self.currentSummit.attributes["adjList"][i]["csi"]
                print("csi: ", csi)
                csg = self.map.csgd[csi]
                print("csg: ", csg)
                tmpEntityKey = self.getSummitEntityKey(csg)
                #print("tmpEntityKey: ", tmpEntityKey)
                if tmpEntityKey == entityKey:
                    #print("MARKER 5")
                    keepOn = False
                i += 1
            except Exception:
                csi = None
                keepOn = False
        return csi

    def getEntity(self, entityKey, csi):
        entityId = self.map.csgd[csi][entityKey]
        entity = self.getSummit(entityId).attributes["synonym"][0]
        return entity

    def similarQuestion(self):
        if (self.currentSummit.attributes["synonym"][0] in ["I", "i", "me", "myself"]) == False:
            #print("MARKER 1")
            csi = self.getSentence("do")
            if csi != None:
                #print("MARKER 3")
                sbj = self.getEntity("subject", csi)
                #print("sbj: ", sbj)
                if ((sbj in ["I", "i", "me", "myself"]) == False) and ((self.currentSummit.attributes["synonym"][0] in ["I", "i", "me", "myself"]) == False):
                    #print("MARKER 7")
                    if self.entityAlreadyExists("I"):
                        #print("MARKER 8")
                        iId = self.getSummit("I").attributes["id"][0]
                        self.csg = self.map.csgd[csi].copy()
                        self.csg["subject"] = iId
                        print("self.csg: ", self.csg)
                        if self.csgAlreadyExists() == False:
                            self.formulDic = {"questType": "yn"}
                            self.formulate()
                elif ((sbj in ["I", "i", "me", "myself"]) == True) and ((self.currentSummit.attributes["synonym"][0] in ["I", "i", "me", "myself"]) == False):
                    self.csg = self.map.csgd[csi].copy()
                    self.formulDic = {"questType": "whElse", "entityKey": "do"}
                    self.formulate()

    def tellMoreRequest(self):
        self.question = "Tell me more about "
        syn = np.random.choice(self.currentSummit.attributes["synonymAIPOV"])
        self.question += syn
        self.prevCsg = {"subject": self.currentSummit.attributes["id"][0]}
        print(self.question)

    def isValid(self, answer):
        return True

    def catchAnswer(self, ynwDic):
        try:
            if ynwDic["ynw"] == "y":
                self.activeSummits = {}
                for entityKey in self.csg.keys():
                    try:
                        self.activeSummits[entityKey] = self.getSummit(self.csg[entityKey])
                    except Exception:
                        pass
            
            if ynwDic["ynw"] == "w":
                entity = ynwDic["input"]
                if self.isValid(entity):
                    entityKey = self.formulDic["entityKey"]
                    if self.entityAlreadyExists(entity):
                        s = self.getSummit(entity)
                    else:
                        s = self.setSummit(entityKey, entity)
                    self.csg[entityKey] = s.attributes['id'][0]
                    for entityKey in self.csg.keys():
                        try:
                            self.activeSummits[entityKey] = self.getSummit(self.csg[entityKey])
                        except Exception:
                            pass
            self.updateMap()
        except Exception:
            print("hmmm...")

    def socialStory(self):
        self.ssName = None
        out = False
        summitId = self.currentSummit.attributes["id"][0]
        if summitId in self.map.socialStorySummits.keys():
            self.ssName = np.random.choice(self.map.socialStorySummits[summitId])
            out = True
        return out

    def primeSocialStory(self):
        self.question = socialStoryDic[self.ssName]["primer"]
        print("social story - ", self.ssName, " - ON")
        self.priming = True
        #print(self.question)

    def defaultQuestion(self):
        print("default procedure")
        self.similarQuestion()
        if self.newQuestionFound == False:
            if self.currentSummit.attributes["type"][0] != "verb":
                self.tellMoreRequest()
            else:
                self.towardsSocialStory()
        self.newQuestionFound = False

    def towardsSocialStory(self):
        self.goToNeighbour()
        print("\ncurrent summit\n__________________________________________\n", self.currentSummit, "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        if self.socialStory():
            self.primeSocialStory()
        else:
            self.defaultQuestion()

    def main(self, grammAnalysis):
        self.grammarToSummit(grammAnalysis)
        self.updateMap()
        print("map\n__________________________________________\n", self.map, "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        self.setCurrentSummit()
        print("\ncurrent summit\n__________________________________________\n", self.currentSummit, "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

        r = np.random.randint(7)
        if r != 1:
            r = 0
        print("r = ", r)
        if r == 0:
            self.towardsSocialStory()

            #self.typeQuestion()
            #print(self.question)
        elif r == 1:
            self.defaultQuestion()

if __name__ == "__main__":
    botAI = AIManager()
    gm = GrammarManager()
    gToM = GrammarToMap()
    preMapBool = False
    mm = MapManager(preMapBool)

    preMapSentences = ["I live in my home", "the bathroom is in my home", "the bedroom is in my home"]
    for sentence in preMapSentences:
        tokens = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(tokens)
        verbPresence = bool(len(gm.searchVerbalGroup(tagged)))
        if verbPresence:
            print("premap sentence: ", sentence)
            ga = gm.processClause(sentence)

        gToM.setMapInput(ga)
        print("mapInput: ", gToM.mapInput, "\n")
        #verb = gToM.mapInput['verb']
        #stem = gm.stem(verb)

        mm.grammarToSummit(gToM.mapInput)
        mm.updateMap()

    while True:
        try:
            txtPath = "/home/zac/Documents/FinalFiles/output.txt"
            inputSentence = open(txtPath, "r").readline()
            #inputSentence = input("input >> ")
            clause = """Cindy plays the guitar in my room"""
            clause = """Brooke stayed in the bathroom"""
            botReaction = botAI.react(inputSentence)
            if botReaction == None:
                tokens = nltk.word_tokenize(inputSentence)
                tagged = nltk.pos_tag(tokens)
                #print("tagged: ", tagged)
                verbPresence = bool(len(gm.searchVerbalGroup(tagged)))
                if verbPresence:
                    #print("input sentence: ", inputSentence)
                    ga = gm.processClause(inputSentence)
                    #print("ga: ", ga)
                else:
                    if inputSentence == "yes":
                        mm.catchAnswer({"ynw": "y"})
                    else:
                        mm.catchAnswer({"ynw": "w", "input": inputSentence})
                    #mm.canonicalAnswer(inputSentence)
                print("ga: ", ga, "\n")

                gToM.setMapInput(ga)
                print("mapInput: ", gToM.mapInput, "\n")
                verb = gToM.mapInput['verb']
                stem = gm.stem(verb)
                print("stem: ", stem)

                mm.main(gToM.mapInput)
                if mm.priming:
                    botReaction = botAI.react(mm.question)
                    mm.priming = False
                    print(botReaction)
            else:
                print(botReaction)
            textToSendFile = open("textToSend.txt", "w")
            if botReaction:
                textToSendFile.write(botReaction)
            else:
                textToSendFile.write(mm.question)

        except Exception as e:
            print("Someting got wrong dude")
            print(e)
