from socket import *
import numpy as np
import sys
import re

d = True if '-d' in sys.argv else False

# Connect to the server
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
print ('Connected to Server')

def sendRequest(socket, message):
    socket.send(message.encode())

def getResponse(socket):
    response = socket.recv(1024).decode()
    return response

def buildRequest(arr):
    requestStr = ""
    for e in arr:
        requestStr = requestStr + e + "\\"
    return requestStr[:-1]

## Start of the client program ##
while True:
    request = re.split(' ', raw_input('> '))
    req = request[0]

    if req == 'p':
        tags = raw_input('')
        question = raw_input('')
        print('.')
        a = raw_input('(a) ')
        print('.')
        b = raw_input('(b) ')
        print('.')
        c = raw_input('(c) ')
        print('.')
        d = raw_input('(d) ')
        print('.\n.')
        correct = raw_input('')
        request = [req,tags,question,a,b,c,d,correct]

    request = buildRequest(request)
    sendRequest(clientSocket, request)
    response = getResponse(clientSocket)
    if response == 'EXIT':
        clientSocket.close()
        break
    else:
        print(response)
