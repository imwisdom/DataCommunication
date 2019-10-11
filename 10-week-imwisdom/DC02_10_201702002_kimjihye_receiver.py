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
def calChecksum(idtype, length, n, payload) :
    
    idtype = int.from_bytes(idtype, "big")
    length = int.from_bytes(length, "big")

    n = int.from_bytes(n, "big")

    checksum = idtype + length + n
    
    for i in payload :
        checksum = checksum + i
    
    checksum = checksum.to_bytes(20, byteorder="big")
    return checksum


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
        header, addr = self_socket.recvfrom(1080)

    except socket.timeout:
        print("no packet")
        break;

    unpacked = struct.unpack('1s15s20s1024s20s', header)

    #type, size, n, data
    data_checksum = calChecksum(unpacked[0], unpacked[2], unpacked[1], unpacked[3])
    if  unpacked[4]  == data_checksum :
        self_socket.sendto(str(sign).encode(), (addr[0], int(FLAGS.port)))

        break;
    else : 
        print("Packet corrupted!! *** - Send To Sender NAK(2)")
        self_socket.sendto(str(2).encode(), (addr[0], int(FLAGS.port)))

#get file info
fileName = unpacked[1].decode().replace("\x00", "")
filesize = int.from_bytes(unpacked[2], "big")

print("File Name : ", fileName)
print("File Size : ", filesize)

print("Received File Path = ", os.path.expanduser('~/send.jpg'))

recvFile = open(fileName, 'wb')
recvFile.write(unpacked[3])

finalsize = len(unpacked[3])

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
            data, addr = self_socket.recvfrom(1080)

        except socket.timeout:
            print("Wait for 5 ...")
            self_socket.sendto(str(9).encode(), (addr[0], int(FLAGS.port)))
            continue;
    
        unpacked = struct.unpack('1s15s20s1024s20s', data)
        
        #make checksum
        recv_hash = calChecksum(unpacked[0], unpacked[2], unpacked[1], unpacked[3])
        finalsize = int.from_bytes(unpacked[2], "big")
        #checksum test
        if unpacked[4] == recv_hash :
        
            print( "(current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")

            recvFile.write(unpacked[3])
            
            if int.from_bytes(unpacked[1], "big") == 0 :
                sign = 1
            else :
                sign = 0
            self_socket.sendto(str(sign).encode(), (addr[0], int(FLAGS.port)))
            
            continue;

        elif sign != unpacked[1].decode():   #wrong order
            print("Packet corrupted!! *** - Sent To Sender NAK(1)")
            self_socket.sendto("n1".encode(), (addr[0], int(FLAGS.port)))
        else :  #packet loss
            print("Packet corrupted!! *** - Sent To Sender NAK(2)")
            self_socket.sendto('2'.encode(), (addr[0], int(FLAGS.port)))
    
    #except : 
        #print("except")
        #break


