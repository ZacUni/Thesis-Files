"""
aimFolderList: list of folders AIML scripts are saved in. The folders are sorted according to their reading priority.
"""
aimlFolderList = ['aiml/']

####################################################################################################################

"""
Creation of a list of first names
"""
"""
firstNameTxt = open('firstNames.txt', 'r')
firstNamePy = open('firstName.py', 'w')
firstNamePy.write("firstNames = [")
keepOn = True
firstElem = True
while keepOn:
    firstName = firstNameTxt.readline()[: -1].lower()
    if len(firstName) > 0:
        if firstElem:
            firstNamePy.write("'" + firstName + "'")
            firstElem = False
        else:
            firstNamePy.write(", '" + firstName + "'")
    else:
        keepOn = False
firstNamePy.write("]")
firstNamePy.close()
firstNameTxt.close()
"""
from firstName import firstNames
from city import cities

####################################################################################################################

familyMemberTitles = ['mother', 'father', 'brother', 'sister', 'aunt', 'uncle', 'cousin', 'nephew']
relationship = familyMemberTitles + ["friend"]

####################################################################################################################

socialStoryDic = {"bathroom": {"primer": "BATHROOMPRIMER",
                               "topics": ["bathroom", "toilets", "flush", "shower"]},
                  "bullying": {"primer": "BULLYINGPRIMER",
                               "topics": ["bullying", "bully", "bullies", "intimidate", "tyrannise", "tyrannize", "inveigle"]}}
reducedList = []
for key in socialStoryDic:
    reducedList += socialStoryDic[key]["topics"]
####################################################################################################################

patternTopic = {'IN': ['when', 'where']}
dic = {'eight': ['number', 'when'], "o'clock": ['when'], "thursday": ['day', 'when'], "morning": ['day', 'when'], "tomorrow": ['when'], 'now': ['when'], 'stadium': ['where']}
npVerbList = ["do", "does", "did", "have", "has", "had", "am", "are", "is", "was", "were", "will"]
stateVerbList = ["be", "arrive", "stay", "live", "die", "come", "go"]
articles = ["a", "an", "the", "this", "every", "all"]
phrasalVerbParticules = {'look': ['about', 'after', 'ahead', 'alike', 'around', 'back', 'down', 'for', 'out', 'up'], 'give': ['away', 'back', 'in', 'out', 'up']}
syntaxicVerbParticules = {'look': ['at', 'in', 'into'], 'wait': ['for']}
irregularVerbs = {'be': {'present': ['am', 'is', 'are'], 'preterit': ['was', 'were'], 'pp': ['been']}, 'have': {'present': ['have', 'has'], 'preterit': ['had'], 'pp': ['had']}, 'do': {'present': ['do', 'does'], 'preterit': ['did'], 'pp': ['done']}}

####################################################################################################################
"""
Creation of a list of verb stems
"""
"""
irregularVerbTxt = open('irregularVerbs.txt', 'r')
stemPy = open('stem.py', 'w')
stemPy.write("stems = [")
i = 0
keepOn = True
firstElem = True
while keepOn:
    verb = irregularVerbTxt.readline()[: -1].lower()
    if len(verb) > 0:
        if i%3 == 0:
            if firstElem:
                stemPy.write("'" + verb + "'")
                firstElem = False
            else:
                stemPy.write(", '" + verb + "'")
        i += 1
    else:
        keepOn = False
irregularVerbTxt.close()
regularVerbTxt = open('regularVerbs.txt', 'r')
keepOn = True
while keepOn:
    verb = regularVerbTxt.readline()[: -1].lower()
    if len(verb) > 0:
        stemPy.write(", '" + verb + "'")
    else:
        keepOn = False
stemPy.write("]")
stemPy.close()
"""
from stem import stems

def concaDic(dicList):
    dic = {}
    for d in dicList:
        for key in d.keys():
            dic[key] = d[key]
    return dic

from noun import nounDic as d0
from nounPlace import nounDic as d1
from nounTime import nounDic as d2

dic = concaDic([d0, d1, d2])
#print(dic)

from musicalInstruments import musicalInstruments

def getReduced(ng):
    tmp = ng.split(" ")
    if "of" in tmp:
        keepOn = True
        i = 0
        while keepOn:
            if tmp[i] == "of":
                reduced = tmp[i - 1]
                keepOn = False
            i += 1
    else:
        reduced = tmp[- 1]
    return reduced

def getType(key, value):
    print('key: ', key, "    value: ", value)
    reducedKey, reducedValue = getReduced(key), getReduced(value)
    personKeys = firstNames + ['ww', 'members', 'friends'] + familyMemberTitles
    roomKeys = ['rooms']
    placeKeys = ['places', 'house']
    cityKeys = ['city']
    if reducedKey in personKeys or reducedValue in personKeys or reducedKey.lower() in personKeys or reducedValue.lower() in personKeys:
        typeS = 'person'
    elif key == "verb":
        typeS = 'verb'
    elif reducedKey[: 5] == 'where' or reducedKey in placeKeys or reducedKey.lower() in placeKeys:
        typeS = 'place'
    elif reducedKey in roomKeys:
        typeS = 'room'
    elif reducedKey in cityKeys or reducedKey.lower() in cityKeys:
        typeS = 'city'
    elif reducedKey == 'activity' or reducedKey == 'commonActivity' or reducedValue in musicalInstruments:
        typeS = 'activity'
    elif reducedKey == 'who' or reducedKey == 'whoFamily' or reducedKey == 'family':
        typeS = 'family'
    elif reducedKey == 'friendGroup':
        typeS = 'friendGroup'
    else:
        typeS = 'defaultType'
    #print('typeS: ', typeS)
    return typeS

def getSynonymAIPOV(entityKey, entity):
    split = entity.split(" ")
    for i in range(len(split)):
        if split[i] == "my":
            split[i] = "your"
        elif split[i] == "I" or split[i] == "i":
            split[i] = "you"
        elif split[i] == "me":
            split[i] = "you"
        elif split[i] == "mine":
            split[i] = "yours"
        elif split[i] == "you":
            if entityKey == "subject":
                split[i] = "I"
            elif entityKey == "do":
                split[i] = "me"
        elif split[i] == "yours":
            split[i] = "mine"
    out = ""
    for elem in split:
        if len(out) == 0:
            out += elem
        else:
            out += " " + elem
    return out

def standardise(ng):
    out = ""
    split = ng.split(" ")
    locationPrep = ["in", "at", "on"]
    if split[0] in locationPrep:
        split = split[1 :]
    for elem in split:
        if len(out) == 0:
            out += elem
        else:
            out += " " + elem
    return out