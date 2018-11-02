#!/bin/bash

ip="192.168.19.224"

rm output.txt

python COM_getSoundFile.py $ip
python COM_speech2txt.py '/home/zac/Documents/WatsonSpeechStuff/audioFile.wav' >> output.txt

python mapZac.py

python COM_sendTextFile.py $ip

