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
        print(str(info))

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
        debug(nums[i] + " " + i+1)
        if nums[i] != i+1:
            debug('returning {}'.format(i+1))
            return i+1
    debug('returning {}'.format(len(nums)+1))
    return len(nums)+1

def dbGetQuestionExists(n):
    num = (n,)
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
    debug(result[0])
    return result

def buildResponse(arr):
    response = ''
    for e in arr:
        response += '{}\n'.format(e)
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
    for c, addr in allcons:
        try:
            sendResponse(c, 'EXIT')
            connection.close()
            print('Client {} disconnected'.format(addr[1]))
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
            response += '\n\t{}'.format(choice)
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
        for contestant in contestants:
            conn = contestant['connection']
            correct = contestant['correct']
            if correct[-1] == 1:
                response += 'Correct. {}% of contestants answered this question correctly.\n'.format(ratio)
            else:
                response += 'Incorrect. {}% of contestants answered this question correctly.\n'.format(ratio)
            response += 'Your score is {}/{}. The top score is currently {}/{}'.format(sum(correct),len(correct),top,len(correct))
            sendResponse(conn, response)

    for contestant in contestants:
        sendResponse(contestant['connection'], 'FINISHED')
        contestant['connection'].close()
    contestData['contestants'] = np.concatenate((contestData['contestants'],np.transpose(totals)),1)
    contestData['status'] = 'run'

def hostMeister(connectionSocket, addr):
    debug('Connected to Meister {}'.format(addr[1]))
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
        debug(str(request))

        # Take arguments and service the request
        if req[0] in ['p','put']:
            try:
                num = int(req[1])
                response = ''
                if int(num) in questions.keys():
                    response = 'Error: question number {} already used.'.format(num)
                else:
                    response = 'Question {} added.'.format(num)
                    question = {
                        'tags': request[1].strip(),
                        'question': request[2].strip(),
                        'choices': {},
                        'answer': ''
                    }
                    for i in range(3,100):
                        if request[i] == '.':
                            i += 1
                            if request[i] == '.':
                                question['answer'] = request[i+1].strip()
                                break
                        question['choices'][request[i][1]] = request[i][3:].strip()
                    questions[num] = question
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: {}'.format(e))
                continue
        elif req[0] in ['g','get']:
            # Get a question
            try:
                num = int(req[1])
                response = ''
                if num not in questions.keys():
                    response = 'Error: question {} not found.'.format(num)
                else:
                    qdata = questions[num]
                    response = '{}\n{}\n.\n'.format(qdata['tags'], qdata['question'])
                    for key, val in qdata['choices'].items():
                        response += '({}) {}\n.\n'.format(key,val)
                    response += '.\n{}'.format(qdata['answer'])
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: {}'.format(e))
                continue
        elif req[0] in ['d','delete']:
            # Delete a question
            try:
                num = int(req[1])
                questions.pop(int(num), None)
                response = 'Deleted question {}'.format(num)
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: {}'.format(e))
                continue
        elif req[0] in ['s','set']:
            # Set a new contest
            try:
                num = int(req[1])
                response = ''
                if int(num) in contests.keys():
                    response = 'Error: Contest {} already exists.'.format(num)
                else:
                    response = 'Contest {} is set.'.format(num)
                    contests[num] = {
                        'questions': [], # question numbers for this contest
                        'contestants': [], # score data for every contestant over all contests
                        'status': 'not run'
                    }
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: {}'.format(e))
                continue
        elif req[0] in ['l','list']:
            # List contests by number
            try:
                response = 'No contests have been set.'
                for (num, contest) in contests.items():
                    contestants = contest['contestants']
                    numcontestants = len(contestants)
                    status = contest['status']
                    total = len(contest['questions'])
                    response = '{}\t{} questions, {}'.format(num, total, status)
                    if status == 'run':
                        contestantcorrect = contestants.sum(axis=0)
                        # totalcorrect = contestants.sum(axis=1)
                        avgcorrect = np.average(contestantcorrect)
                        response += ', average correct: {}; maximum correct: {}'.format(avgcorrect,total)
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: {}'.format(e))
                continue
        elif req[0] in ['a','append']:
            # Append question to contest
            try:
                response = ''
                cnum = int(req[1])
                qnum = int(req[2])
                if cnum not in contests.keys():
                    response = 'Error: Contest {} does not exist.'.format(cnum)
                elif qnum not in questions.keys():
                    response = 'Error: Question {} does not exist.'.format(qnum)
                else:
                    response = 'Added question {} to contest {}'.format(qnum,cnum)
                    contests[cnum]['questions'].append(qnum)
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: {}'.format(e))
                continue
        elif req[0] in ['b','begin']:
            # Begin a contest
            try:
                num = int(req[1])
                contestSocket, cPort = setupContestSocket() # Get the meister socket
                contestData = contests[num]
                contest = sessions[cPort] = {
                    'contest-number': num,
                    'socket': contestSocket,
                    'questions': contests[int(num)]['questions'],
                    'connections': [],
                    'registered': [],
                    'contestants': {}, # each entry is nickname: { personal stats }
                }
                thread.start_new_thread(runContest, (contestData, contest, questions))
                print('Contest {} started on port {}'.format(num,cPort))
                sendResponse(connectionSocket, str(cPort))
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: {}'.format(e))
                continue
        elif req[0] in ['r','review']:
            # Review a contest
            try:
                num = int(req[1])
                response = ''
                if num not in contests.keys():
                    response = 'Error: Contest {} does not exist.'.format(num)
                else:
                    contest = contests[num]
                    contestants = contest['contestants']
                    questions = contest['questions']
                    numcontestants = len(contestants)
                    total = len(questions)
                    status = contest['status']
                    response = '{}\t{} questions, {}'.format(num,total,status)
                    if status == 'run':
                        contestantcorrect = contestants.sum(axis=0)
                        totalcorrect = contestants.sum(axis=1)
                        avgcorrect = np.average(contestantcorrect)
                        response += ', average correct: {}; maximum correct: {}'.format(avgcorrect,total)
                        for i in range(0,total-1):
                            num = questions[i]
                            percent = int(totalcorrect[i]*100/numcontestants)
                            response += '\n\t{}\t{}% correct'.format(num,percent)
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: {}'.format(e))
                continue
        elif req[0] in ['h','help']:
            try:
                response = helpPage();
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: {}'.format(e))
                continue
        elif req[0] in ['k','kill']:
            killAllConnections()
        elif req[0] in ['q','quit']:
            sendResponse(connectionSocket,'EXIT')
            connectionSocket.close()
            debug('Meister {} disconnected'.format(addr[1]))
            break
        else:
            sendResponse(connectionSocket, 'Error: Invalid Request')
            continue
  
## Start of the Program ##
global db, allcons
db = {}
allcons = []

## Network Setup ##
# Setup hostname and port number for meister
meisterSocket = setupMeisterSocket() # Get the meister socket
while True:
    c,addr = meisterSocket.accept()
    allcons.append((c,addr))
    thread.start_new_thread(hostMeister, (c,addr))
