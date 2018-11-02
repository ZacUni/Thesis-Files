from grammarManager import GrammarManager
from common import firstNames, familyMemberTitles, getType

class GrammarToMap(object):
    def __init__(self):
        self.mapInput = {}
    
    def getEntity(self, entityKey, grammarAnalyse):
        out = []
        outTagged = grammarAnalyse[entityKey]
        for elem in outTagged:
            outKey = elem[0]
            tagged = elem[1 : -2]
            outStr = ""
            for i in range(len(tagged)):
                if i == 0 or tagged[i][0][0] == "'":
                    outStr += tagged[i][0]
                else:
                    outStr += " " + tagged[i][0]
            self.mapInput[outKey] = outStr
        return out

    def setMapInput(self, grammarAnalyse):
        self.mapInput = {}
        for entityKey in grammarAnalyse.keys():
            self.getEntity(entityKey, grammarAnalyse)

if __name__ == "__main__":
    #clause = """Brooke's sister likes playing this beautiful guitar in my room"""
    clause = """Cindy plays the guitar in my room"""
    gm = GrammarManager()
    grammarAnalyse = gm.processClause(clause)
    print(grammarAnalyse)

    gToM = GrammarToMap()
    gToM.setMapInput(grammarAnalyse)
    print(gToM.mapInput)