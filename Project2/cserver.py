from socket import *
import sys, re, json, io
import sqlite3 as sql
import random as rand
import numpy as np
import os.path

def debug(info):
    if d:
        print(info)

def dbGetLowestNumber():
    db.execute('SELECT Number FROM Questions;')
    conn.commit()
    nums = db.fetchone()
    if nums == None:
        return 1
    debug(nums)
    debug('Numbers')
    least = 1
    for i in range(0,len(nums)):
        debug(str(nums[i]) + " " + str(i+1))
        if nums[i] != i+1:
            debug('returning ' + str(i+1))
            return i+1
    debug('returning ' + str(len(nums)+1))
    return len(nums)+1

def dbGetQuestionExists(n):
    num = (str(n),)
    db.execute("SELECT count(*) FROM Questions WHERE Number=?", num)
    conn.commit()
    result = db.fetchone()
    return result[0]

## Server Functions ##
def sendResponse(socket, message):
    socket.send(message.encode())

def getRequest(socket):
    req = socket.recv(2048).decode() 
    result = re.split("\\\\",req)
    return result

def buildResponse(arr):
    response = ''
    for e in arr:
        response = response + e + '\n'
    return response

def addQuestion(newQuestion):
    lnum = dbGetLowestNumber()
    tags = re.split(',|, ', newQuestion[1])
    debug(tags)
    while len(tags) < 5:
        tags.append('')
    tags = tags[0:5]
    debug(tags)
    question = newQuestion[2]
    answers = newQuestion[3:7]
    correct = newQuestion[7]

    qinsert = [num]
    tinsert = [num]
    ainsert = [num]
    qinsert.append(question)
    qinsert.append(correct.lower())
    tinsert = np.concatenate([tinsert,tags])
    ainsert = np.concatenate([ainsert,answers])

    debug('Inserts:')
    debug(qinsert)
    debug(tinsert)
    debug(ainsert)
    db.execute("INSERT INTO Questions VALUES (?,?,?);", qinsert)
    db.execute("INSERT INTO Tags VALUES (?,?,?,?,?,?);", tinsert)
    db.execute("INSERT INTO Answers VALUES (?,?,?,?,?);", ainsert)
    conn.commit()
    
    return str(num)

def deleteQuestion(num):
    result = 'Error: Question ' + num + ' not found.'
    exists = dbGetQuestionExists(num)
    if exists:
        val = (num,)
        db.execute("DELETE FROM Questions WHERE Number=?;", val)
        db.execute("DELETE FROM Tags WHERE Number=?;", val)
        db.execute("DELETE FROM Answers WHERE Number=?;", val)
        conn.commit()
        result = 'Deleted question ' + str(num)

    return result

def getQuestion(num):
    question = 'Error: Question ' + str(num) + ' not found.'
    exists = dbGetQuestionExists(num)
    if exists:
        db.execute("SELECT * FROM Questions WHERE Number=?", (num,))
        conn.commit()
        questions = db.fetchone()

        db.execute("SELECT * FROM Tags WHERE Number=?", (num,))
        conn.commit()
        tags = db.fetchone()

        db.execute("SELECT * FROM Answers WHERE Number=?", (num,))
        conn.commit()
        answers = db.fetchone()

        question = str(num) + '\n'
        for tag in tags[1:]:
            if tag != '':
                question = question + str(tag) + ', '
        question = question[:-2] + '\n' + questions[1] + '\n.\n'
        question = question + '(a) ' + answers[1] + '\n.\n'
        question = question + '(b) ' + answers[2] + '\n.\n'
        question = question + '(c) ' + answers[3] + '\n.\n'
        question = question + '(d) ' + answers[4] + '\n.\n.'

    return question

def getRandomQuestion():
    question = 'Error: No questions exist'
    db.execute("SELECT count(*) FROM Questions;")
    conn.commit()
    total = db.fetchone()
    if total[0] > 0:
        index = rand.randint(0,total[0]-1)
        db.execute("SELECT Number FROM Questions;")
        conn.commit()
        nums = db.fetchall()
        debug(nums)
        debug('value = ' + str(nums[index][0]))
        question = getQuestion(nums[index][0])
    return question

def checkAnswer(num, ans):
    result = 'Error: Question ' + num + ' not found.'
    exists = dbGetQuestionExists(num)
    if exists:
        val = (num,)
        db.execute("SELECT Correct FROM Questions WHERE Number=?;", val)
        conn.commit()
        correct = db.fetchone()
        result = 'Correct' if ans.lower() == correct[0] else 'Incorrect'
    return result

def helpPage():
    page = '\n\n--------------------------------------------------------------------------------------------------\n\nThis is a quiz program that allows you to insert new question, delete old ones, and test yourself on them.\nUsage is as follows:\n\n> p :: Use \'p\' to insert a new question.\n\t:: Input question tags as comma separated list (up to 5)\n\t:: Input question\n\t:: Input answer choices when prompted\n\t:: Input letter of correct answer choice\n\t>> Server will output the assigned question id\n\n> d <n> :: Use \'d\' to delete a question with id == n\n\t>> Server will output either success or failure message\n\n> g <n> :: Use \'g\' to see the question with id == n\n\t>> Server will output id, tags, question, and choices if question exists\n\n> r :: Use \'r\' to get a random question\n\t>> Server will output id, tags, question, and choices of a random question if any question exist\n\n> c <n> <x> :: Use \'c\' to check question n with your answer x (a, b, c, or d)\n\t>> Server outputs either Correct or Incorrect if question exists\n> k :: Use \'k\' to terminate the client and the server\n\n> q :: Use \'q\' to terminate just the client but leaving the server running\n\n> h :: Use \'h\' to display this page again\n\n--------------------------------------------------------------------------------------------------\n\n'
    return page

def startContest():
    def connectContestant():
        return
    return




d = True if '-d' in sys.argv else False
# conn = sql.connect('cbank')
# db = conn.cursor()

# db.execute("SELECT count(*) FROM sqlite_master;")
# conn.commit()
# checkTables = db.fetchone() 
# if checkTables[0] == 0:
    # debug('Creating Tables')
    # db.execute("CREATE TABLE Questions(Number INTEGER PRIMARY KEY ASC, Contest INTEGER, Question TEXT, Correct TEXT);")
    # db.execute("CREATE TABLE Tags(Number INTEGER PRIMARY KEY ASC, Contest INTEGER, tag1 BLOB, tag2 BLOB, tag3 BLOB, tag4 BLOB, tag5 BLOB);")
    # db.execute("CREATE TABLE Answers(Number INTEGER PRIMARY KEY ASC, Contest INTEGER, A TEXT, B TEXT, C TEXT, D TEXT);")
    # conn.commit()
    # debug('Tables Created')


## Start of the Program ##
# Create database if not exists
db = json.dumps({"contests": {}})
if os.path.exists("cbank"):
    with open("cbank","r") as file:
        db = json.dumps(file.readlines())

print (db)

## Network Setup ##
# Setup hostname and port number for meister
hostname = 'storm.cise.ufl.edu' if '-h' not in sys.argv else sys.argv[sys.argv.index('-h')+1]
serverPort = 12000 if '-p' not in sys.argv else int(sys.argv[sys.argv.index('-p')+1])
serverSocket = socket(AF_INET,SOCK_STREAM)
while True:
    debug("Trying port " + str(serverPort) + "...")
    try:
        serverSocket.bind((hostname,serverPort))
        print("Server bound to " + hostname + " at port " + str(serverPort))
        break
    except:
        serverPort += 1
        continue
serverSocket.listen(1)
print('The server is ready to receive')
print('Waiting on client...')
exit(0)


## Accept Connections and Handle Requests ##
# Wait for a meister, and then wait again once that connection drops
while True:
    connectionSocket, addr = serverSocket.accept()
    print('Connected to Client')

    # Handle Requests from Connected Meister
    while True:
        # Get a request
        request = getRequest(connectionSocket)
        debug(request)
        req = request[0]

        # Take arguments and service the request
        if req in ['k','kill']:
            sendResponse(connectionSocket,'EXIT')
            connectionSocket.close()
            conn.close()
            print('Client disconnected')
            print('Terminating server...')
            sys.exit(0)
        elif req in ['q','quit']:
            sendResponse(connectionSocket,'EXIT')
            connectionSocket.close()
            print('Client disconnected')
            print('Waiting on client...')
            break
        elif req in ['p','put']:
            try:
                response = addQuestion(request)
                sendResponse(connectionSocket, str(response))
            except Exception as e:
                sendResponse(connectionSocket, 'Error: ' + str(e))
                continue
        elif req in ['d','delete']:
            try:
                response = deleteQuestion(request[1])
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error: ' + str(e))
                continue
        elif req in ['g','get']:
            try:
                response = getQuestion(request[1])
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error: ' + str(e))
                continue
        elif req in ['c','check']:
            try:
                response = checkAnswer(request[1], request[2])
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error: ' + str(e))
                continue
        elif req in ['r','random']:
            try:
                response = getRandomQuestion()
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error: ' + str(e))
                continue
        elif req in ['h','help']:
            try:
                response = helpPage();
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error: ' + str(e))
                continue
        else:
            sendResponse(connectionSocket, 'Error: Invalid Request')
            continue
