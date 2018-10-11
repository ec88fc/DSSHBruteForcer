'''
clients for do ssh brute force
'''

import requests
import sys
from connection import Connection


class Client():
    def __init__(self):
        self.info = 'Distribution SSH Brute Forcer'
        self.targetIp = ""
        self.targetPort = 22
        self.targets = []
        self.usernames = []
        self.passwords = []
        self.connections = []
        self.amountOfThreads = 0
        self.currentThreadCount = 0
        self.timeoutTime = 0
        self.outputFileName = ""
        self.singleMode = False
        self.verbose = False


if __name__ == '__main__':
    # todo
    pass
