#!/usr/bin/env python2
from socket import *
from Queue import Queue
import StringIO
import numpy as np
import thread, threading
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

def getValidChoices(input):
    choices = {}
    while True:
        choice = input('')
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
                choice += input(choice)

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
                replace = input('[Y/n] Replace ' + key + '? ').lower()
                if replace == 'n':
                    print('.')
                    continue

            # Build any more of the answer and place in dictionary
            end = input('')
            while end != '.':
                answer += ' ' + end
                end = input('')
            choices[key] = answer

    # Convert choices to a string
    result = "\n.\n"
    for key in choices:
        result += key + choices[key] + '\n.\n'
    while True:
        answer = input('').lower()
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
            print(response.strip())


## Start of the client program ##
# Connect to the server
try:
    # serverName = gethostname()
    serverName = 'storm.cise.ufl.edu'
    serverPort = int(sys.argv[1])
except Exception as e:
    print("Error: " + str(e))
    print("Error: contestmeister takes 1 arguments and 1 optional\nEx:    contestmeister <portnumber> [init.txt]")
    sys.exit(-1)

try:
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    print('Connected to Server')
except Exception as e:
    clientSocket.connect((gethostname(),serverPort))
    print('Connected to Server')
    # print("Error: " + str(e))
    # sys.exit(-1)

# Interface with server
global response, lineq
lineq = Queue()
response = ''
next = False
# thread.start_new_thread(waitForResponse, (clientSocket,))
def initialize():
    try:
        def lineqget(na=''):
            line = lineq.get()
            lineq.task_done()
            debug(line)
            return line

        initfile = sys.argv[2]
        with (open(initfile)) as f:
            for line in f:
                lineq.put(line.strip())

            while not lineq.empty():
                request = lineqget()
                req = request[0]

                if req == 'p':
                    request += '\n' + lineqget() # add tags
                    request += '\n' + lineqget() # add question
                    end = lineqget() # check if period given
                    while end != '.':
                        request += '\n' + end # add more to the question
                        end = lineqget() # check period again
                    choices = getValidChoices(lineqget)
                    request += choices # add valid choices and answer

                # request = buildRequest(request)
                sendRequest(clientSocket, request)
                time.sleep(.1)
            line1.join()

    except:
        sys.exit(0)


t = threading.Thread(target=waitForResponse, args=(clientSocket,))
t.daemon = True
t.start()
t = threading.Thread(target=initialize)
t.daemon = True
t.start()
t.join()

while True:
    request = raw_input('> ')
    if request == '':
        continue
    req = request[0]

    if req == 'p':
        request += '\n' + raw_input('') # add tags
        request += '\n' + raw_input('') # add question
        end = raw_input('') # check if period given
        while end != '.':
            request += '\n' + end # add more to the question
            end = raw_input('') # check period again
        choices = getValidChoices(raw_input)
        request += choices # add valid choices and answer

    # request = buildRequest(request)
    sendRequest(clientSocket, request)
    time.sleep(.05)
