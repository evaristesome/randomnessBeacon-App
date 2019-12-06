import zmq
import time
import sys
import rngServer as rngServer #This is the code in rngServer.py to launch a RNG
import multiprocessing
import copy
import convertion
import queue
import threading
import sqlite3
from sqlite3 import Error
from standardCryptoTask import standardCryptoFunction
q = queue.Queue()
import os
#duration  = 3000 # milliseconds
#frequency = 1000 # Hertz
#from queueTransit import *

import logging
logging.basicConfig(filename='RNGLog.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
#logger=logging.getLogger(__name__)

'''
The following few functions are for the RNG clients. We need one socket connection
for each RNG that is launched. The clients should be launched first, but it doesn't
really matter for how this is encoded.

The program works as follows. First a number of client sockets are launched to to
connect to each of the RNGs. The RNGs are then launched each in it's own process.
These could be launched from the command line as well if needed. The engine() function
each round communicates to each rng and asks it for random bits. Each rng returns
a 512 bit random number along with a timestamp. Once bits from each RNG are collected
they are hashed (in this first case just XORed) together. This result along with
a timetamp can be used as part of a record and connected to a database (not done here).
'''
class beaconEngineProcess:

    def __init__(self):
        self.messageSigned  = []
        self.digest = []
        self.currentTime    = []
        self.sourceRNG1 = []
        self.sourceRNG2 = []
        self.sourceHSM = []
        self.sourcePaul = []

        self.ports = []
        self.rngJobs = []
        self.rngClients = []

    # This function talks to a given RNG and receives its output.
    def get_rng(self,socket):
        try:
            # Send the request to this particular RNG
            socket.send(b"update")
            # Get the RNG and timestamp
            msg = socket.recv_string()
            #time.sleep(1)
            #print('bloc message', msg)
            #msg = msg.split("*****")
            #Accessing the parsed lists by row
            msg = [x for x in msg.split("*****") if x.strip() != ""]
            if msg[0] == 'None':
                self.get_rng(socket)
            #print(msg)
            #print('message split:', msg)

            messageSigned = msg[0]
            digest = msg[1]
            currentTime = msg[2]
            sourceRNG1 = msg[3]
            sourceRNG2 = msg[4]
            sourceHSM = msg[5]
            sourcePaul = msg[6]
            return messageSigned, digest, currentTime, sourceRNG1, sourceRNG2, sourceHSM, sourcePaul
        except Exception as e:
            logging.error("Exception occured: ", exc_info=True)
            pass

    # Create a single RNG client socket to connect to a RNG server
    def create_rng_client_socket(self,port = 5005):
        try:
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://localhost:" + str(port))
            return(socket)
        except Exception as e:
            logging.error("Exception occured: ", exc_info=True)

    # Now we can start up all of the RNG clients to talk to all of the servers
    def start_rng_clients(self,nClients = 1):
        try:
            #global ports, rngClients
            startPort = 5005
            for p in range(nClients):
                port = startPort + p
                self.ports.append(port)
                print('rng client launching on', port )
                clientSocket = self.create_rng_client_socket(port)
                self.rngClients.append(clientSocket)
            return(self.ports, self.rngClients)
        except Exception as e:
            logging.error("Exception occured: ", exc_info=True)

    # This next part could be carried out in a separate file or command line, but
    # I do it here for convenience.

    # Launch a single RNG server
    def start_single_rng(self, port):
        try:
            rngServer.create_socket(port)
        except Exception as e:
            logging.error("Exception occured: ", exc_info=True)

    # Start a number of different RNGs all in their own process.
    def start_rngs(self, ports):
        try:
            # global rngJobs # @TODO: remove this
            for p in self.ports:
                print('rng launching on', p )
                # The standard multiprocessing code to launch a function in a separate process
                rng = multiprocessing.Process(target=self.start_single_rng, args=(p,))
                self.rngJobs.append(rng)
                rng.start()
            return(self.rngJobs)
        except Exception as e:
            logging.error("Exception occured: ", exc_info=True)

    # Code to clean up and stop the RNGs. Not completed yet:
    def stop_rngs(self, rngJobs, rngClients):
        try:
            #global ports, rngJobs, rngClients
            # First tell all the RNG server handlers to stop
            for socket in self.rngClients:
                socket.send(b"END")
            # Next we join all the outstanding RNG threads
            for rng in self.rngJobs:
                rng.join()
            self.rngJobs = []
            self.ports = []
            self.rngClients = []
            sys.exit(0)
        except Exception as e:
            logging.error("Exception occured: ", exc_info=True)


    # The brains of the program.
    def engine(self, queueS1, queueS2):
    #def engine(self):
        try:
            n=1
            global ports, rngJobs, rngClients
            print('starting RNG Clients')
            self.ports, self.rngClients = self.start_rng_clients(n)
            print('')
            print('starting RNGs')
            self.rngJobs = self.start_rngs(self.ports)
            print('')
            print('Beginning test loop')
            logging.warning('Starting RNG client')

        except Exception as e:
            logging.error("Exception occured: ", exc_info=True)

        try:
            while True:
                # A function to send data for external use
                # First, we will query each of the RNGs for their bits and time stamp
                #global currentTime, randBits, hasher, signer
                for socket in self.rngClients:
                    #message signed, hashed message, current Time
                    messageSigned, digest, currentTime, sourceRNG1, sourceRNG2, sourceHSM, sourcePaul  = self.get_rng(socket)
                    self.messageSigned.append(messageSigned)
                    self.digest.append(digest)
                    self.currentTime.append(currentTime)
                    self.sourceRNG1.append(sourceRNG1)
                    self.sourceRNG2.append(sourceRNG2)
                    self.sourceHSM.append(sourceHSM)
                    self.sourcePaul.append(sourcePaul)

                queueS1.put(self.messageSigned[0])
                queueS1.put(self.digest[0])
                queueS1.put(self.currentTime[0])        #queueS1.put(self.currentTime[0])
                queueS1.put(self.sourceRNG1[0])
                queueS1.put(self.sourceRNG2[0])
                queueS1.put(self.sourceHSM[0])
                queueS1.put(self.sourcePaul[0])

                self.messageSigned.clear()
                self.currentTime.clear()
                self.digest.clear()
                self.sourceRNG1.clear()
                self.sourceRNG2.clear()
                self.sourceHSM.clear()
                self.sourcePaul.clear()

                #time.sleep(1)
        except Exception as e:
            logging.error("Exception occured: ", exc_info=True)

#if __name__ == '__main__':
    #ports = []
    #rngJobs = []
    #rngClients = []

    #db = sqlite3.connect('randomnessBeacon')
    #objectBeaconEngine = beaconEngineProcess()

    #from dataContainment import dataContainment
    #objectDataContainment = dataContainment()

    #from test import q_pocess
    #q = q_pocess()


    #t1 = threading.Thread(target=objectBeaconEngine.engine)
    #t2 = threading.Thread(target=objectBeaconEngine.collectData)
    #t1.start()
    #t2.start()
    #t1.daemon = True


    #counter =1
    #n = 1 # number of RNGs to spawn.

    #objectBeaconEngine.engine()