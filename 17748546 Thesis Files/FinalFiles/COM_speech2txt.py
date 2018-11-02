from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud.websocket import RecognizeCallback
from os.path import join, dirname
import json
import sys

speech_to_text = SpeechToTextV1(
    iam_api_key = "mtWzuFyo7rMK7Jefthb9DppkziAl_uohLkFA2vPrMC8G",
    url = "https://gateway-syd.watsonplatform.net/speech-to-text/api")

class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_data(self, data):
        self.info = json.dumps(data, indent=2)
        self.data = data
        #print(self.info)

    def on_error(self, error):
        pass
        #print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        pass
        #print('Inactivity timeout: {}'.format(error))

myRecognizeCallback = MyRecognizeCallback()

with open(sys.argv[1], 'rb') as audio_file:
    response = speech_to_text.recognize_with_websocket(
    audio=audio_file,
    content_type='audio/wav',
    model='en-US_BroadbandModel',
    recognize_callback=myRecognizeCallback,
    interim_results=False,
    #keywords=['colorado', 'tornado', 'tornadoes'],
    #keywords_threshold=0.5,
    max_alternatives=1)
  
#print(myRecognizeCallback.data)
print(myRecognizeCallback.data['results'][0]['alternatives'][0]['transcript'])
#d = json.loads(myRecognizeCallback.info)
#print d["results"["alternatives"["transcirpts"]]]
