import socket
import hashlib
import os

FLAGS = None
class ClientSocket():

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def socket_send(self):
        fileName = input("Input your file name : ")
        print("File Transmit Start....")
        #ip address must be edited
        #send file name
        self.socket.sendto(fileName.encode(), (FLAGS.ip, int(FLAGS.port)))
        #ip address must be edited
        #send file size
        filesize = os.path.getsize(fileName)
        self.socket.sendto(str(filesize).encode(), (FLAGS.ip, int(FLAGS.port)))
        
        readfile = open(fileName, 'rb')

        finalsize = 0
        while True:
                try:
                    datafile = readfile.read(1024)
            
                    if finalsize==filesize:
                        readfile.close()
                        break
                    #ip address must be edited
                    self.socket.sendto(datafile, (FLAGS.ip, int(FLAGS.port)))
                    currentsize = len(datafile)
                    finalsize = finalsize + currentsize
        
                    print("current_size / total_size = ",finalsize,"/",filesize,", ",finalsize/filesize*100,"%") 

                except:
                    print("replay")
                    break

        print("ok")
        print("file_send_end")

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


