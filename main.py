#!/usr/bin/env python

import sys
import logging
import argparse
import configparser
import time
import queue
import socket
from threading import Thread
from SimpleXMLRPCServer import SimpleXMLRPCServer
from random import randint

sys.path.append('./aio/')
from aio_selftest import AIOSelfTest
from aio_serialprotocol import AIOSerialProtocol
from daemon import Daemon

#import serial
#from twisted.internet.protocol import DatagramProtocol
#from twisted.internet import reactor


class AIO(Daemon):
    def __init__(self, pidFile='/tmp/aio.pid', stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.logLevel = 0
        self.workerName = "AIO"
        self.Interval = 10
        self.aioSP = False                                       # SerialProtocol Object
        self.loadFunction1, self.loadFunction2 = False, False
        self.loadFunction3, self.loadFunction4 = False, False    # SerialProtocol Load Function handlers
        self.XMLRPCServer = True
        self.NetClient = False
        self.NetClientProtocol = False

        # load configuration file
        self.config = configparser.ConfigParser()
        self.config.read("/etc/aio.conf")
        if (not self.config.has_section("General")):
            logging.critical("AIO Cannot load config file!")
            sys.exit()

        if (self.config.has_option("General", "PidFile")):
            self.pidFile = self.config.get("General", "PidFile")
        else:
            self.pidFile = pidFile

        if (self.config.has_option("General", "LogFile")):
            self.logFile = self.config.get("General", "LogFile")
        else:
            self.logFile = "aio.log"

        if (self.config.has_option("General", "LogLevel")):
            self.setLogLevel(self.config.get("General", "LogLevel").upper())
        else:
            self.logLevel = logging.INFO

    def init(self):
        self.logInit()
        logging.debug("AIO Init")
        sections = self.config.sections()
        logging.debug("AIO Config" + str(sections))
        if (self.config.has_option("General", "MQPollingInterval")):
            self.MQPollingInterval = self.config.getfloat("General", "MQPollingInterval")
        else:
            self.MQPollingInterval = 0.05

        if (self.config.has_option("NetClient", "Protocol")):
            if (self.config.get("NetClient", "Protocol") == "UDP"):
                self.destinationIP = self.config.get("NetClient", "DestinationIP")
                self.destinationPort = self.config.getint("NetClient", "DestinationPort")
                self.NetClient = True
                self.NetClientProtocol = socket.SOCK_DGRAM
                logging.debug("AIO Config NetClient: UDP " + str(self.destinationIP) + ":" + str(self.destinationPort))
            elif (self.config.get("NetClient", "Protocol") == "TCP"):
                self.destinationIP = self.config.get("NetClient", "DestinationIP")
                self.destinationPort = self.config.getint("NetClient", "DestinationPort")
                self.NetClient = True
                self.NetClientProtocol = socket.SOCK_STREAM
                logging.debug("AIO Config NetClient: TCP " + str(self.destinationIP) + ":" + str(self.destinationPort))
            else:
                logging.error("AIO Config NetClient bad protocol specified!")

        self.aioSP = AIOSerialProtocol()

    def logInit(self):
        """ logInit() -> null
        Sets initial logging parameters
        """
        logging.basicConfig(filename=self.logFile, format='%(asctime)s;%(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=self.logLevel)

    def logLevelToInt(self, x):
        """logLevelToInt(logLevelStr) -> logLevelInt
        Returns int representation of logLevelStr
        """
        return {
            'DEBUG': 10,
            'INFO': 20,
            'WARNING': 30,
            'ERROR': 40,
            'CRITICAL': 50
            }.get(x, 30)

    def setLogLevel(self, lvl):
        self.logLevel = self.logLevelToInt(lvl)

    def run(self):
        logging.debug("AIO daemon Init")
        #try:
            #ser = serial.Serial('/dev/ttyUSB0', 19200, timeout=5)
            #x = ser.read()          # read one byte
            #s = ser.read(10)        # read up to ten bytes (timeout)
            #line = ser.readline()   # read a '\n' terminated line
            #logging.debug("Serial 1: " + repr(line))
            #ser.close()
        #except:
            #logging.debug("Serial Error")

        if (self.XMLRPCServer):
            logging.info("AIO RPC Server Init Thread")
            XMLRPCServer = SimpleXMLRPCServer(('localhost', 9000), logRequests=False)
            XMLRPCServer.register_introspection_functions()
            XMLRPCServer.register_function(self.daemonStop, 'AIO.Stop')
            thread = Thread(target=XMLRPCServer.serve_forever)
            thread.daemon = True
            thread.start()

        self.loadFunction1 = self.aioSP.loadHCHDM
        self.loadFunction2 = self.aioSP.loadHEHDT
        self.loadFunction3 = self.aioSP.loadPRDID
        self.loadFunction4 = self.aioSP.loadPRDID

        for t in range(1, 5):
            mode = self.config.getint("Serial" + str(t), "Mode")
            logging.debug("AIO Config Serial" + repr(t) + " mode " + repr(mode))
            if (mode == 1):
                logging.info("AIO Serial" + str(t) + " Init Thread ")
                thread = Thread(target=self.readSerial, args=(t,))
                thread.daemon = True
                thread.start()

        if (self.NetClient):
            logging.info("AIO UDP Client Init Thread")
            thread = Thread(target=self.writeUDPSocket)
            thread.daemon = True
            thread.start()

        while True:
            logging.debug("AIO Main Worker")
            # Read all Threads to MQ
            try:
                block = mqRead.get(block=False, timeout=0)
                port = int(block[0])
                data = block[1]
                logging.info("AIO Serial" + str(port) + " Thread read data=" + repr(data))
                mqRead.task_done()
                if (port == 1):
                    self.loadFunction1(data)
                elif (port == 2):
                    self.loadFunction2(data)
                elif (port == 3):
                    self.loadFunction3(data)
                elif (port == 4):
                    self.loadFunction4(data)
            except:
                logging.debug("AIO Serial Queue read timeout")

            # Write all Thread to MQ
            if (port == 1):
                data = self.aioSP.generatePRDID()
                logging.info("AIO UDP Thread write data=" + repr(data))
                mqWrite.put(data)
                logging.debug("AIO UDP Queue size: " + str(mqWrite.qsize()))

            # Wait for read MQ
            logging.debug("AIO Serial Queue size: " + str(mqRead.qsize()))
            while (mqRead.qsize() == 0):
                time.sleep(self.MQPollingInterval)

    def readSerial(self, port=0):
        block = [port, '']
        self.aioSP.setPitch(1.00)
        self.aioSP.setRoll(3.00)
        self.aioSP.setHeading(13.05)
        self.aioSP.setDepth(-314.0)

        # testing generator
        if (port == 1):
            block.insert(1, self.aioSP.generateHCHDM())
        elif (port == 2):
            block.insert(1, self.aioSP.generateHEHDT())
        else:
            block.insert(1, "Dumb string")
        #

        while True:
            mqRead.put(block)
            time.sleep(1)

    def writeSerial(self, block):
        port = block[0]
        data = block[1]
        logging.info("AIO Thread write" + str(port) + " data=" + repr(data))

    def writeUDPSocket(self):
        client = socket.socket(socket.AF_INET, self.NetClientProtocol)
        while True:
            data = mqWrite.get()
            client.sendto(data, (self.destinationIP, self.destinationPort))
            mqWrite.task_done()
            while (mqWrite.qsize() == 0):
                time.sleep(0.5)
        client.close()

    def daemonStart(self):
        logging.info("AIO starting daemon")
        self.start()

    def daemonStop(self):
        logging.info("AIO stopping daemon")
        self.stop()

    def daemonRestart(self):
        logging.info("AIO restarting daemon")
        self.restart()

    def selftest(self):
        logging.info("AIO SelfTest Started")
        st = AIOSelfTest()
        st.selfTest()
        logging.info("AIO SelfTest Stopped")

# Main program starting point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(epilog="All rights reserved.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--selftest', help="perform some internal self tests", action="store_true")
    group.add_argument('--daemon-start', help="run as a daemon", action="store_true")
    group.add_argument('--daemon-stop', help="stop running daemon", action="store_true")
    group.add_argument('--daemon-restart', help="restart daemon", action="store_true")
    parser.add_argument('--loglevel', help="change log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    args = parser.parse_args()

    mqRead = queue.queue()
    mqWrite = queue.queue()

# Initial config section
    app = AIO()
    if (args.loglevel):
        app.setLogLevel(args.loglevel.upper())

# Functions section
    if (args.selftest):
        app.init()
        app.selftest()
    elif (args.daemon_start):
        app.init()
        app.daemonStart()
    elif (args.daemon_stop):
        app.init()
        app.daemonStop()
    elif (args.daemon_restart):
        app.init()
        app.daemonRestart()
    else:
        parser.print_help()
