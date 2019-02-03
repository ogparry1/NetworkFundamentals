from socket import *
import sys
import re
import json

terminate = False
d = True if '-d' in sys.argv else False

serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)

## Server Functions ##

def debug(call, req, resp):
    if d:
        print ('Call: ' + call + '\tRecieved: ' + req + '\tResponse: ' + resp)
    return resp

def error(call, req, message):
    if d:
        print ('Call: ' + call + '\tRecieved: ' + req + '\tError: ' + message)
    return message

def sendResponse(socket, message):
    debug('sendResponse', 'N/A', message)
    socket.send(message.encode())

def getArguments(socket, need, have, argnum):
    # loop through receiving all arguments
    arguments = []
    for i in range(argnum):
        resp = socket.recv(1024).decode() 
        arguments = arguments + resp
    return arguments

def getRequest(socket):
    # get request type
    req = socket.recv(1024).decode() 
    request = [req]
    if req in ['k','q','h','r']:
        resp = debug('getRequest', req, 'ARGS_0')
        sendResponse(socket, resp)
        req = socket.recv(1024).decode()
        if req == 'OK':
            args = getArguments(socket, 0)
            request = request + args
    elif req in ['d','g']:
        resp = debug('getRequest', req, 'ARGS_1')
        sendResponse(socket, resp)
        req = socket.recv(1024).decode() 
        if req == 'OK':
            args = getArguments(socket, 1)
            request = request + args
    elif req in ['c']:
        resp = debug('getRequest', req, 'ARGS_2')
        sendResponse(socket, resp)
        req = socket.recv(1024).decode() 
        if req == 'OK':
            args = getArguments(socket, 2)
            request = request + args
    elif req in ['p']:
        resp = debug('getRequest', req, 'ARGS_7')
        sendResponse(socket, resp)
        req = socket.recv(1024).decode() 
        if req == 'OK':
            args = getArguments(socket, 7)
            request = request + args
    else:
        resp = error('getRequest', req, 'INVALID_REQUEST')
        sendResponse(socket, resp)
        return resp
    return request

def helpPage():
    debug('helpPage', 'N/A', 'N/A')
    helpPage = 'Help Page Goes Here'
    return helpPage


## Start of the Program ##

print('The server is ready to receive')
while True:
    if terminate:
        break

    connectionSocket, addr = serverSocket.accept()
    print('Connected to Client')

    while True:
        # Get a request
        request = getRequest(connectionSocket)
        req = request[0]

        # Take arguments and service the request
        if req == 'INVALID_REQUEST' or req == 'INVALID_ARGS':
            continue
        elif req == 'k':
            sendResponse(connectionSocket,'OK')
            connectionSocket.close()
            terminate = True
            break
        elif req == 'q':
            sendResponse(connectionSocket,'OK')
            connectionSocket.close()
            break
        elif req == 'p':
            tags = re.split(',|, ', request[1])
            question = request[2]
            answers = request[3:6]
            correct = request[7]

            # temporary response
            sendResponse(connectionSocket, req)
        elif req == 'd':
            # temporary response
            sendResponse(connectionSocket, req)
        elif req == 'g':
            # temporary response
            sendResponse(connectionSocket, req)
        elif req == 'c':
            # temporary response
            sendResponse(connectionSocket, req)
        elif req == 'r':
            # temporary response
            sendResponse(connectionSocket, req)
        else:
            sendResponse(helpPage())
