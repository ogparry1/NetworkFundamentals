#!/usr/bin/env python2
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
            print('Hello' + nickname + ', get ready for contest!')
            return nickname
        else:
            print('Error: Nickname '+ nickname + ' is already in use.')

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
total = contest['total'] # is incremented in getContest
count = 0
ccount = 0
for q in questions: # Questions is an array of dictionaries and an array or choices
    count += 1

    # Ask the question
    print('Question ' + count + ':')
    print(q['question'])
    for choice in q['choices']:
        print(choice)
    answer = raw_input('Enter your choice: ').lower()

    # Check the answer
    result = 'Incorrect. ' 
    if answer == correct:
        result = 'Correct. '
        ccount += 1
        q['answered-correct'] += 1

    tratio = q['answered-correct']/q['total']*100
    print(result + int(tratio) + '% of contestants answered this question correctly.')
    print('Your score is ' + ccount + '/' + count + '. The top score is currently ' + contest['top-score'])

