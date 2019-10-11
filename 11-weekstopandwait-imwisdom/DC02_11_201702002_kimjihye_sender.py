import socket
import os
import struct

FLAGS = None
finalsize = 0
class ClientSocket():

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('192.168.0.69', int(FLAGS.port)))
    
    def socket_send(self):

        print("Sender Socket open...")
        print("Receiver IP = ",(FLAGS.ip))
        print("Receiver Port = ",int(FLAGS.port))

        fileName = input("Input File Name : ")
        filesize = os.path.getsize(fileName)

        bfilesize = filesize
        print("Send File Info(file name, file size, seqNum) to Server...")

        send_header = 0
        readfile = open(fileName, 'rb')

        def calChecksum(idtype, length, n, payload):
            
            idtype = int.from_bytes(idtype.encode(), "big")
            n = int.from_bytes(n.encode(), "big")
            
            checksum = idtype + length + n

            for i in payload :
                checksum = checksum + i

            checksum = checksum.to_bytes(20, byteorder="big")

            return checksum

        def send_frame(seqNum, datafile) :
           
            global finalsize
            finalsize = finalsize + len(datafile)
            bseqNum = seqNum.to_bytes(15, byteorder="big")
            bfinalsize = finalsize.to_bytes(20, byteorder="big")
            data_checksum = calChecksum('d', finalsize, bseqNum.decode(), datafile)
        
            packet_data = struct.pack('1s15s20s1024s20s', 'd'.encode(), bseqNum, bfinalsize, datafile, data_checksum)
            print("(current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")

            return packet_data

        windex = 0
        sign = 0
        one_frame = ''

        while True:
                #try:
                    
                    global finalsize
                    if finalsize==filesize:
                        
                        readfile.close()
                        break
                    
                    #send
                    if send_header == 0 :
                        print("header only") 
                        datafile = readfile.read(1024)
                        
                        #file name (15byte)
                        fileName = fileName.rjust(15, '\x00')
                        fileName = fileName.encode()
        
                        #file size (20byte)
                        bfilesize = bfilesize.to_bytes(20, byteorder="big")
                        
                        print("Start File send")
                        data_checksum = calChecksum('s',filesize, fileName.decode(), datafile)
                        packet_header = struct.pack('1s15s20s1024s20s', 's'.encode(), fileName, bfilesize, datafile, data_checksum)

                        finalsize = finalsize + len(datafile)
                        print("(current_size / total_size) = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%")

                        datafile = readfile.read(1024)
                        send_one = send_frame(1, datafile)
                        datafile = readfile.read(1024)
                        send_two = send_frame(2, datafile)
                        datafile = readfile.read(1024)
                        send_three = send_frame(3, datafile)

                        packet_frame = [packet_header, send_one, send_two, send_three]

                        for i in packet_frame :
                            self.socket.sendto(i, (FLAGS.ip, int(FLAGS.port)))
        
                        sign, addr = self.socket.recvfrom(10)

                        if sign.decode() == '9':
                            print("**** Timeout!! ****")
                            print("** Check seqNum and Retransmission From", windex%8,"**")

                            while sign.decode() == '9' :

                                for i in packet_frame :
                                    self.socket.sendto(i, (FLAGS.ip, int(FLAGS.port)))
                                sign, addr = self.socket.recvfrom(10)
                        send_header = 1        

                    if sign.decode() != '9' :

                        windex = windex+1
                        
                        print("\n**** Window Change! ****")
                        pre_window = [windex%8, (windex+1)%8, (windex+2)%8, (windex+3)%8]
                        print("Present Window : ",pre_window)
                        
                        datafile = readfile.read(1024)
                        one_frame = send_frame(int(sign.decode()), datafile)
                        
                        self.socket.sendto(one_frame,(FLAGS.ip, int(FLAGS.port)))
                        sign, addr = self.socket.recvfrom(10)
                    else :
                        print("\n**** Timeout!! ****")
                        print("** Check seqNum and Retransmission From ", windex%8, "**")

                        while sign.decode() == '9' :
                            self.socket.sendto(one_frame,(FLAGS.ip, int(FLAGS.port)))
                            sign, addr = self.socket.recvfrom(10)



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


