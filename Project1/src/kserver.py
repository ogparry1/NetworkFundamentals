from socket import *
import sys, re, json, io
import sqlite3 as sql

terminate = False
d = True if '-d' in sys.argv else False
conn = sql.connect('project1.db')
db = conn.cursor()
checkTables = db.execute("SELECT count(*) FROM sqlite_master;")
print(checkTables)
if checkTables == '0':
    print('Creating Tables')
    db.execute("CREATE TABLE Questions(Number INTEGER PRIMARY KEY ASC, Question TEXT, Correct TEXT);")
    db.execute("CREATE TABLE Tags(Number INTEGER PRIMARY KEY ASC, tag1 BLOB, tag2 BLOB, tag3 BLOB, tag4 BLOB, tag5 BLOB);")
    db.execute("CREATE TABLE Answers(Number INTEGER PRIMARY KEY ASC, A TEXT, B TEXT, C TEXT, D TEXT);")
    conn.commit()

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

def addQuestion(newQuestion):
    qNum = -1
    tags = re.split(',|, ', request[1])
    question = request[2]
    answers = request[3:6]
    correct = request[7]
    
    return str(qNum)

def deleteQuestion(num):
    question = 'Error: Question ' + num + ' not found.'
    return question

def getQuestion(num):
    question = 'Error: Question ' + num + ' not found.'
    return question

def getRandomQuestion():
    question = 'Error: No questions exist'
    return question

def checkAnswer(num, ans):
    result = 'Error: No questions exist'
    return result

def helpPage():
    hPage = 'Help Page'
    return hPage

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
        if req in ['k','kill']:
            sendResponse(connectionSocket,'EXIT')
            connectionSocket.close()
            terminate = True
            conn.close()
            break
        elif req in ['q','quit']:
            sendResponse(connectionSocket,'EXIT')
            connectionSocket.close()
            break
        elif req in ['p','put']:
            response = buildResponse(request)
            sendResponse(connectionSocket, response)
        elif req in ['d','delete']:
            response = deleteQuestion(request[1])
            sendResponse(connectionSocket, response)
        elif req in ['g','get']:
            response = getQuestion(request[1])
            sendResponse(connectionSocket, response)
        elif req in ['c','check']:
            response = checkAnswer(request[1], request[2])
            sendResponse(connectionSocket, response)
        elif req in ['r','random']:
            response = getRandomQuestion()
            sendResponse(connectionSocket, response)
        elif req in ['h','help']:
            response = helpPage()
            sendResponse(connectionSocket, response)
        else:
            sendResponse(connectionSocket, 'Error: Invalid Request')
            continue
