import socket
import os
import hashlib
import argparse
import struct
import time

FLAGS = None
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ip', type=str, default = 'localhost')
parser.add_argument('-p', '--port', type=str, default = '8080')

FLAGS, _ = parser.parse_known_args()
#calculation checksum
def calChecksum(idtype, length, n, payload) :
    
    idtype = int.from_bytes(idtype, "big")
    length = int.from_bytes(length, "big")

    n = int.from_bytes(n, "big")

    checksum = idtype + length + n
    
    for i in payload :
        checksum = checksum + i
    
    checksum = checksum.to_bytes(20, byteorder="big")
    return checksum

def compareCS(unpacked) :
	
	if unpacked[4] == calChecksum(unpacked[0], unpacked[2], unpacked[1], unpacked[3]):
		return True
	else:
		return False

startT = time.time()

self_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
self_socket.bind((FLAGS.ip, int(FLAGS.port)))

print("Send file info ACK..")

#get header

addr = ''

header = ''
frame_1 = ''
frame_2 = ''
frame_3 = ''

unpacked_header = ''
unpacked_1 = ''
unpacked_2 = ''
unpacked_3 = ''

while True:
	
	self_socket.settimeout(5)
    
	try:
		header, addr = self_socket.recvfrom(1080)
		frame_1, addr = self_socket.recvfrom(1080)
		frame_2, addr = self_socket.recvfrom(1080)
		frame_3, addr = self_socket.recvfrom(1080)

	except socket.timeout:
		print("no packet")
		break

	unpacked_header = struct.unpack('1s15s20s1024s20s', header)
	unpacked_1 = struct.unpack('1s15s20s1024s20s', frame_1)
	unpacked_2 = struct.unpack('1s15s20s1024s20s', frame_2)
	unpacked_3 = struct.unpack('1s15s20s1024s20s', frame_3)

	if compareCS(unpacked_header) and compareCS(unpacked_1) and compareCS(unpacked_2) and compareCS(unpacked_3):

		self_socket.sendto(str(4).encode(), (addr[0], int(FLAGS.port)))
		
		break;
	else : 
		self_socket.sendto(str(9).encode(), (addr[0], int(FLAGS.port)))


#get file info
fileName = unpacked_header[1].decode().replace("\x00", "")
filesize = int.from_bytes(unpacked_header[2], "big")

print("File Name : ", fileName)
print("File Size : ", filesize)

print("Received File Path = ", os.path.expanduser('~/send.jpg'))

recvFile = open(fileName, 'wb')

recvFile.write(unpacked_header[3])
recvFile.write(unpacked_1[3])
recvFile.write(unpacked_2[3])
recvFile.write(unpacked_3[3])

finalsize = len(unpacked_header[3])

print( "(current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")
finalsize = int.from_bytes(unpacked_1[2], "big")
print( "(current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")
finalsize = int.from_bytes(unpacked_2[2], "big")
print( "(current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")
finalsize = int.from_bytes(unpacked_3[2], "big")
print( "(current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")


data_frame = ''
while True:
    #try:
          
	if finalsize == filesize:
		recvFile.close()
		print("File receive end.")
		break

	self_socket.settimeout(5)
	
	try:
		data_frame, addr = self_socket.recvfrom(1080)

	except socket.timeout:
		self_socket.sendto(str(9).encode(), (addr[0], int(FLAGS.port)))
		continue;
    
	unpacked = struct.unpack('1s15s20s1024s20s', data_frame)
        
	finalsize = int.from_bytes(unpacked[2], "big")
    #checksum test
	
	if compareCS(unpacked) :
		print( "(current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")

		recvFile.write(unpacked[3])
            
		ack = (int.from_bytes(unpacked[1], "big")+1)%8
		self_socket.sendto(str(ack).encode(), (addr[0], int(FLAGS.port)))
            
		continue;

	else :
		self_socket.sendto(str(9).encode(), (addr[0], int(FLAGS.port)))
    
    #except : 
        #print("except")
        #break
endT = time.time()
print(endT-startT)
