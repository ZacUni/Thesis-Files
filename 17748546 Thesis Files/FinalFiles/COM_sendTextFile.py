import paramiko
import sys

exists = False

NAO_URL = sys.argv[1]  # IP address of the NAO

c_path_notString = "/home/WoodZ/Documents/ResearchProject/RecordedFiles/textToSend.txt"  # path to store the recorded file
nao_path_notString = "/var/persistent/home/nao/recordings/microphones/textToSend.txt" # path to find recorded file
c_path = str(c_path_notString)
nao_path = str(nao_path_notString)

transport = paramiko.Transport((NAO_URL, 22))
transport.connect(username = "nao", password = "nao")
sftp = paramiko.SFTPClient.from_transport(transport)

#sftp.mkdir("/var/persistent/home/nao/recordings/madefilehere", mode = 511)

while(not exists):
	try:
		sftp.put(c_path, nao_path)
		exists = True
	except Exception:
		pass

sftp.close()
transport.close()
