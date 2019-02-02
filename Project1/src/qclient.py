from socket import *
import numpy as np
import re

# Connect to the server
serverName = ''
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
print ('Connected to Server')

# Make the request and receive the response
while True:
    user_input = re.split(' ', raw_input('> '))
    req = user_input[0]
    args = (len(user_input) > 1 ? user_input[1:len(user_input)] : [])
    resp = sendRequest(clientSocket, req, len(args))

    if resp == -1:
        continue
    elif req in ['k','q']:
        clientSocket.close()
        break
    elif req == 'p':
        tags = raw_input('')
        question = raw_input('')
        print('.')
        a = raw_input('(a) ')
        print('.')
        b = raw_input('(a) ')
        print('.')
        c = raw_input('(a) ')
        print('.')
        d = raw_input('(a) ')
        print('.\n.')
        correct = raw_input('')
        newQuestion = [tags,question,a,b,c,d,correct]
        resp = sendArgumentsTo(clientSocket, newQuestion)
    else:
        resp = sendArgumentsTo(clientSocket, args)

    print(resp)


def sendRequest(socket, req, arglen):
    if req in ['k','q','p','d','g','r','c','h']:
        resp = getResponseTo(socket, req)
        if resp != 'OK':
            print('Error: ', resp)
            return -1
        resp = getResponseTo(socket, arglen)
        if resp != 'READY':
            print('Error: ', resp)
            return -1
        return 'READY'
    else:
        print ('Error: INVALID_REQUEST')
        print ('For help, enter [h].')
        return -1

def sendArgumentsTo(socket, args):
    for arg in args:
        

def getResponseTo(socket, req):
    socket.send(req.encode())
    response = socket.recv(1024).decode()
    return response
