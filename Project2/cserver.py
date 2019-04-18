#!/usr/bin/env python2
from socket import *
import sys, re, json, io
import sqlite3 as sql
import random as rand
import numpy as np
import ctypes as ct
import os.path
import os
import thread
import time

def debug(info):
    if '-d' in sys.argv:
        print(info)

def loadJSON(filename):
    if os.path.exists(filename):
        with open(filename) as file:
            return json.load(file)

def saveJSON(filename, data):
    if os.path.exists(filename):
        with open(filename) as file:
            file.write(json.dumps(data))

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
    result = req.split("\n")
    print result[0]
    return result

def buildResponse(arr):
    response = ''
    for e in arr:
        response = response + e + '{}{}\n'
    return response

def helpPage():
    page = '\n\n--------------------------------------------------------------------------------------------------\n\nThis is a quiz program that allows you to insert new question, delete old ones, and test yourself on them.\nUsage is as follows:\n\n> p :: Use \'p\' to insert a new question.\n\t:: Input question tags as comma separated list (up to 5)\n\t:: Input question\n\t:: Input answer choices when prompted\n\t:: Input letter of correct answer choice\n\t>> Server will output the assigned question id\n\n> d <n> :: Use \'d\' to delete a question with id == n\n\t>> Server will output either success or failure message\n\n> g <n> :: Use \'g\' to see the question with id == n\n\t>> Server will output id, tags, question, and choices if question exists\n\n> r :: Use \'r\' to get a random question\n\t>> Server will output id, tags, question, and choices of a random question if any question exist\n\n> c <n> <x> :: Use \'c\' to check question n with your answer x (a, b, c, or d)\n\t>> Server outputs either Correct or Incorrect if question exists\n> k :: Use \'k\' to terminate the client and the server\n\n> q :: Use \'q\' to terminate just the client but leaving the server running\n\n> h :: Use \'h\' to display this page again\n\n--------------------------------------------------------------------------------------------------\n\n'
    return page

def setupMeisterSocket():
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind((gethostname(), 0))
    global port
    port  = s.getsockname()[1]      
    print(port)
    s.listen(5)
    return s

def setupContestSocket():
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(('', 0))
    contestPort = s.getsockname()[1]      
    s.listen(5)
    return s, contestPort

def killAllConnections():
    for connection in allcons:
        try:
            sendResponse(connection, 'EXIT')
            connection.close()
            print('Client disconnected')
        except:
            pass
    print('Terminating server...')
    os._exit(0)

def waitForThreads(conns, contest, threads):
    dead = 0
    end = time.time() + 60
    while time.time() < end and dead != len(threads):
        dead = 0
        for t in threads:
            if not t.isAlive():
                dead += 1
    for conn in conns:
        if conn not in contest['connections']:
            sendResponse(conn, 'EXIT')
            conn.close()
    return []

def getContestant(conns, num, contest):
    conn = conns[num]
    while True:
        request = getRequest(conn)
        req = request[0]
        if req in contest['contestants'].keys():
            sendResponse(conn, 'NACK')
        else:
            contest['contestants'][req] = {
                'connection': conn,
                'correct': []
            }
            contest['connections'].append(conn)
            sendResponse(conn, 'ACK')
            break

def sendQuestion(contestant, response, totals):
    conn = contestant['connection']
    sendResponse(conn, response)
    answer = getRequest(conn)
    answer = answer[0].lower()
    if answer == question['answer']:
        contestant['correct'].append(1)
    else:
        contestant['correct'].append(0)

def runContest(contestData, contest, questions):
    conns = []
    threads = []

    # Get Contestants
    end = time.time() + 60
    while time.time() < end:
        c,addr = contest['socket'].accept()
        conns.append(c)
        threads.append(thread.start_new_thread(getContestant, (conns, len(conns)-1, contest)))
    for conn in conns:
        if conn not in contest['connections']:
            sendResponse(conn, 'EXIT')
            conn.close()
    for thread in threads:
        if not thread.isAlive():
            thread.exit()

    # Serve the questions
    totals = []
    contestants = contest['contestants']
    for num in contest['questions']:
        threads = []
        names = contestants.keys()
        response = question['question']
        for choice in question['choices']:
            if choice == '.':
                continue
            response += '\n\t' + choice
        for contestant in contestants:
            threads.append(thread.start_new_thread(sendQuestion, (contestant, response, totals)))

        dead = [0] * len(threads)
        end = time.time() + 60
        while time.time() < end:
            if np.average(dead) == 1:
                break
            for t in threads:
                if t.isAlive():
                    dead[t.index()] = 1
        for d in dead:
            if d == 0:
                t[d.index()].exit()
                name = names(d.index())
                contestants['name'][correct].append(0)
        for contestant in contestants:
            totals.append(contestant['correct'])
        total = totals.sum(axis=0)
        top = np.max(totals.sum(axis=1))
        ratio = int(total[-1]*100/len(contestants.keys()))
        rstat = str(ratio) + '% of contestants answered this question correctly.\n'
        for contestant in contestants:
            conn = contestant['connection']
            correct = contestant['correct']
            if correct[-1] == 1:
                response = 'Correct. ' + rstat
            else:
                response = 'Incorrect. ' + rstat
            response += 'Your score is ' + str(sum(correct)) + '/' + str(len(correct)) + '. The top score is currently ' + str(top) + '/' + str(len(correct))
            sendResponse(conn, response)

    for contestant in contestants:
        sendResponse(contestant['connection'], 'FINISHED')
        contestant['connection'].close()
    contestData['contestants'] = np.concatenate((contestData['contestants'],np.transpose(totals)),1)
    contestData['status'] = 'run'

def hostMeister(connectionSocket, addr):
    print('Connected to Meister: ' + str(addr))
    contests = {}
    sessions = {}
    questions = {}
    db[str(addr)] = {
        'socket': connectionSocket,
        'contests': contests,
        'sessions': sessions,
        'questions': questions 
    }

    # Handle Requests from Connected Meister
    while True:
        # Get a request
        request = getRequest(connectionSocket)
        debug(request)
        req = request[0].split()
        print(str(request))

        # Take arguments and service the request
        if req[0] in ['p','put']:
            try:
                num = req[1]
                response = ''
                if int(num) in questions.keys():
                    response = 'Error: question number ' + num + ' already used.'
                else:
                    response = 'Question ' + num + ' added.' 
                    question = {
                        'tags': request[1],
                        'question': request[2],
                        'choices': [],
                        'answer': ''
                    }
                    for i in range(3,100):
                        question['choices'].append(request[i])
                        if request[i] == '.' and request[i+1] == '.':
                            question['answer'] = request[i+2]
                            break
                    questions[int(num)] = question
                sendResponse(connectionSocket, str(response))
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver put: ' + str(e))
                continue
        elif req[0] in ['g','get']:
            # Get a question
            try:
                num = req[1]
                response = ''
                if int(num) not in questions.keys():
                    response = 'Error: question ' + num + ' not found.'
                else:
                    qdata = questions[int(num)]
                    response = qdata['tags'] + '\n' + qdata['question'] + '\n'
                    for choice in qdata['choices']:
                        response += choice + '\n'
                    response += '.\n' + qdata['answer']
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: ' + str(e))
                continue
        elif req[0] in ['d','delete']:
            # Delete a question
            try:
                num = req[1]
                questions.pop(int(num), None)
                response = 'Deleted question ' + num
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error: ' + str(e))
                continue
        elif req[0] in ['s','set']:
            # Set a new contest
            try:
                num = req[1]
                response = ''
                if int(num) in contests.keys():
                    response = 'Error: Contest ' + num + ' already exists.'
                else:
                    response = 'Contest ' + num + ' is set.'
                    contests[int(num)] = {
                        'questions': [], # question numbers for this contest
                        'contestants': [], # score data for every contestant over all contests
                        'status': 'not run'
                    }
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error: ' + str(e))
                continue
        elif req[0] in ['l','list']:
            # List contests by number
            try:
                response = 'No contests have been set.'
                for (num, contest) in contests.items():
                    contestants = contest['contestants']
                    numcontestants = len(contestants)
                    status = contest['status']
                    total = str(len(contest['questions']))
                    if status != 'run':
                        response = str(num) + '\t' + total + ' questions, ' + status
                    else:
                        contestantcorrect = contestants.sum(axis=0)
                        totalcorrect = contestants.sum(axis=1)
                        avgcorrect = np.average(contestantcorrect)
                        response = str(num) + '\t' + total + ' questions, ' + status + ', average correct: ' + str(avgcorrect) + '; maximum correct: ' + total
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error: ' + str(e))
                continue
        elif req[0] in ['a','append']:
            # Append question to contest
            try:
                response = ''
                cnum = req[1]
                qnum = req[2]
                if int(cnum) not in contests.keys():
                    response = 'Error: Contest ' + cnum + ' does not exist.'
                elif int(qnum) not in questions.keys():
                    response = 'Error: Question ' + qnum + ' does not exist.'
                else:
                    response = 'Added question ' + qnum + ' to contest ' + cnum + '.'
                    contests[int(cnum)]['questions'].append(int(qnum))
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error: ' + str(e))
                continue
        elif req[0] in ['b','begin']:
            # Begin a contest
            try:
                num = req[1]
                contestSocket, cPort = setupContestSocket() # Get the meister socket
                contestData = contests[int(num)]
                contest = sessions[cPort] = {
                    'contest-number': num,
                    'socket': contestSocket,
                    'questions': contests[int(num)]['questions'],
                    'connections': [],
                    'registered': [],
                    'contestants': {}, # each entry is nickname: { personal stats }
                }
                thread.start_new_thread(runContest, (contestData, contest, questions))
                print('Contest ' + num + ' started on port ' + str(cPort))
                sendResponse(connectionSocket, str(cPort))
            except Exception as e:
                sendResponse(connectionSocket, 'Error: ' + str(e))
                continue
        elif req[0] in ['r','review']:
            # Review a contest
            try:
                num = req[1]
                response = ''
                if int(num) not in contests.keys():
                    response = 'Error: Contest ' + num + ' does not exist.'
                else:
                    contest = contests[int(num)]
                    contestants = contest['contestants']
                    questions = contest['questions']
                    numcontestants = len(contestants)
                    total = str(len(questions))
                    status = contest['status']
                    if status != 'run':
                        response = num + '\t' + total + ' questions, ' + status
                    else:
                        contestantcorrect = contestants.sum(axis=0)
                        totalcorrect = contestants.sum(axis=1)
                        avgcorrect = np.average(contestantcorrect)
                        response = num + '\t' + total + ' questions, ' + status + ', average correct: ' + str(avgcorrect) + '; maximum correct: ' + total
                        for i in range(0,total-1):
                            num = str(questions[i])
                            percent = int(totalcorrect[i]*100/numcontestants)
                            response += '\n\t' + num + '\t' + str(percent) + '% correct'
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error: ' + str(e))
                continue
        elif req[0] in ['h','help']:
            try:
                response = helpPage();
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error: ' + str(e))
                continue
        elif req[0] in ['k','kill']:
            killAllConnections()
        elif req[0] in ['q','quit']:
            sendResponse(connectionSocket,'EXIT')
            connectionSocket.close()
            print('Client disconnected')
            print('Waiting on client...')
            break
        else:
            sendResponse(connectionSocket, 'Error: Invalid Request')
            continue
  
# def makeConnection():
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # s.bind(('', port))
    # print(port)
    # s.listen(5)
    # c, addr = s.accept()
    # return c


## Start of the Program ##
global db, allcons
db = {}
allcons = []

## Network Setup ##
# Setup hostname and port number for meister
# hostname = 'storm.cise.ufl.edu' if '-h' not in sys.argv else sys.argv[sys.argv.index('-h')+1]
meisterSocket = setupMeisterSocket() # Get the meister socket
while True:
    c,addr = meisterSocket.accept()
    allcons.append(c)
    thread.start_new_thread(hostMeister, (c,addr))

# serverPort = 12000 if '-p' not in sys.argv else int(sys.argv[sys.argv.index('-p')+1])
# serverSocket = socket(AF_INET,SOCK_STREAM)
# while True:
    # debug("Trying port " + str(serverPort) + "...")
    # try:
        # serverSocket.bind((hostname,serverPort))
        # print("Server bound to " + hostname + " at port " + str(serverPort))
        # break
    # except:
        # serverPort += 1
        # continue
# serverSocket.listen(1)
# print('The server is ready to receive')
# print('Waiting on client...')


