from socket import *
import re
import json

terminate = False

serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)

print('The server is ready to receive')
while True:
    if terminate:
        break

    connectionSocket, addr = serverSocket.accept()
    print ('Connected to Client')

    while True:
        # Get a request
        req = getRequest(connectionSocket)

        # Take arguments and service the request
        if req == -1:
            continue
        elif req == 'k':
            args = getArguments(connectionSocket, 0)
            connectionSocket.close()
            terminate = True
            break
        elif req == 'q':
            args = getArguments(connectionSocket, 0)
            connectionSocket.close()
            break
        elif req == 'p':
            args = getArguments(connectionSocket, 7)
            tags = re.split(',|, ', args[0])
            question = args[1]
            answers = args[2:5]
            correct = args[6]

            # Create a persistent entry for the question and return the number of the question
            tempNum = 1
            sendResponse(connectionSocket, tempNum)
        elif req == 'd':
            args = getArguments(connectionSocket, 1)

            # temporary response
            tempNum = 1
            sendResponse(connectionSocket, tempNum)
        elif req == 'g':
            args = getArguments(connectionSocket, 1)

            # temporary response
            tempNum = 1
            sendResponse(connectionSocket, tempNum)
        elif req == 'c':
            args = getArguments(connectionSocket, 2)

            # temporary response
            tempNum = 1
            sendResponse(connectionSocket, tempNum)
        elif req == 'r':
            args = getArguments(connectionSocket, 0)

            # temporary response
            tempNum = 1
            sendResponse(connectionSocket, tempNum)
        else:
            args = getArguments(connectionSocket, 0)
            sendResponse(helpPage())


def getRequest(socket):
    req = socket.recv(1024).decode() 
    sendResponse(socket,'OK')
    reqnum = socket.recv(1024).decode() 
    if req in ['k','q','h','r'] and reqnum == 0:
        sendResponse(socket, 'READY')
        return -1
    elif req in ['d','g'] and reqnum == 1:
    elif req in ['c'] and reqnum == 2:
    elif req in ['p'] and reqnum == 7:
    else:
        sendResponse(socket, 'INVALID_NUM_ARGS')
        return -1

def getArguments(socket, numNeeded):
    resp = socket.recv(1024).decode() 
    arguments = []
    if resp < numNeeded:
        sendResponse(socket, 'INSUFFICIENT_ARGUMENTS')
        return -1
    elif resp > numNeeded:
        sendResponse(socket, 'TOO_MANY_ARGUMENTS')
        return -1
    else:
        sendResponse(socket, 'READY')
        for i in range(numNeeded):
            resp = socket.recv(1024).decode() 
            arguments = arguments + resp
            sendResponse(socket, 'RECEIVED')
        return arguments

def sendResponse(socket, message):
    socket.send(message.encode())

def helpPage():
    helpPage = 'Help Page Goes Here'
    return helpPage
