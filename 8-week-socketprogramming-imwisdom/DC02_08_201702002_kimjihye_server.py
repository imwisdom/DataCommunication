import socket
import os
import hashlib
import argparse

FLAGS = None
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ip', type=str, default = 'localhost')
parser.add_argument('-p', '--port', type=str, default = '8080')

FLAGS, _ = parser.parse_known_args()

self_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
self_socket.bind((FLAGS.ip, int(FLAGS.port)))
#get fileName
fileName, addr = self_socket.recvfrom(2000)

print("file recv start")
print(fileName)
#get file size
filesize, addr = self_socket.recvfrom(2000)
filesize = int(filesize)

print("File Name : ", fileName.decode())
print("File Size : ", filesize)

recvFile = open(fileName.decode(), 'wb')
    
finalsize = 0
while True:
    try:
        
        if finalsize == filesize:
            recvFile.close()
            break

        data, addr = self_socket.recvfrom(2000)

        recvFile.write(data)

        currentsize = len(data)
        finalsize = finalsize + currentsize
    
        print("current_size / total_size = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")
    
    except : 
        break

print("the end")   

