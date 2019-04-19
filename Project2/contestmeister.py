#!/usr/bin/env python2
from socket import *
import numpy as np
import thread
import time
import sys, os
import re

def verbose(message):
    if '-v' in sys.argv:
        print(message)

def debug(message):
    if '-d' in sys.argv:
        print(message)

def sendRequest(socket, message):
    socket.send(message.encode())

def getResponse(socket):
    response = socket.recv(2048).decode()
    return response

def buildRequest(reqarr):
    requestStr = ""
    for arr in reqarr:
        for e in arr:
            requestStr = requestStr + e + "\n"
    return requestStr[:-1]

def printRequest(reqarr):
    requestStr = ""
    for arr in reqarr:
        for e in arr:
            requestStr = requestStr + e + "\n"
    print(requestStr[:-1])

def getValidChoices():
    choices = {}
    while True:
        choice = raw_input('')
        if choice == '.':
            if len(choices) == 0:
                print('Please supply at least 1 choice.')
                continue
            break
        else:
            key = ""
            answer = ""

            doprint = True
            # Check input length
            while len(choice) < 5:
                if doprint:
                    print("Error: Input not long enough.")
                    doprint = False
                choice += raw_input(choice)

            # Check input syntax
            if choice[0] != '(' or not choice[1].isalpha() or choice[2] != ')' or choice[3] != ' ':
                print("Error: Input not of form: (<a-z>) Question?\n.")
                continue
            else:
                # Split the key and the answer
                debug('Spliting key and answer')
                key = choice[0:3].lower()
                answer = choice[3:]

            # Check if key exists or want to replace
            if key in choices:
                replace = raw_input('[Y/n] Replace ' + key + '? ').lower()
                if replace == 'n':
                    print('.')
                    continue

            # Build any more of the answer and place in dictionary
            end = raw_input('')
            while end != '.':
                answer += ' ' + end
                end = raw_input('')
            choices[key] = answer

    # Convert choices to a string
    result = "\n.\n"
    for key in choices:
        result += key + choices[key] + '\n.\n'
    while True:
        answer = raw_input('').lower()
        key = '(' + answer + ')'
        if key in choices:
            result += '.\n' + answer
            break
        else:
            verbose("Answer " + key + " is not a choice")
    return result

def waitForResponse(clientSocket):
    while True:
        response = getResponse(clientSocket)
        next = True
        if response == 'EXIT':
            clientSocket.close()
            os._exit(0)
        else:
            print(response)


## Start of the client program ##
# Connect to the server
try:
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
except Exception as e:
    print("Error: " + str(e))
    print("Error: qclient takes exactly 2 arguments\nEx:    contestmeister <hostname> <portnumber>")
    sys.exit(-1)

try:
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    print('Connected to Server')
except Exception as e:
    print("Error: " + str(e))
    sys.exit(-1)

# try:
    # lines = []
    # with open(sys.argv[2]) as f:
        # lines = f.read().split('\n')
        # lines = lines[:-1]
    # for line in lines:
        # print(line)

        # sleep(.05)



    # for i in range(len(lines)):
        # line = lines[i]
        # if line[0] == 'p':
            # for j in range(i+1, len(lines)-1):
                # if lines[j] == '.' and lines[j+1] == '.':
                    # line += '\n' + lines[j+2]
                    # i = j+2
                    # break
                # elif lines[j] == '.':
                    # pass
                # else:
                    # line += '\n' + lines[j]
        # print('Line: ' + line)
        # sendRequest(clientSocket, line)
        # print('Requested')
        # time.sleep(.05)
        # socket.recv(2048).decode()
        # print('Received')
# except Exception as e:
    # print('Error: ' + str(e))

# def processInput(uin=True, 

# Interface with server
global response
response = ''
next = False
thread.start_new_thread(waitForResponse, (clientSocket,))
while True:
    request = raw_input('> ')
    req = request[0]

    if req == 'p':
        request += '\n' + raw_input('') # add tags
        request += '\n' + raw_input('') # add question
        end = raw_input('') # check if period given
        while end != '.':
            request += '\n' + end # add more to the question
            end = raw_input('') # check period again
        choices = getValidChoices()
        request += choices # add valid choices and answer

    # request = buildRequest(request)
    sendRequest(clientSocket, request)
    time.sleep(.05)
