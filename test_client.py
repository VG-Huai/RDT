from rdt import RDTSocket
from socket import socket, AF_INET, SOCK_STREAM
import time
from difflib import Differ

if __name__=='__main__':
    client = RDTSocket()
    #client = socket(AF_INET, SOCK_STREAM) # check what python socket does
    client.connect(('127.0.0.1', 9999))