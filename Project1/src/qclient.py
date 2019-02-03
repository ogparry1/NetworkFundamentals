from socket import *
import numpy as np
import sys
import re

d = True if '-d' in sys.argv else False

# Connect to the server
serverName = ''
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
print ('Connected to Server')

def debug(call, req, resp):
    if d:
        print('Call: '+ call+'\tRequest: '+req+'\tResponse: '+resp)
    return resp

def error(call, req, message):
    if d:
        print('Call: '+ call+'\tRequest: '+req+'\tError: '+message)
    return message
    
def sendRequest(socket, message):
    debug('sendRequest',message,'N/A')
    socket.send(message.encode())

def sendArgumentsTo(socket, args):
    for arg in args:
        sendRequest(socket,arg)
    return debug('sendArgumentsTo','None',0)

def getResponseTo(socket, request, have):
    req = request[0]
    sendRequest(socket,req)
    need = socket.recv(1024).decode()
    if have == need:
        sendRequest(socket, 'OK')
    else:
        sendArguments(socket, request[1:


    resp = getResponseTo(socket, req)
    if resp != 'OK':
        return error('getResponseTo',req,resp)
    resp = getResponseTo(socket, arglen)
    if resp != 'READY':
        return error('getResponseTo',req,resp)
    return debug('getResponseTo',req,'READY')
    err = 'INVALID_REQUEST\nFor help, enter [h].'
    return error('getResponseTo', req, err)


## Start of the client program ##
while True:
    request = re.split(' ', raw_input('> '))
    req = request[0]

    if req in ['k','q']:
        resp = getResponseTo(clientSocket,request,'ARGS_0')
        debug('main',req,resp)
        clientSocket.close()
        break
    elif req in ['h','r']:
        resp = getResponseTo(clientSocket,request,'ARGS_0')
    elif req in ['d','g']:
        resp = getResponseTo(clientSocket,request,'ARGS_1')
    elif req in ['c']:
        resp = getResponseTo(clientSocket,request,'ARGS_2')
    elif req == 'p':
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
        newQuestion = [req,tags,question,a,b,c,d,correct]
        resp = getResponseTo(clientSocket, newQuestion,'ARGS_7')
    else:
        resp = sendArgumentsTo(clientSocket, args)
    print(debug('main',req,resp))
