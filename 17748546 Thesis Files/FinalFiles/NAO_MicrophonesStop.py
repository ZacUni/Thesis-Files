from naoqi import ALProxy

ad = ALProxy("ALAudioDevice", "192.168.0.100", 9559)
ad.stopMicrophonesRecording()
