import socket
import hashlib
import os
import struct

FLAGS = None
class ClientSocket():

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('192.168.0.4', int(FLAGS.port)))
        
    def socket_send(self):
        
        def calChecksum(data):

            checksum = int.from_bytes(data, "big")
            checksum = hex(checksum).replace('0x','')
            realsum = 0

            i = len(checksum)

            if i < 20 :
                return checksum.zfill(20)
                

            while i >= 20 :
                realsum = realsum + int(checksum[i-20:i], 16)
                i=i-20

            realsum = hex(realsum).replace('0x','')
            leng = len(realsum)

            if leng > 20 :
                realsum = int(realsum[0:leng-20],16)+int(realsum[leng-20:leng],16)
            
            return (hex(realsum).replace('0x', '')).zfill(20)
        
        print("Sender Socket open...")
        print("Receiver IP = ",(FLAGS.ip))
        print("Receiver Port = ",int(FLAGS.port))

        fileName = input("Input File Name : ")
        filesize = os.path.getsize(fileName)
        bfilesize = filesize
        print("Send File Info(file name, file size, seqNum) to Server...")
        
        seqNum = 0
        finalsize = 0
     
        send_header = 0
        readfile = open(fileName, 'rb')

        while True:
                #try:
                    
                    if finalsize==filesize:
                        readfile.close()
                        break
                    
                    #send
                    datafile = readfile.read(1024)
                    
                    packet_data = ''
                    if send_header == 0 :
                        
                        print("Send File Info(file name, file size, seqNum) to Server...")
        
                        #file name (11byte)
                        fileName = bytearray(fileName.encode())
                        fileName = bytearray(11-len(fileName))+fileName
        
                        #file size (4byte)
                        bfilesize = bytearray((str(hex(bfilesize)).replace("0x", "")).encode())
                        bfilesize = bytearray(4-len(bfilesize))+bfilesize
                        
                        print("Start File send")
                        in_hash = str(seqNum).encode()+datafile
                        data_hash = calChecksum(in_hash)
                        packet_data = struct.pack('1b11s4s1024s1b20s', 0, fileName, bfilesize, datafile, seqNum, data_hash.encode())
                        
                        send_header=1

                    else :
                        in_hash = str(seqNum).encode()+datafile
                        data_hash = calChecksum(in_hash)
                        packet_data = struct.pack('20s1b'+str(len(datafile))+'s', data_hash.encode(), seqNum, datafile)
                
                    self.socket.sendto(packet_data, (FLAGS.ip, int(FLAGS.port)))
        
                    sign, addr = self.socket.recvfrom(10)

                    if sign.decode() == '1' or  sign.decode() == '0' :
                        currentsize = len(datafile)
                        finalsize = finalsize + currentsize

                        print("(current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")
                        seqNum = seqNum^1
                        continue

                    elif sign.decode() == '2' :

                        print("* Received NAK - Retransmit!")
                        while sign.decode() != '1' and  sign.decode() !='0' :
                            self.socket.sendto(packet_data, (FLAGS.ip, int(FLAGS.port)))
                            sign, addr = self.socket.recvfrom(10)

                        currentsize = len(datafile)
                        finalsize = finalsize + currentsize

                        print("Retransmission : (current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")

                        seqNum = seqNum^1
                        continue

                    elif sign.decode() == '9' :
                        print("* TimeOut !!! ***")
                        while sign.decode() != '1' and sign.decode()!='0' :
                            self.socket.sendto(packet_data, (FLAGS.ip, int(FLAGS.port)))
                            sign, addr = self.socket.recvfrom(10)

                        currentsize = len(datafile)
                        finalsize = finalsize + currentsize
                        print("Retransmission : (current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")
                        seqNum = seqNum^1
                        continue


                #except:
                    #print("except")
                    #break

        print("File send end")

        self.socket.close()

    def main(self):
        self.socket_send()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', type=str, default='localhost')
    parser.add_argument('-p', '--port', type=int, default=8080)

    FLAGS, _ = parser.parse_known_args()

    client_socket = ClientSocket()
    client_socket.main()


