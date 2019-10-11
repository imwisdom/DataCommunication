import socket
FLAGS = None
class ClientSocket():

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def socket_send(self):
        ID = input("학번을 입력하세요 : ")
        self.socket.sendto(ID.encode(), ('192.168.0.105', int(9500)))
        print("send complete")
        data, addr = self.socket.recvfrom(2000)

        print(data.decode())
        while True:
            if data.decode() == "게임을 시작합니다.":
                try:
                    input_game = input("[0]가위 [1]바위 [2]보 중에 하나를 입력하세요 :")
                    input_game = int(input_game)

                    if input_game > 2 :
                        print("wrong number")
                        continue;

                except:
                    print("다시 입력하세요")
                    continue;

                send_str = "game "+ID+" "+str(input_game)

                self.socket.sendto(send_str.encode(), ('192.168.0.105', int(9500)))
                print("send complete")
                data, addr = self.socket.recvfrom(2000)

                print(data.decode())

            else :
                break
        self.socket.close()

        print(data.decode)

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

