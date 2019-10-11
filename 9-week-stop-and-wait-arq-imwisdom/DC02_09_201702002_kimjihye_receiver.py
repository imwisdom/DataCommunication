import socket
import os
import hashlib
import argparse
import struct

FLAGS = None
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ip', type=str, default = 'localhost')
parser.add_argument('-p', '--port', type=str, default = '8080')

FLAGS, _ = parser.parse_known_args()
#calculation checksum
def calChecksum(data) :
    
    checksum = int.from_bytes(data, "big")
    checksum = hex(checksum).replace('0x','')
    realsum = 0

    i = len(checksum)

    if i < 20 :
        return checksum.zfill(20)

    while i >= 20 :
        realsum = realsum + int(checksum[i-20:i], 16)
        i = i-20

    realsum = hex(realsum).replace('0x', '')
    leng = len(realsum)

    if leng > 20 :
        realsum = int(realsum[0:leng-20], 16) + int(realsum[leng-20:leng], 16)    
    return (hex(realsum).replace('0x', '')).zfill(20)

self_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
self_socket.bind((FLAGS.ip, int(FLAGS.port)))

print("Send file info ACK..")

#get header

sign = 1
unpacked =''
header = ''
addr = ''
while True:
    self_socket.settimeout(5)
    
    try:
        header, addr = self_socket.recvfrom(1061)

    except socket.timeout:
        print("no packet")
        break;

    unpacked = struct.unpack('1b11s4s'+str((len(header)-37))+'s1b20s', header)

    in_hash = str(unpacked[4]).encode()+unpacked[3]
    
    if  unpacked[5].decode() == calChecksum(in_hash) :
        self_socket.sendto(str(sign).encode(), (addr[0], int(FLAGS.port)))
        sign = sign^1
        break;
    else :
        print("Packet corrupted!! *** - Send To Sender NAK(2)")
        self_socket.sendto(str(2).encode(), (addr[0], int(FLAGS.port)))

#get file info
fileName = (unpacked[1].decode()).replace("\x00", "")
filesize = (unpacked[2].decode()).replace("\x00", "")
filesize = int(filesize, 16)

print("File Name : ", fileName)
print("File Size : ", filesize)

print("Received File Path = ", os.path.expanduser('~/send.jpg'))

recvFile = open(fileName, 'wb')
recvFile.write(unpacked[3])
currentsize = len(unpacked[3])
finalsize = currentsize

print( "(current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")

sign = 0

data = ''
while True:
    #try:
          
        if finalsize == filesize:
            recvFile.close()
            print("File receive end.")
            break

        self_socket.settimeout(5)
        try:
            data, addr = self_socket.recvfrom(1045)

        except socket.timeout:
            print("Wait for 5 ...")
            self_socket.sendto(str(9).encode(), (addr[0], int(FLAGS.port)))
            continue;
    
        datasize = len(data)-21
        unpacked = struct.unpack('20s1b'+str(datasize)+'s', data)
        
        #make checksum
        in_hash = str(unpacked[1]).encode()+unpacked[2]
        recv_hash = calChecksum(in_hash)

        #checksum test
        if unpacked[0].decode() == recv_hash :
            
            currentsize = len(unpacked[2])
            finalsize = finalsize + currentsize

            print( "(current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")

            recvFile.write(unpacked[2])

            sign = 1
            self_socket.sendto(str(sign).encode(), (addr[0], int(FLAGS.port)))
            
            sign = sign^1
            continue;

        else :
            print("Packet corrupted!! *** - Sent To Sender NAK(2)")
            self_socket.sendto(str(2).encode(), (addr[0], int(FLAGS.port)))
        

    
    #except : 
        #print("except")
        #break


