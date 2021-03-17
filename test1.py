from socket import socket, AF_INET, SOCK_DGRAM, inet_aton, inet_ntoa
import time


def to_packet(dst_addr,src_addr, seq_num, seq_ack, checksum, SYN, FIN, payload):
    # 0-7 dst; 8-15 src;16 FIN & SYN;seq_num
    pkt = bytes()
    pkt += addr_to_bytes(dst_addr)
    pkt += addr_to_bytes(src_addr)
    if SYN and not FIN:
        pkt += b'\x08'
    elif not SYN and FIN:
        pkt += b'\x04'
    else:
        pkt += b'\x00'
    pkt += seq_num.to_bytes(4, 'big')
    pkt += seq_ack.to_bytes(4, 'big')
 #   pkt += len(data).to_bytes(4, 'big')
    pkt += checksum.to_bytes(2, 'big')
#    data = payload.encode()
    data = bytes(payload, encoding='utf8')
    pkt += len(data).to_bytes(4, 'big')
    pkt += data
    return pkt

def packet_analysis(pkt):
    dst_addr = bytes_to_addr(pkt[:8])
    src_addr = bytes_to_addr(pkt[8:16])
    c = pkt[16]
    if pkt[16] == 8:
        SYN = True
        FIN = False
    elif pkt[16] == 4:
        SYN = False
        FIN = True
    else:
        SYN = False
        FIN = False
    seq_num = int.from_bytes(pkt[17:21], 'big')
    seq_ack = int.from_bytes(pkt[21:25], 'big')
    checksum = int.from_bytes(pkt[25:27], 'big')
    length = int.from_bytes(pkt[27:31], 'big')
#    data = pkt[31:].decode()
    data = bytes.decode(pkt[31:])
    print('dst_addr: ', dst_addr)
    print('src_addr: ', src_addr)
    print('FIN: ', FIN)
    print('SYN: ', SYN)
    print('seq_num: ', seq_num)
    print('seq_ack: ', seq_ack)
    print('checksum: ', checksum)
    print('data length: ', length)
    print('data: ', data)
    return dst_addr, src_addr, FIN, SYN, seq_num, seq_ack, checksum, length, data



def bytes_to_addr(bytes):
    p1 = int.from_bytes(bytes[0: 1], 'big')
    p2 = int.from_bytes(bytes[1: 2], 'big')
    p3 = int.from_bytes(bytes[2: 3], 'big')
    p4 = int.from_bytes(bytes[3: 4], 'big')
    ip_address = str(p1) + '.' + str(p2) + '.' + str(p3) + '.' + str(p4)
    port = int.from_bytes(bytes[4:8], 'big')
    return ip_address, port


def addr_to_bytes(addr):
    parts = addr[0].split('.')
    result = b''
    for part in parts:
        result += int(part).to_bytes(1, 'big')
    result += addr[1].to_bytes(4, 'big')
    return result

x = to_packet(('127.0.0.1', 8080),('192.168.0.1', 8080),70,1002,53,True, False, 'woejddajdhfbjsidhfjsjdhfjhfsjkdhsh')
print(x)
packet_analysis(x)