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
def sendResponse(socket, message):
    socket.send(message.encode())

def getRequest(socket):
    req = socket.recv(1024).decode() 
    result = re.split('\\\\',req)
    return result

def buildResponse(arr):
    response = ''
    for e in arr:
        response = response + e + '\n'
    return response

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
        if req == 'k':
            sendResponse(connectionSocket,'EXIT')
            connectionSocket.close()
            terminate = True
            break
        elif req == 'q':
            sendResponse(connectionSocket,'EXIT')
            connectionSocket.close()
            break
        elif req == 'p':
            tags = re.split(',|, ', request[1])
            question = request[2]
            answers = request[3:6]
            correct = request[7]
            response = buildResponse(request)

            # temporary response
            sendResponse(connectionSocket, response)
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
        elif req == 'h':
            # temporary response
            sendResponse(connectionSocket, req)
        else:
            continue
