# -*- coding: utf-8 -*-

import os
import aiml
from common import aimlFolderList

class AIManager(object):
    def __init__(self):
        self.kernelList = []
        for aimlFolder in aimlFolderList:
            kernel = aiml.Kernel()
            kernel.learn(aimlFolder + "try_startup.xml")
            kernel.respond("load aiml b")
            self.kernelList += [kernel]


    
    def react(self , heardText):
        """
        input : text said by the interlocutor | type : string
        output : answer the robot must answer | type : string
        text = None
        return text
        """
        if heardText == "quit":
            exit()
            answer = None
        else:
            keepOn = True
            i = 0
            while keepOn:
                try:
                    kernel = self.kernelList[i]
                    curFolder = aimlFolderList[i]
                    print("read folder : " , curFolder)
                    answer = kernel.respond(heardText)
                    if len(answer) > 0:
                        keepOn = False
                    else:
                        i += 1
                 
                except Exception:
                    if i >= len(self.kernelList):
                        keepOn = False
                        #answer = "Every AIML folder has been scanned: No match found"
                        print("Every AIML folder has been scanned: No match found")
                        answer = None
        
        return answer

if __name__ == '__main__':
    aiManager = AIManager()
    while True:
        heardText = input("Enter your message >> ")
        answer = aiManager.react(heardText)
        print("answer : " , answer)