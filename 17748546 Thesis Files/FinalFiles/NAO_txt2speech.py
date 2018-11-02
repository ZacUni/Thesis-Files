from naoqi import ALProxy
import sys
import os

# this is to run on the nao


ip = sys.argv[1]
tts = ALProxy("ALTextToSpeech", ip, 9559)

filePath = "/var/persistent/home/nao/recordings/microphones/"
fileName = "textToSend.txt"
sendBool = False

print("\033[1;5;36;52mWaiting for file...\033[0m")

while(not sendBool):
    try:
        file = open(os.path.join(filePath,fileName), "r")
        print("++ T2S - File opened dif ++")
        for line in file:
            if(len(line)):
                print("++ T2S - inside for ++")
                textOutput = line
                print("\033[33m Text Said: " + textOutput + "\033[33m")
                tts.say(textOutput)
            else:
                print("++ T2S - File contains nothing ++")

        sendBool = True
        file.close()
        try:
            os.remove(os.path.join(filePath,fileName))
            print("++ T2S - File removed ++")
        except OSError:
            print("File could not be removed")

    except Exception:
        pass
        #print('except')
