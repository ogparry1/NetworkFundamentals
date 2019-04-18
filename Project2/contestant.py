#!/usr/bin/env python2
from socket import *
import numpy as np
import time
import sys
import re

def debug(message):
    if '-d' in sys.argv:
        print(str(message))

def sendRequest(socket, message):
    socket.send(message.encode())

def getResponse(socket):
    response = socket.recv(2048).decode()
    return response

def buildRequest(arr):
    requestStr = ""
    for e in arr:
        requestStr = requestStr + e + "\\"
    return requestStr[:-1]

def inputName(clientSocket):
    nickname = ''
    while True:
        nickname = raw_input('Please input a nickname: ')
        sendRequest(clientSocket, nickname)
        response = getResponse(clientSocket)
        if response == 'ACK':
            print('Hello' + nickname + ', get ready for contest!')
            break
        else:
            print('Error: Nickname '+ nickname + ' is already in use.')
    return nickname

def makeChoice(choice):
    choice[0] = raw_input('Enter your choice: ')

## Start of the client program ##
# Connect to the server
try:
    serverName = gethostname()
    serverPort = int(sys.argv[1])
except:
    print("Error: Contestant takes exactly 1 arguments\nEx:    ./contestant <portnumber>")
    sys.exit(-1)

try:
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    debug('Connected to Server') 
except Exception as e:
    print ("Error: {}".format(e))
    sys.exit(-1)

name = inputName(clientSocket)
qcount = 0
while True:
    response = str(clientSocket.recv(2048).decode())
    if response in ['EXIT', 'FINISHED']:
        sys.exit(0)
    else:
        qcount += 1
        question = response
        print('\nQuestion {}:'.format(qcount))
        print(question)
        choice = ['NOAN']
        t = thread.start_new_thread(makeChoice, (choice,))
        end = time.time() + 60
        while time.time() < end:
            pass
        t.exit(0)
        sendRequest(clientSocket, choice[0])
        stats = str(clientSocket.recv(2048).decode())
        print(stats)



