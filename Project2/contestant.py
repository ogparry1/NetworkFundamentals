#!/usr/bin/env python2
from socket import *
import numpy as np
import threading
import time, sys, re, os

def debug(message):
    if '-d' in sys.argv:
        print(str(message))

def sendRequest(socket, message):
    socket.send(message.encode())

def getResponse(socket):
    res = socket.recv(2048).decode()
    return res

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
        res = getResponse(clientSocket)
        print(res)
        if res[0:5] == 'Hello':
            break
    return nickname

def makeChoice(socket, stats):
    choice = raw_input('Enter your choice: ')
    sendRequest(socket, choice)
    stats = getResponse(socket)
    print(stats)
    return

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

def exitListen(socket):
    while True:
        # with listen_lock:
        response = str(clientSocket.recv(2048).decode())
        if response.find('EXIT') != -1 or response.find('FINISHED') != -1:
            print('The contest is over - thanks for playing {}!'.format(name))
            os._exit(0)
        else:
            time.sleep(1)

name = inputName(clientSocket)
qcount = 0
stats = ''
while True:
    response = getResponse(clientSocket)
    if response.find('EXIT') != -1 or response.find('FINISHED') != -1:
        print('The contest is over - thanks for playing {}!'.format(name))
        os._exit(0)
    qcount += 1
    print('Question {}:\n{}'.format(qcount, response))
    t = threading.Thread(target = makeChoice, args = (clientSocket,stats))
    t.daemon = True
    t.start()
    t.join(60.0)
    print('\n'+stats)
