import socket
import os
import struct

FLAGS = None
class ClientSocket():

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('192.168.0.5', int(FLAGS.port)))
        
    def socket_send(self):
        
        def calChecksum(idtype, length, n, payload):
     
            idtype = int.from_bytes(idtype.encode(), "big")
            
            n = int.from_bytes(n, "big")

            checksum = idtype + length + n

            for i in payload:
                checksum = checksum + i

            checksum = checksum.to_bytes(20, byteorder="big")
            
            return checksum

        print("Sender Socket open...")
        print("Receiver IP = ",(FLAGS.ip))
        print("Receiver Port = ",int(FLAGS.port))

        fileName = input("Input File Name : ")
        filesize = os.path.getsize(fileName)
        bfilesize = filesize
        
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
                        
                        #file name (15byte)
                        fileName = fileName.rjust(15,"\x00").encode()
        
                        #file size (20byte)
                        bfilesize = bfilesize.to_bytes(20, byteorder="big")
                    
                        print("Start File send")
                        data_checksum = calChecksum('s',filesize, fileName, datafile)
                        packet_data = struct.pack('1s15s20s1024s20s', 's'.encode(), fileName, bfilesize, datafile, data_checksum)
                        
                        send_header=1

                        currentsize = len(datafile)
                        finalsize = finalsize + currentsize

                    else :
                        currentsize = len(datafile)
                        finalsize = finalsize + currentsize

                        bseqNum = seqNum.to_bytes(15, byteorder="big")
                        bfinalsize = finalsize.to_bytes(20, byteorder="big")
                        data_checksum = calChecksum('d', finalsize, bseqNum, datafile)
                        packet_data = struct.pack('1s15s20s1024s20s','d'.encode(), bseqNum, bfinalsize, datafile, data_checksum )
                
                    self.socket.sendto(packet_data, (FLAGS.ip, int(FLAGS.port)))
        
                    sign, addr = self.socket.recvfrom(10)

                    if sign.decode() == '1' or  sign.decode() == '0' :
                        print("(current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")
                        
                        if sign.decode() == '1' :
                            seqNum = 1
                        else :
                            seqNum = 0

                        continue

                    elif sign.decode() == '2' or sign.decode() == "n1" :

                        print("* Received NAK - Retransmit!")
                        while sign.decode() != '1' and  sign.decode() !='0' :
                            self.socket.sendto(packet_data, (FLAGS.ip, int(FLAGS.port)))
                            sign, addr = self.socket.recvfrom(10)

                        print("Retransmission : (current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")

                        
                        if sign.decode() == '1' :
                            seqNum = 1
                        else :
                            seqNum = 0

                        continue

                    elif sign.decode() == '9' :
                        print("* TimeOut !!! ***")
                        while sign.decode() != '1' and sign.decode()!='0' :
                            self.socket.sendto(packet_data, (FLAGS.ip, int(FLAGS.port)))
                            sign, addr = self.socket.recvfrom(10)

                        print("Retransmission : (current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")
                        
                        if sign.decode() == '1' :
                            seqNum = 0
                        else :
                            seqNum = 1

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


