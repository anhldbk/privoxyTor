#-------------------------------------------------------------------------------
# Name:         privoxyTor
# Purpose:      Using multiple Tor connections simultaneously
#
# Narrator:     In a project, I wanted to use multiple Tor connections to
#               anonymously crawl a website. I googled and got a good answer for
#               using one instance of Tor at:
#               http://stackoverflow.com/questions/9887505/changing-tor-identity-inside-python-script
#               But for multiple instances, how could we could that? I decided
#               to write a Python script automating the configuration process and
#               making Tor easier to use. I hope it works out well for you!
#
# Usage:        Before running the demo accompanied with this script, you have
#               to prepare prepare directory /abstract:
#               1. Copy the installation of Tor to /abstract/tor
#               2. Copy /conf/tr to  /abstract/tor
#               3. Copy the installation of Privoxy to /abstract/privoxy
#               4. Copy /conf/privoxy to  /abstract/privoxy
#
# Author:       Anh Le
#
# Created:      27/12/2013
# Copyright:    (c) AnhLD 2013
# Licence:      LGPL-2.1
#-------------------------------------------------------------------------------


import shutil, errno
import os
import os.path
import subprocess
import time
import socket
from subprocess import Popen, CREATE_NEW_CONSOLE
from Queue import Queue
import urllib2



class PrivoxyTor:
    # Class defining a proxy to work with Tor and Privoxy
    def __init__(self, controlPort, privoxyPort):
        # Creates a proxy based on a pair of a Tor's control port and
        # a Privoxy's listening port
        # controlPort: a Tor's control port
        # privoxyProt: a Privoxy's listening port
        self.proxyHandler = urllib2.ProxyHandler({"http" : "127.0.0.1:%s" % privoxyPort})
        self.__privoxyProt = privoxyPort
        self.__controlPort = controlPort

    def newId2(self, wait = 5):
        # Acquires a new Identity for our connection
        # wait: time to wait (in second)
        # return: nothing

        conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=self.__controlPort, passphrase="123")
        conn.send_signal("NEWNYM")
        time.sleep(wait)

    def newId(self, wait = 2):
        # Acquires a new Identity for our connection
        # wait: time to wait (in second)
        # return: nothing
        try:
            tor_ctrl = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            tor_ctrl.connect(("127.0.0.1", self.__controlPort))
            tor_ctrl.send('AUTHENTICATE "{}"\r\nSIGNAL NEWNYM\r\n'.format("123"))
            response = tor_ctrl.recv(1024)
            if response != '250 OK\r\n250 OK\r\n':
                sys.stderr.write('Unexpected response from Tor control port: {}\n'.format(response))
        except Exception, e:
            sys.stderr.write('Error connecting to Tor control port: {}\n'.format(repr(e)))
        time.sleep(wait)

class PrivoxyTorManager:
    # Class automating the process of configuring and launching multiple
    # instances of Tor and Privoxy
    def __init__(self, controlPort, socksPort, privoxyPort):
        # Creates an instance of PrivoxyTorManager
        # controlPort: starting Control port for 1st Tor instance
        # socksPort: starting Socks port for 1st Tor instance
        # privoxyPort: starting port for 1st Privoxy instance to listen
        # return: Nothing
        self.controlPort = controlPort
        self.socksPort = socksPort
        self.privoxyPort = privoxyPort
        self.rootDir = self.__getWorkingDir()

    def __copyDir(self, src, dst):
        # Copies a directory to another one
        # src: source directory
        # dst: destination one
        # return: Nothing
        try:
            shutil.copytree(src, dst)
        except OSError as exc: # python >2.5
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else: raise

    def create(self, instanceNum):
        # Creates several instances of Tor-Privoxy connections
        # instanceNum: number of instances to create
        # return: a list of PrivoxyTor instances
        directory = self.rootDir+ '/instances'
        controlPort = self.controlPort
        privoxyPort = self.privoxyPort

        # remove the previous directory /instances
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)

        for i in range(0, instanceNum):
            print 'Creating instance %s' % i
            self.__createInstance(i)

        # wait for circuits established
        time.sleep(10)

        # return list of PrivoxyTor instances
        proxies = []
        for i in range(0, instanceNum):
            proxies+=[PrivoxyTor(controlPort, privoxyPort)]
            controlPort+=2
            privoxyPort+=2

        return proxies


    def __getWorkingDir(self):
        # Gets the current working directory of our script
        # return: The directory containing our script

        ret = os.path.abspath(os.path.join(__file__, os.pardir))
        ret = ret.replace('\\', '/') # for windows
        return ret

    def __alterFileContent(self, path, newContent):
        # Alters the content of a specific file
        # path: path to the file
        # newContent: new content
        # return: Nothing
        try:
            f = open(path, "w")
            f.write(newContent)
            f.close()
        except:
            pass

    def __createInstance(self, index):
        # Create a new instance of Tor-Privoxy proxy
        # index: Index of the proxy
        # return: Nothing

        print 'Tor: controlPort = %s socksPort = %s\nPrivoxy listenPort=%s\n' % (self.controlPort, self.socksPort, self.privoxyPort)
        directory = '%s/instances/%s' % (self.rootDir, index)

        # Copy the whole directory ./abstract to directory ./instances/<index>
        self.__copyDir('./abstract', directory)

        # open tor config file then start it
        with open(directory + '/tor/torrc', 'r') as content_file:
            content = content_file.read()
            content = content % (self.controlPort,self.socksPort)
            self.__alterFileContent(directory + '/tor/torrc', content)
            os.chdir(directory + '/tor/')
            Popen('tor -f torrc', creationflags=subprocess.SW_HIDE)

        # do the same thing with privoxy
        with open(directory + '/privoxy/config.txt', 'r') as content_file:
            content = content_file.read()
            content = content % (self.privoxyPort, self.socksPort)
            self.__alterFileContent(directory + '/privoxy/config.txt', content)
            os.chdir(directory + '/privoxy/')
            Popen('privoxy', creationflags=subprocess.SW_HIDE)

        # Modify ports for the next PrivoxyTor instances
        self.controlPort += 2
        self.socksPort += 2
        self.privoxyPort += 2

        # Restore the working directory
        os.chdir(self.rootDir)


def torCheck():
    # This is an example of using the 2 classes above
    # Scenario: Creates 2 PrivoxyTor instances and prints out associated IPs for
    # each established connection
    torInstance = 1 # number of PrivoxyTor instances to make
    torControlPort = 9051
    torSocksPort = 9050
    privoxyPort = 8118
    tm = PrivoxyTorManager(torControlPort, torSocksPort, privoxyPort)
    proxies = tm.create(torInstance)

    # select the first one
    torProxy = proxies[0]

    while (True):
        try:
            # acquire a new circuit
            torProxy.newId();

            # establish a connection to a web service to get the associated IP
            opener = urllib2.build_opener(torProxy.proxyHandler)
            urllib2.install_opener(opener)
            url = 'http://api.externalip.net/ip/'

            # print out the IP
            print('%s\n' % (urllib2.urlopen(url).read()))
        except:
            pass

torCheck()
