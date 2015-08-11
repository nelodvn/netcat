import getopt
from sys import argv
import sys
import socket
import threading
from macerrors import rcvrErr
from __builtin__ import KeyboardInterrupt
from scapy.utils import hexdump
import os

listen = False
command = False
port = 0
target = ""
command = False
upload = False
sockets = []
forever = False
serverSocket = None
fileDest = ""

def handle_connect():
    global port, target
    buffer = sys.stdin.read()
    if len(buffer):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target, port))
        
        s.send(buffer)
        
        temp = s.recv(4096);
        response = ""
        
        while len(temp):
            response += temp
            temp = s.recv(4096);
            
            if len(temp) < 4096:
                response += temp
                break
        
        print response
        handle_connect()
    
    
def readFromClient(client):
    buf = client.recv(4096)
    recvd = ""
    while len(buf):
        recvd += buf
        buf = client.recv(4096)
        if len(buf) < 4096:
            recvd += buf
            break
    return recvd
    
def handle_client(client, addrs):
    global command, sockets, forever, serverSocket, upload, fileDest
    
    print "[*] New connection from %s : %s.\n" % (addrs)
    sockets.append(client)
    
    if not command:
        indForever = 1
        while indForever:
            r = readFromClient(client)
            if not upload:
                print r
            else:
                o = open(fileDest, "w")
                o.write(r)
                
            if not len(r):
                client.close()
                print "[*] %s disconnected." % addrs[0]
                if not forever:
                    break
        serverSocket.close()
        sys.exit(0)
        
def server_loop():
    global port, target, serverSocket
    if not len(target):
            target = "127.0.0.1"
            
    print "[*] Listening on %s:%i" %(target, port)
    try:
        
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        serverSocket.bind((target, port))
        serverSocket.listen(5)
        
        while 1:
            clientSocket, addrs = serverSocket.accept()
            ts = threading.Thread(target=handle_client, args=(clientSocket, addrs))
            ts.start()
    except:
        closeSockets()
        serverSocket.close()
        sys.exit()

def closeSockets():
    global sockets
    for s in sockets:
        s.close()

# this is called by the client
def handle_upload():
    global fileDest, port, target
    o = open(fileDest, "r")
    buffer = o.read()
    if len(buffer):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target, port))
        s.send(buffer)
        
        s.close()
        sys.exit()
    pass

def main():
    global listen, target, port, forever, upload, fileDest
    opts, args = getopt.getopt(argv[1:], "lp:t:u:L", ["listen, port, target, forever, upload"])
    for o, a in opts:
        if o in ("-l", "--listen"):
            listen = True
        elif o in ("-t"):
            target = str(a)
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-L", "--forever"):
            listen, forever = (True, True)
        elif o in ("-u, --upload"):
            upload = True
            fileDest = str(a)

    if upload and not listen:            
        handle_upload()
    if not listen and len(target):
        handle_connect()
    
    if listen:
        server_loop()

if __name__ == '__main__':
    try:
        main()
    except Exception:
        closeSockets()
        
