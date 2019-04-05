from socket import *
import numpy as np
import sys
import re

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

def inputName():
    while True:
        nickname = raw_input('Please input a nickname: ')
        sendRequest(clientSocket, request)
        response = getResponse(clientSocket)
        if response == 'ACK':
            return nickname


print (inputName())
exit(0)

## Start of the client program ##
# Connect to the server
try:
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
except:
    print("Error: contestant takes exactly 2 arguments\nEx:    contestant <hostname> <portnumber>")
    sys.exit(-1)

try:
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    print ('Connected to Server')
except Exception as e:
    print ("Error: " + str(e))
    sys.exit(-1)

# Interface with server
name = inputName()
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
