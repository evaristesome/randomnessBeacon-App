import zmq
import time
import sys
import rngServer as rngServer #This is the code in rngServer.py to launch a RNG
import multiprocessing
import copy

# These are globals. Need to do some simple clean up to remove them.
#ports = []
#rngJobs = []
#rngClients = []

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
        self.randBits = []
        self.hasher = []
        self.signer = []
        self.currentTime = []
    # This function talks to a given RNG and receives its output.
    def get_rng(self,socket):
        # Send the request to this particular RNG
        socket.send(b"update")
        # Get the RNG and timestamp
        msg = socket.recv_string()
        msg = msg.split('*****')
        randomBits = int(msg[0])
        hash = msg[1]
        signed = msg[2]
        currentTime = msg[3]
        # now we return the randombits and time stamp.
        # #message = str(randomMessage) + ',' +str(digest) + ',' + str(messageSigned) + ',' + str(timeUTC)
        return(randomBits, hash, signed, currentTime)

    # Create a single RNG client socket to connect to a RNG server
    def create_rng_client_socket(self,port = 5005):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:" + str(port))
        return(socket)

    # Now we can start up all of the RNG clients to talk to all of the servers
    def start_rng_clients(self,nClients = 1):
        global ports, rngClients
        startPort = 5005
        for p in range(nClients):
            port = startPort + p
            ports.append(port)
            print('rng client launching on', port )
            clientSocket = self.create_rng_client_socket(port)
            rngClients.append(clientSocket)
        return(ports, rngClients)

    # This next part could be carried out in a separate file or command line, but
    # I do it here for convenience.

    # Launch a single RNG server
    def start_single_rng(self, port):
        rngServer.create_socket(port)

    # Start a number of different RNGs all in their own process.
    def start_rngs(self, ports):
        # global rngJobs # @TODO: remove this
        for p in ports:
            print('rng launching on', p )
            # The standard multiprocessing code to launch a function in a separate process
            rng = multiprocessing.Process(target=self.start_single_rng, args=(p,))
            rngJobs.append(rng)
            rng.start()
        return(rngJobs)

    # Code to clean up and stop the RNGs. Not completed yet:
    def stop_rngs(self, rngJobs, rngClients):
        #global ports, rngJobs, rngClients
        # First tell all the RNG server handlers to stop
        for socket in rngClients:
            socket.send(b"END")
        # Next we join all the outstanding RNG threads
        for rng in rngJobs:
            rng.join()
        rngJobs = []
        ports = []
        rngClients = []
        sys.exit(0)
    #return data to client for further processing
    def collectData(self):
        randBitsTemp = self.randBits
        hasherTemp = self.hasher
        signerTemp = self.signer
        currentTimeTemp = self.currentTime
        #return randBitsTemp, hasherTemp, signerTemp, currentTimeTemp
        return self.randBits, self.hasher, self.signer, self.currentTime
        #print(randBitsTemp)
        #print(hasherTemp)
        #print(signerTemp)
        #print(currentTimeTemp)

    # The brains of the program.
    def engine(self, n = 1):
        global ports, rngJobs, rngClients
        print('starting RNG Clients')
        ports, rngClients = self.start_rng_clients(n)
        print('')
        print('starting RNGs')
        rngJobs = self.start_rngs(ports)
        print('')
        print('Beginning test loop')
        nLoop = 10 # We could change this to a "while True:" loop to make it a handler
        counter1 = True
        counter2 = False
        #for i in range(nLoop):
        try:
            while True:
                # A function to send data for external use
                # First, we will query each of the RNGs for their bits and time stamp
                #global currentTime, randBits, hasher, signer
                for socket in rngClients:
                    #bits, tim = get_rng(socket)        #randomBits, hash, signed, currentTime
                    bits, hash, signed, tim = self.get_rng(socket)
                    self.randBits.append(bits)
                    self.hasher.append(hash)
                    self.signer.append(signed)
                    self.currentTime.append(tim)

                print('Random Bits & Time: ' + str(self.randBits) + ' ' + str(self.currentTime))

                self.collectData()

                #if counter2 ==True:
                print('Current time: ' + str(self.currentTime))
                print('Random Bits: ' + str(self.randBits))
                print('Hash Message: ' + str(self.hasher))
                print('Signed Message: ' + str(self.signer))

                time.sleep(1)
                self.randBits.clear()
                self.hasher.clear()
                self.signer.clear()
                self.currentTime.clear()

                time.sleep(1)
        except  AssertionError as error:         #use KeyboardInterrupt for future
            print (error)

if __name__ == '__main__':
    ports = []
    rngJobs = []
    rngClients = []
    n = 1 # number of RNGs to spawn.
    objectBeaconEngine = beaconEngineProcess()
    objectBeaconEngine.engine(n)