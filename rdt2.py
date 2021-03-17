from USocket import UnreliableSocket

import threading
import time
import math
import queue
import random


class RDTSocket(UnreliableSocket):
    """
    The functions with which you are to build your RDT.
    -   recvfrom(bufsize)->bytes, addr
    -   sendto(bytes, address)
    -   bind(address)

    You can set the mode of the socket.
    -   settimeout(timeout)
    -   setblocking(flag)
    By default, a socket is created in the blocking mode.
    https://docs.python.org/3/library/socket.html#socket-timeouts

    """

    def __init__(self, rate=None, debug=True):
        super().__init__(rate=rate)
        self._rate = rate
        self._send_to = None
        self._recv_from = None
        self.debug = debug
        self.syn = False
        self.conn_address = ('127.0.0.1', random.randint(23455, 36780))
        self.own_address = ('127.0.0.1', 9999)
        self.buffer = queue.Queue(10)
        self.ack_buffer = queue.Queue(10)
        self.conn = None
        self.timeout = 0.1
        self.seq_Num = 0
        self.seq_Ack = 0
        self.acked_seq_num = 0
        self.recved_data = bytes()

        #############################################################################
        # TODO: ADD YOUR NECESSARY ATTRIBUTES HERE
        #############################################################################

        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################

    def accept(self) -> ('RDTSocket', (str, int)):
        """
        Accept a connection. The socket must be bound to an address and listening for
        connections. The return value is a pair (conn, address) where conn is a new
        socket object usable to send and receive data on the connection, and address
        is the address bound to the socket on the other end of the connection.

        This function should be blocking.
        """
        conn, addr = RDTSocket(self._rate), None
        conn.bind(self.conn_address)
        thread = threading.Thread(target=self.recving)
        thread.start()
        thread = threading.Thread(target=conn.recving)
        thread.start()
        #############################################################################
        # TODO: YOUR CODE HERE                                                      #
        while True:
            time.sleep(0.01)
            if not conn.syn and not self.buffer.qsize() == 0:
                data, src_addr = self.buffer.get()
                dst_addr, src_addr1, FIN, SYN, seq_num, seq_ack, checksum, length, is_ack, data = packet_analysis(data)
                if SYN and check_packet():
                    conn._recv_from = src_addr
                else:
                    continue
                # handshake
                pkt = to_packet(src_addr, self.conn_address, 1, 1, 233, True, False, False, b'')
                conn.sendto(pkt, src_addr)
                # conn.recving
                while True:
                    print('conn.buffer.qsize() = ' + str(conn.buffer.qsize()))
                    if conn.buffer.qsize() > 0:
                        data, src_addr = conn.buffer.get()
                        dst_addr, src_addr1, FIN, SYN, seq_num, seq_ack, checksum, length, is_ack, data = packet_analysis(
                            data)
                    else:
                        time.sleep(0.5)
                        continue
                    if src_addr == conn._recv_from and SYN and seq_ack == 1 and check_packet():
                        conn.syn = True
                        conn._send_to = src_addr
                        conn._recv_from = src_addr
                        conn.seq_Num = 1
                        conn.seq_Ack = 1
                        conn.acked_seq_num = 1
                        print('accept handshake successfully')
                        break
                    else:
                        conn.sendto(pkt, src_addr)
                break

        #############################################################################

        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################
        return conn, conn._recv_from

    def connect(self, address: (str, int)):
        """
        Connect to a remote socket at address.
        Corresponds to the process of establishing a connection on the client side.
        """
        #############################################################################
        # TODO: YOUR CODE HERE                                                      #
        #############################################################################
        self.bind(('127.0.0.1', random.randint(12346, 13500)))
        thread = threading.Thread(target=self.recving)
        thread.start()
        pkt = to_packet(address, ('0.0.0.0', 0), 1, 1, 233, True, False, False, b'')
        while True:
            if not self.syn:
                self.sendto(pkt, address)
                while True:
                    if self.buffer.qsize() == 0:
                        self.sendto(pkt, address)
                        time.sleep(0.01)
                        continue
                    data, src_addr = self.buffer.get()
                    dst_addr, src_addr1, FIN, SYN, seq_num, seq_ack, checksum, length, is_ack, data = \
                        packet_analysis(data)
                    pkt1 = to_packet(src_addr, ('0.0.0.0', 0), 1, 1, 233, True, False, False, b'')
                    if SYN and seq_ack == 1 and check_packet():
                        self.syn = True
                        self._send_to = src_addr
                        self._recv_from = src_addr
                        print('accept new conn port')
                        self.seq_Num = 1
                        self.seq_Ack = 1
                        self.acked_seq_num = 1
                        for i in range(5):
                            time.sleep(0.01)
                            self.sendto(pkt1, src_addr)
                        # 这里应该重复确认
                        break
                break

        # raise NotImplementedError()
        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################

    def recv(self, bufsize: int) -> bytes:
        """
        Receive data from the socket.
        The return value is a bytes object representing the data received.
        The maximum amount of data to be received at once is specified by bufsize.

        Note that ONLY data send by the peer should be accepted.
        In other words, if someone else sends data to you from another address,
        it MUST NOT affect the data returned by this function.
        """
        data = None
        assert self._recv_from, "Connection not established yet. Use recvfrom instead."
        #############################################################################
        # TODO: YOUR CODE HERE                                                      #
        '''
        data = bytes()
        while not self.buffer.qsize() == 0:
            # print('waiting for packets')
            data, src_addr = self.buffer.get()
            dst_addr, src_addr1, FIN, SYN, seq_num, seq_ack, checksum, length, is_ack, analysised_data = packet_analysis(
                data)
            if not FIN:
                data += analysised_data
            elif FIN:
                self.close()
            time.sleep(0.01)
        return data
        '''
        return self.recved_data
        #############################################################################

        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################

    def send(self, bytes: bytes):
        """
        Send data to the socket.
        The socket must be connected to a remote socket, i.e. self._send_to must not be none.
        """
        assert self._send_to, "Connection not established yet. Use sendto instead."
        #############################################################################
        # TODO: YOUR CODE HERE                                                      #
        slices_num = int(len(bytes)/150)
        for i in range(slices_num):
            self.seq_Num += 1
            pkt = to_packet(self._send_to, ('0.0.0.0', 0), self.seq_Num, self.seq_Ack, 233, False, False, False, bytes[i*150: min((i+1) * 150, len(bytes))])
            print(bytes[i*150: min((i+1) * 150, len(bytes))])
            self.sendto(pkt, self._send_to)
            print('send a not ack pkt, seq_num = ' + str(self.seq_Num))
            time.sleep(0.01)
            while True:
                print('in loop')
                if not self.ack_buffer.qsize() == 0:
                    data, src_addr = self.ack_buffer.get()
                    print("\n send")
                    dst_addr, src_addr1, FIN, SYN, seq_num, seq_ack, checksum, length, is_ack, analysised_data = packet_analysis(
                        data)
                    print(FIN)
                    if not FIN:
                        if seq_ack >= self.seq_Num:
                            print('here')
                            self.acked_seq_num = seq_ack
                            break
                        else:
                            print('?')
                    else:
                        self.close()
                else:
                    print('send pkt to: ' + str(self._send_to))
                    self.sendto(pkt, self._send_to)
                    time.sleep(0.01)

        #############################################################################
        # raise NotImplementedError()
        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################

    def close(self):
        """
        Finish the connection and release resources. For simplicity, assume that
        after a socket is closed, neither futher sends nor receives are allowed.
        """
        #############################################################################
        # TODO: YOUR CODE HERE                                                      #
        #############################################################################

        #############################################################################
        #                             END OF YOUR CODE                              #
        #############################################################################
   #     super().close()

    def set_send_to(self, send_to):
        self._send_to = send_to

    def set_recv_from(self, recv_from):
        self._recv_from = recv_from

    def recving(self):
        while True:
            data, src_addr = self.recvfrom(512)
            dst_addr, src_addr1, FIN, SYN, seq_num, seq_ack, checksum, length, is_ack, analysised_data = packet_analysis(
                data)
            if not is_ack:
                if self.buffer.qsize() == 10:
                    time.sleep(0.01)
                    continue
                print('\n recv a not_ack pkt: seq num = ' + str(seq_num))
                if seq_num > self.acked_seq_num and check_packet():
                    self.buffer.put((data, src_addr))
                    if seq_num > 1:
                        self.recved_data += analysised_data
                    self.acked_seq_num = seq_num
                pkt = to_packet(src_addr, ('0.0.0.0', 0), self.seq_Num, self.acked_seq_num, 233, False, False,
                                True,
                                b'')
                print('\n send an ack pkt: ack ' + str(self.acked_seq_num))
                self.sendto(pkt, src_addr)
            else:
                if self.ack_buffer.qsize() == 10:
                    time.sleep(0.01)
                    continue
                if seq_ack < self.seq_Num or not check_packet():
                    continue
                print('\n recv an ack pkt: ack' + str(self.acked_seq_num))
                self.ack_buffer.put((data, src_addr))


"""
You can define additional functions and classes to do thing such as packing/unpacking packets, or threading.
"""


def max(a, b):
    if a > b:
        return a
    return b
def min(a, b):
    if a < b:
        return a
    return b


def check_packet():
    return True


def to_packet(dst_addr, src_addr, seq_num, seq_ack, checksum, SYN, FIN, is_ack, payload):
    # 0-7 dst; 8-15 src;16 FIN & SYN;seq_num
    pkt = bytes()
    pkt += addr_to_bytes(src_addr)
    pkt += addr_to_bytes(dst_addr)
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
    pkt += len(payload).to_bytes(4, 'big')
    if is_ack:
        pkt += b'\x05'
    else:
        pkt += b'\x00'
    pkt += payload
    return pkt


def packet_analysis(pkt):
    dst_addr = bytes_to_addr(pkt[8:16])
    src_addr = bytes_to_addr(pkt[0:8])
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
    data = pkt[32:]
    if pkt[31] == 5:
        is_ack = True
    else:
        is_ack = False
    return dst_addr, src_addr, FIN, SYN, seq_num, seq_ack, checksum, length, is_ack, data


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