import nltk
from nltk.corpus import treebank
from common import patternTopic, dic, npVerbList, stateVerbList, articles, phrasalVerbParticules, syntaxicVerbParticules, irregularVerbs, stems, firstNames, cities

#sentence = """At eight o'clock on Thursday morning Arthur didn't feel very good."""

#tokens = nltk.word_tokenize(sentence)
#print(tokens)

#tagged = nltk.pos_tag(tokens)
#print(tagged)

#entities = nltk.chunk.ne_chunk(tagged)
#print(entities)

#t = treebank.parsed_sents('wsj_0001.mrg')[0]
#t.draw()
"""
patternTopic = {'IN': ['when']}
dic = {'eight': ['number', 'when'], "o'clock": ['when'], "thursday": ['day', 'when'], "morning": ['day', 'when'], "tomorrow": ['when']}
npVerbList = ["do", "does", "did", "have", "has", "had", "am", "are", "is", "was", "were", "will"]
stateVerbList = ["arrive", "stay", "live", "agree"]
articles = ["a", "an", "the"]
phrasalVerbParticules = {'look': ['about', 'after', 'ahead', 'alike', 'around', 'back', 'down', 'for', 'out', 'up'], 'give': ['away', 'back', 'in', 'out', 'up']}
syntaxicVerbParticules = {'look': ['at', 'in', 'into'], 'wait': ['for']}
irregularVerbs = {'be': {'present': ['am', 'is', 'are'], 'preterit': ['was', 'were'], 'pp': ['been']}, 'have': {'present': ['have', 'has'], 'preterit': ['had'], 'pp': ['had']}, 'do': {'present': ['do', 'does'], 'preterit': ['did'], 'pp': ['done']}}
stems = ['be']
"""
class GrammarManager(object):
    def __init__(self):
        pass

    def findIrregularStem(self, w):
        keepOn = True
        stemList = list(irregularVerbs.keys())
        i = 0
        while keepOn:
            stem = stemList[i]
            declensionDic = irregularVerbs[stem]
            declensionList = []
            for value in declensionDic.values():
                declensionList += value
            if w in declensionList:
                keepOn = False
            i += 1
        return stem

    def stem(self, w):
        if w in stems:
            stem = w
        else:
            if w[-3 :] == 'ing':
                stem = w[: -3]
            elif w[-2 :] == 'ed':
                stem = w[: -2]
            elif w[-1] == 'd':
                stem = w[: -1]
            elif w[-1] == 's' and w[-2] != 's' and w != "is":
                stem = w[: -1]
            else:
                stem = self.findIrregularStem(w)
            if (stem in stems) == False:
                stem += 'e'
        #print("stem: ", stem)
        return stem

    def searchVerbalGroup(self, tagged):
        i = 0
        verbalGroupList = []
        iStart = None
        iEnd = None
        pVP = []
        sVP = []
        while i < len(tagged) - 1:
            w = tagged[i]
            if w[1][0] == "V" or w[1] == 'MD':
                iStart = i
                j = iStart + 1
                keepOn = True
                while keepOn:
                    try:
                        w = tagged[j]
                        if w[1][0] == "V" or w[1] == "RB" or w[0] in pVP or w[0] in sVP:
                            try:
                                pVP = phrasalVerbParticules[self.stem(w[0])]
                            except Exception:
                                pass
                            try:
                                sVP = syntaxicVerbParticules[self.stem(w[0])]
                            except Exception:
                                pass
                            j += 1
                        else:
                            keepOn = False
                    except Exception:
                        keepOn = False
                    iEnd = j
                verbalGroupList += [['verb'] + tagged[iStart : iEnd] + [iStart, iEnd]]
                i = j
            else:
                i += 1
        try:
            pass
        except Exception:
            pass

        return verbalGroupList

    def fitPotential(self, w, potential):
        output = False
        if w[0].lower() in potential or w[1] in potential:
            output = True
        #print("fit? ", output)
        return output

    def getPotentialFollowing(self, w):
        if w[0] in articles or w[1] == "PRP$":
            potentialFollowing = articles + ['JJ', 'NN']
        if w[0] in firstNames:
            potentialFollowing = ["POS", "JJ"]
        if w[1] == "NN":
            potentialFollowing = ["NN"] + ["of"]
        if w[1] == "JJ":
            potentialFollowing = firstNames + cities + ["NN"]
        if w[1] == "POS":
            potentialFollowing = ["NN", "JJ"]
        if w[0] == "of":
            potentialFollowing = firstNames + articles + cities + ["PRP$"]
        return potentialFollowing

    def searchContingent(self, tagged):
        contingentList = []
        for i in range(len(tagged) - 1):
            w = tagged[i]
            if w[1] in patternTopic.keys():
                iStart = i
                for topic in patternTopic[w[1]]:
                    j = i + 1
                    keepOn = True
                    topicDetected = False
                    potentialFollowing = firstNames + articles + cities + ["NN", "PRP$"]
                    while keepOn:
                        #print("topic: ", topic)
                        #print("w: ", w)
                        #print("j: ", j)
                        try:
                            topicDetected = (topic in dic[tagged[j][0]])
                        except:
                            pass
                        #print("topic detected: ", topicDetected)
                        try:
                            if (topicDetected or self.fitPotential(tagged[j], potentialFollowing)) and tagged[j]:
                                j += 1
                                potentialFollowing = self.getPotentialFollowing(tagged[j])
                            else:
                                keepOn = False
                        except Exception:
                            keepOn = False
                        """
                        try:
                            if topic in dic[tagged[j][0]]:
                                j += 1
                            else:
                                keepOn = False
                        except Exception:
                            keepOn = False
                        """
                    iEnd = j
                    if j - 1 != i and topicDetected:
                        contingentList += [[topic] + tagged[i : j] + [iStart, iEnd]]
        return contingentList

    def getPotentialPrevious(self, w):
        if w[1] == 'PRP' or w in articles:
            potentialPrevious = articles + ['and', 'or']
        if w[0] in firstNames:
            potentialPrevious = firstNames + ['PRP$']
        if w[1] == 'NN':
            potentialPrevious = articles + ['POS', 'PRP$']
        if w[1] == 'POS':
            potentialPrevious = firstNames
        return potentialPrevious

    def searchSubject(self, tagged, group, markedTokens):
        iStart = group[-2]
        jEnd = iStart
        i = jEnd - 1
        keepOn = True
        subject = []
        potentialPrevious = firstNames + ['PRP', 'NN']
        while keepOn:
            try:
                if i >= 0:
                    w = tagged[i]
                    #print("w: ", w)
                    #print("potentialPrevious: ", potentialPrevious[: 5])
                    if markedTokens[i] == 0 and (self.fitPotential(w, potentialPrevious)):
                        i += -1
                        potentialPrevious = self.getPotentialPrevious(w)
                    else:
                        keepOn = False
                else:
                    keepOn = False
            except Exception:
                keepOn = False
        jStart = i + 1
        #jEnd += 1
        subject += [['subject'] + tagged[jStart : jEnd] + [jStart, jEnd]]
        return subject

    def classify(self, w):
        try:
            topics = dic[w[0]]
            topic = topics[0]
        except Exception:
            topic = None
        return topic

    def verbAnalysis(self, group):
        analysis = []
        verbPresence = False
        doLiable = False
        saLiable = False
        for k in range(1, len(group) - 2):
            tmpList = []
            w = group[k]
            tmpStr = ""
            if (w[1] == "MD" or w[1][0] == "V"):
                tmpList += [w]
                if w[1][0] == "V":
                    verbPresence = True
                #if (w[0] in stateVerbList or w[0][: -1] in stateVerbList or w[0][: -2] in stateVerbList):
                if self.stem(w[0]) in stateVerbList:
                    tmpStr += "s"
                    saLiable = True
                else:
                    tmpStr += "a"
                #if ((w[0] in npVerbList or w[0][: -1] in npVerbList or w[0][: -2] in npVerbList) == False):
                    #tmpStr += "p"
                #else:
                    #tmpStr += "n"
                if tmpStr == "a":
                    doLiable = True
                if tmpStr == "s":
                    saLiable = True
                tmpList += [tmpStr]
                analysis += [tmpList]

        analysis += [saLiable, doLiable, verbPresence]
        return analysis
                
    def searchDO(self, group, tagged, markedTokens):
        analysis = self.verbAnalysis(group)
        #print("analysis: ", analysis)
        verbPresence = analysis[-1]
        doLiable = analysis[-2]
        saLiable = analysis[-3]
        do = []
        if verbPresence and (doLiable or saLiable):
            verbList = []
            for elem in analysis:
                try:
                    if elem[0][1][0] == "V":
                        verbList += [elem[0][0]]
                except Exception:
                    pass
            #print("verbList: ", verbList)
            iEndVG = group[-1]
            iStart = iEndVG
            i = iStart
            keepOn = True
            potentialFollowing = firstNames + articles + ["NN", "PRP$", "JJ"]
            while keepOn:
                try:
                    w = tagged[i]
                    #print("w[" + str(i) + "]: ", w)
                    if self.fitPotential(w, potentialFollowing) and markedTokens[i] == 0:
                        i += 1
                        potentialFollowing = self.getPotentialFollowing(w)
                    else:
                        keepOn = False
                except Exception:
                    keepOn = False
            iEnd = i
            if iStart != iEnd:
                if doLiable:
                    do = [["do"] + tagged[iStart : iEnd] + [iStart, iEnd]]
                if saLiable and doLiable == False:
                    do = [["sa"] + tagged[iStart : iEnd] + [iStart, iEnd]]
        return do
        
            
    def processClause(self, clause):
        tokens = nltk.word_tokenize(clause)
        tagged = nltk.pos_tag(tokens)
        #print("tagged: ", tagged)
        markedTokens = [0 for k in range(len(tokens))]
        #print("markedTokens: ", markedTokens)
        clause = clause.lower()

        verbalGroupList = self.searchVerbalGroup(tagged)
        #print("verbalGroup: ", verbalGroupList)
        for group in verbalGroupList:
            iStart, iEnd = group[-2], group[-1]
            markedTokens[iStart : iEnd] = [1 for k in range(iEnd - iStart)]
            do = self.searchDO(group, tagged, markedTokens)
            for dirObj in do:
                try:
                    iStart, iEnd = dirObj[-2], dirObj[-1]
                    markedTokens[iStart : iEnd] = [1 for k in range(iEnd - iStart)]
                except Exception:
                    pass
            #print("do: ", do)
        #print("markedTokens: ", markedTokens)

        contingentList = self.searchContingent(tagged)
        #print("contigent: ", contingentList)        
        for contingent in contingentList:
            iStart, iEnd = contingent[-2], contingent[-1]
            markedTokens[iStart : iEnd] = [1 for k in range(iEnd - iStart)]
        #print("markedTokens: ", markedTokens)

        subject = self.searchSubject(tagged, group, markedTokens)
        #print("subject: ", subject)
        for group in subject:
            iStart, iEnd = group[-2], group[-1]
            markedTokens[iStart : iEnd] = [1 for k in range(iEnd - iStart)]
        #print("markedTokens: ", markedTokens)

        remainders = []
        for i in range(len(markedTokens)):
            if markedTokens[i] == 0:
                w = tagged[i]
                #print("w: ", w)
                topic = self.classify(w)
                if topic != None:
                    remainders += [[topic] + [w] + [i, i + 1]]
                    markedTokens[i] = 1
        #print("remainders: ", remainders)
        #print("markedTokens: ", markedTokens)

        #print('\n')
        #print(subject)
        #print(verbalGroupList)
        #print(do)
        #print(contingentList)
        #print(remainders)

        processResult = {}
        processResult['subject'] = subject
        processResult['verb'] = verbalGroupList
        processResult['do'] = do
        processResult['contingent'] = contingentList
        processResult['remainders'] = remainders
        
        return processResult
        

if __name__ == '__main__':
    #clause = """Brooke's sister likes playing this beautiful guitar in my room"""
    clause = """i like pizzas"""
    gm = GrammarManager()
    ga = gm.processClause(clause)
    print("ga: ", ga)

        