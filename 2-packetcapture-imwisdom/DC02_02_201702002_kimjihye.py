import socket
import struct


print("<<<<<<Packet Capture Start>>>>>>")

def parsing_ethernet_header(data):
    ethernet_header = struct.unpack("!6c6c2s", data)
    ether_dest = convert_ethernet_address(ethernet_header[0:6])
    ether_src = convert_ethernet_address(ethernet_header[6:12])
    ip_type = "0x"+ethernet_header[12].hex()

    print("======ethernet header======")
    print("src_mac_address: ", ether_src)
    print("dest_mac_address: ", ether_dest)
    print("ip_version: ", ip_type)

def convert_ethernet_address(data):
    ethernet_addr = list()
    for i in data:
        ethernet_addr.append(i.hex())
    ethernet_addr = ":".join(ethernet_addr)
    return ethernet_addr

def parsing_ip_header(data):
    
    print("======ip header======")
    ip_header = struct.unpack("!1s1s7B1s1s1s4B4B", data)
    
    print("ip_version: " , ip_header[0].hex()[0])
    print("ip_length: " , (ip_header[0].hex()[1]))

    print("differentiated_service_codepoint: " , (ip_header[1].hex()[0]))
    print("explicit_congestion_notification: " , (ip_header[1].hex()[1]))
    
    print("total_length: ", (ip_header[2]*16*16+ip_header[3])) 
    print("identification: ", ip_header[4]*16*16+ip_header[5])

    flagdata = ip_header[6]*16*16+ip_header[7]
    print("flags: ","0x"+ data[6:8].hex())
    flagbin = "{0:b}".format(flagdata).zfill(16)
    print(">>>reserved_bit: ", flagbin[0])
    print(">>>not_fragments: ", flagbin[1])
    print(">>>fragments: ", flagbin[2])
    print(">>>fragments_offset: ", (flagdata & 0x1fff))
    
    print("Time to live: ", ip_header[8])
    print("protocol: ", ip_header[9].hex())
    print("header checksum: ", "0x"+ip_header[10].hex()+ip_header[11].hex())

    ip_src = convert_ip_address(ip_header[12:16])
    ip_dest = convert_ip_address(ip_header[16:20])

    print("source_ip_address: ", ip_src)
    print("dest_ip_address: ", ip_dest)

def convert_ip_address(data):
    ip_addr = list()
    for i in data:
        ip_addr.append(str(i))
    ip_addr = ".".join(ip_addr)
    return ip_addr

def parsing_tcp_header(data):
    print("======tcp_header======")

    tcp_header = struct.unpack("!2B2BII2B2B2B2B", data)
    
    print("src_port: ", tcp_header[0]*16*16+tcp_header[1])
    print("dst_port: ", tcp_header[2]*16*16+tcp_header[3])
    
    print("seq_num: ", tcp_header[4])
    print("ack_num: ", tcp_header[5])
    print("header_len: ", (int)(tcp_header[6]/16))
    print("flags: ", (tcp_header[6]%16)*16*16+tcp_header[7])

    flagdata = (tcp_header[6]%16)*16*16+tcp_header[7]
    flagbin = "{0:b}".format(flagdata).zfill(12)

    print(">>>reserved: ", flagbin[0:3])
    print(">>>nonce: ", flagbin[3])
    print(">>>cwr: ", flagbin[4])
    print(">>>ecn: ", flagbin[5])
    print(">>>urgent: ", flagbin[6])
    print(">>>ack: ", flagbin[7])
    print(">>>push: ", flagbin[8])
    print(">>>reset: ", flagbin[9])
    print(">>>syn: ", flagbin[10])
    print(">>>fin: ", flagbin[11])

    print("window_size_value: ", tcp_header[8]*16*16+tcp_header[9])
    print("checksum: ", tcp_header[10]*16*16+tcp_header[11])
    print("urgent_pointer: ", tcp_header[12]*16*16+tcp_header[13])


def parsing_udp_header(data):
    print("======udp_header======")

    udp_header = struct.unpack("2B2B2B1s1s",data)
    print("src_port: ", udp_header[0]*16*16+udp_header[1])
    print("dst_port: ", udp_header[2]*16*16+udp_header[3])
    print("leng: ", udp_header[4]*16*16+udp_header[5])
    print("header checksum: ", "0x"+udp_header[6].hex()+udp_header[7].hex())

recv_socket = socket.socket(socket.AF_PACKET,socket.SOCK_RAW, socket.ntohs(0x800))
while True:
      data = recv_socket.recvfrom(65565)
      parsing_ethernet_header(data[0][0:14])
      parsing_ip_header(data[0][14:34])
      ptc = data[0][23]
      if ptc==6:
        parsing_tcp_header(data[0][34:54])
      elif ptc==17:
        parsing_udp_header(data[0][34:42])















