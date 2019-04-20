#!/usr/bin/env python3
from Queue import Queue
from socket import *
import sys, re, json, io, os, time
import threading
import sqlite3 as sql
import random as rand
import numpy as np
import ctypes as ct
import operator

def debug(info):
    if '-d' in sys.argv:
        print(str(info))

def printDictionary(dict):
    print(json.dumps(dict, indent=4))

def sortDictionary(dict):
    d_sorted = sorted(dict.items(), key=operator.itemgetter(0))
    return d_sorted

def loadJSON(dict):
    return json.loads(dict)

def updateJSON():
    with open('qbank','w+') as f:
        json.dump(qbank, f)

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
    page = '--------------------------------------------------------------------------------------------------\n\nThis program is a multi-threaded sockets program which allows users to create, update, start and review contests and to take part in those contests as well.\n\nUsage is as follows:\n> p <qn> :: Use \'p\' to insert a new question.\n\t:: Input question tags as comma separated list\n\t:: Input question followed by a period: \'question <CR> . <CR>\'\n\t:: Input answer choices as follows: \'(<letter>) choice <CR> . <CR>\'\n\t:: When finished inputing choices, enter a second period before the answer\n\t:: Input letter of correct answer choice\n\t>> Server will Error if the question already exists for the current meister\n\n> d <qn> :: Use \'d\' to delete a question with id == qn\n\t>> Server will delete the indicated question\n\n> g <qn> :: Use \'g\' to see the question with id == qn\n\t>> Server will output the question as it was input\n\n> s <cn> :: Use \'s\' to setup a new contest\n\n> b <cn> :: Use \'b\' to allocate a socket for a new instance of a contest which runs until finished\n\t:: Will pass the port number back to the meister\n\t:: A single contest can have multiple instances of itself started.\n\n> r <qn> :: Use \'r\' to review statistics on a set contest\n\t>> Server will output overall statistics of the contest\n\t>> If the contest has been run, statistics on each question are provided\n\n> a <cn> <qn> :: Use \'a\' to append a question to a set contest\n\t>> Server outputs an error if either the contest or the question don\'t exist\n\n> k :: Use \'k\' to terminate the server and all clients\n\n> q :: Use \'q\' to terminate just the current meister\n\n> h :: Use \'h\' to display this page again\n\n--------------------------------------------------------------------------------------------------\n\n'
    return page

def killAllConnections():
    for tup in allcons:
        try:
            sendResponse(tup[0], 'EXIT')
            connection.close()
            debug('Client {} disconnected'.format(tup[1][1]))
        except:
            pass
    print('Terminating server...')
    os._exit(0)

# def waitForThreads(conns, contest, threads):
    # dead = 0
    # end = time.time() + 60
    # while time.time() < end and dead != len(threads):
        # dead = 0
        # for t in threads:
            # if not t.isAlive():
                # dead += 1
    # for conn in conns:
        # if conn not in contest['connections']:
            # sendResponse(conn, 'EXIT')
            # conn.close()
    # return []

def sendQuestion(contestant, response, question):
    contestant['correct'].append(0)
    conn = contestant['connection']
    sendResponse(conn, response)
    answer = getRequest(conn)
    answer = answer[0].lower()
    if answer == question['answer']:
        contestant['correct'][-1] = 1
    return

def getContestant(conn, addr, contest):
    while True:
        request = getRequest(conn)
        req = request[0]
        if req in contest['contestants'].keys():
            sendResponse(conn, 'Error: Nickname {} is already in use.'.format(req))
        else:
            allcons.append(conn)
            contest['contestants'][req] = {
                'connection': conn,
                'correct': []
            }
            contest['connections'].append(conn)
            sendResponse(conn, 'Hello {}, get ready for contest!'.format(req))
            return

def acceptClients(contest):
    socket = contest['socket']
    while True:
        c,addr = socket.accept()
        allcons.append((c,addr))
        t = threading.Thread(target = getContestant, args = (c, addr, contest))
        t.daemon = True
        t.start()


def runContest(contestData, contest):

    def qthreader(qq):
        contestant, response, question = qq.get()
        sendQuestion(contestant,response, question)
        qq.task_done()

    def sendStats(top, ratio, data):
        conn = data['connection']
        correct = data['correct']
        response = ''
        if correct[-1] == 1:
            response += 'Correct. {}% of contestants answered this question correctly.\n'.format(ratio)
        else:
            response += 'Incorrect. {}% of contestants answered this question correctly.\n'.format(ratio)
        response += 'Your score is {}/{}. The top score is currently {}/{}'.format(sum(correct),len(correct),top,len(correct))
        sendResponse(conn, response)

    def sthreader():
        top, ratio, data = qq.get()
        sendStats(top,ratio, data)
        qq.task_done()

    conns = []

    # Get Contestants
    cthread = threading.Thread(target = acceptClients, args = (contest,))
    cthread.daemon = True
    cthread.start()
    cthread.join(60.0)
    contestants = contest['contestants']
    if len(contestants.keys()) == 0:
        print('No Contestants')
        return

    # Serve the questions
    qq = Queue()
    threads = []
    for num in contest['questions']:
        # names = contestants.keys()
        question = qbank[num]
        response = question['question']
        choices = question['choices']
        for key in sorted(choices.keys()):
            response += '\n\t({}) {}'.format(key, choices[key])
        for name, data in contestants.items():
            qq.put((data, response, question))
            t = threading.Thread(target = qthreader, args = (qq,))
            t.daemon = True
            t.start()
            threads.append(t) 
        for t in threads:
            t.join(60.0)

        # Send stats
        totals = []
        for data in contestants.values():
            totals.append(data['correct'])
        num_correct = np.sum(totals,axis=0)
        each_correct = np.sum(totals,axis=1)
        top = np.max(each_correct)
        ratio = int(num_correct[-1]*100/len(contestants.keys()))

        for data in contestants.values():
            qq.put((top, ratio, data))
            t = threading.Thread(target = sthreader)
            t.daemon = True
            t.start()

    time.sleep(0.1)
    for name, data in contestants.items():
        sendResponse(data['connection'], 'FINISHED')
        data['connection'].close()
    contestData['contestants'] = totals if contestData['status'] != 'run' else np.concatenate((contestData['contestants'],totals),0)
    contestData['recents'] = totals
    contestData['status'] = 'run'

def setupContestSocket():
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(('', 0))
    contestPort = s.getsockname()[1]      
    s.listen(5)
    return s, contestPort

def hostMeister(connectionSocket, addr):
    debug('Connected to Meister {}'.format(addr[1]))
    contest_threads = []
    contests = {}
    sessions = {}
    # db[str(addr)] = {
        # 'socket': connectionSocket,
        # 'contests': contests,
        # 'sessions': sessions,
        # 'questions': questions 
    # }

    # Handle Requests from Connected Meister
    while True:
        # Get a request
        request = getRequest(connectionSocket)
        req = request[0].split()
        debug(str(req))

        # Take arguments and service the request
        if req[0] in ['p','put']:
            try:
                num = req[1]
                response = ''
                if num in qbank.keys():
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
                    qbank[num] = question
                updateJSON()
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: {}'.format(e))
                continue
        elif req[0] in ['g','get']:
            # Get a question
            try:
                num = req[1]
                response = ''
                if num not in qbank.keys():
                    response = 'Error: question {} not found.'.format(num)
                else:
                    qdata = qbank[num]
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
                num = req[1]
                qbank.pop(num, None)
                response = 'Deleted question {}'.format(num)
                updateJSON()
                sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: {}'.format(e))
                continue
        elif req[0] in ['s','set']:
            # Set a new contest
            try:
                num = req[1]
                response = ''
                if num in contests.keys():
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
                    contest = contests[num]
                    contestants = contest['contestants']
                    qnums = contest['questions']
                    numcontestants = len(contestants)
                    numquestions = len(qnums)
                    status = contest['status']
                    response = '{}\t{} questions, {}'.format(num,numquestions,status)
                    if status == 'run':
                        contestantcorrect = np.sum(contestants,axis=0)
                        totalcorrect = np.sum(contestants,axis=1)
                        avgcorrect = np.average(totalcorrect)
                        response += ', average correct: {}; maximum correct: {}'.format(round(avgcorrect,2),numquestions)
                    response += '\n'
                    sendResponse(connectionSocket, response)
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: {}'.format(e))
                continue
        elif req[0] in ['a','append']:
            # Append question to contest
            try:
                response = ''
                cnum = req[1]
                qnum = req[2]
                if cnum not in contests.keys():
                    response = 'Error: Contest {} does not exist.'.format(cnum)
                elif qnum not in qbank.keys():
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
                num = req[1]
                contestSocket, cPort = setupContestSocket() # Get the meister socket
                contestData = contests[num]
                contest = sessions[cPort] = {
                    'contest-number': num,
                    'socket': contestSocket,
                    'questions': contests[num]['questions'],
                    'connections': [],
                    'registered': [],
                    'contestants': {}, # each entry is nickname: { personal stats }
                }
                t = threading.Thread(target = runContest, args = (contestData, contest))
                t.daemon = True
                t.start()
                print('Contest {} started on port {}'.format(num,cPort))
                sendResponse(connectionSocket, str(cPort))
            except Exception as e:
                sendResponse(connectionSocket, 'Error cserver get: {}'.format(e))
                continue
        elif req[0] in ['r','review']:
            # Review a contest
            try:
                num = req[1]
                response = ''
                if num not in contests.keys():
                    response = 'Error: Contest {} does not exist.'.format(num)
                else:
                    contest = contests[num]
                    contestants = contest['contestants']
                    recents = contest['recents']
                    qnums = sorted(contest['questions'])
                    numcontestants = len(contestants)
                    numrecents = len(recents)
                    numquestions = len(qnums)
                    status = contest['status']
                    response = '{}\t{} questions, {}'.format(num,numquestions,status)
                    if status == 'run':
                        contestantcorrect = np.sum(contestants,axis=0)
                        recentscorrect = np.sum(recents,axis=0)
                        totalcorrect = np.sum(contestants,axis=1)
                        avgcorrect = np.average(totalcorrect)
                        response += ', average correct: {}; maximum correct: {}'.format(round(avgcorrect,2),numquestions)
                        for i in range(0,numquestions):
                            num = qnums[i]
                            percent = int(recentscorrect[i]*100/numrecents)
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
            updateJSON()
            killAllConnections()
        elif req[0] in ['q','quit']:
            updateJSON()
            sendResponse(connectionSocket,'EXIT')
            connectionSocket.close()
            debug('Meister {} disconnected'.format(addr[1]))
            break
        else:
            sendResponse(connectionSocket, 'Error: Invalid Request')
            continue
  
def setupMeisterSocket():
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind((gethostname(), 0))
    global port
    port = s.getsockname()[1]      
    print(port)
    s.listen(5)
    return s

def mthreader():
    c, addr = mq.get()
    hostMeister(c,addr)
    mq.task_done()

## Start of the Program ##
global mq, allcons, qbank
allcons = []
mq = Queue()

try:
    with open('qbank', 'r') as f:
        data = f.read()
        qbank = json.loads(data)
except Exception as e:
    print(e)
    qbank = {}
    updateJSON()

## Network Setup ##
# Setup hostname and port number for meister
meisterSocket = setupMeisterSocket() # Get the meister socket
while True:
    c,addr = meisterSocket.accept()
    allcons.append((c,addr))
    mq.put((c,addr))
    t = threading.Thread(target = mthreader)
    t.daemon = True
    t.start()
