'''
This Server control the clients
'''
import sys
from optparse import OptionParser
from flask import Flask, render_template, send_from_directory, request, jsonify
import logging
import time
# from DSSHBruteForcer import utils
import linecache
import json
import common


class Server():
    def __init__(self):
        self.info = "Simple Distributed SSH Brute Forcer"
        # self.targetIp = ""
        self.targetPort = 0
        self.targets = []
        self.usernames = []
        self.passwords = []
        self.passwordsFiles = []
        self.passwordsFileIdx = 0
        self.connections = []
        self.amountOfThreads = 0
        self.currentThreadCount = 0
        self.timeoutTime = 0
        self.outputFileName = ""
        self.singleMode = False
        self.verbose = False
        self.listenPort = 3000
        self.listenIp = '0.0.0.0'
        self.sessions = []  # client sessions
        self.passwordCounts = 0  # passwords file total line counts
        self.passwordsNumPerClient = 1000  # passwords num serve to one client
        self.currentPasswordsIdx = 0  # current passwords file index
        self.targetIpIdx = 0  # current target ip index for brute force
        self.usernameIdx = 0  # current username index for brute force
        self.passwordsFileCount = 0

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
        optionParser.add_option('-v', '--verbose', action='store_true',
                                dest='verbose', help='verbose')

        (options, args) = optionParser.parse_args()

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

        # self.passwordCounts = common.FileTotalCounts(options.passwordsFile)

        self.StartServer(options)

    # http server for serving data to clients
    # todo encrypt message between server and client
    def StartServer(self, options):
        app = Flask(__name__)

        # serve targets for clients
        @app.route('/targets')
        def targets():
            return json.dumps(self.targets[self.targetIpIdx])

        # serve usernames for clients
        @app.route('/usernames')
        def usernames():
            return json.dumps(self.usernames[self.usernameIdx])

        # serve passwords for clients
        @app.route('/passwords')
        def passwords():
            path = self.passwordsFiles[self.currentPasswordsIdx]
            startIdx = self.currentPasswordsIdx
            endIdx = startIdx + self.passwordsNumPerClient

            if endIdx > self.currentThreadCount:
                endIdx = self.currentThreadCount

            return json.dumps(common.GetFileRangeLines(path, startIdx, endIdx))

        app.run(self.listenIp, port=self.listenPort)


if __name__ == '__main__':
    Server().StartUp()
