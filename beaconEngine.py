import zmq
import time
import sys
import rngServer as rngServer #This is the code in rngServer.py to launch a RNG
import multiprocessing

# These are globals. Need to do some simple clean up to remove them.
ports = []
rngJobs = []
rngClients = []

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

# This function talks to a given RNG and receives its output.
def get_rng(socket):
    # Send the request to this particular RNG
    socket.send(b"update")
    # Get the RNG and timestamp
    msg = socket.recv_string()
    msg = msg.split(',')
    randomBits = int(msg[0])
    currentTime = msg[1]
    # print(randomBits, currentTime)
    # now we return the randombits and time stamp.
    return(randomBits, currentTime)

# Create a single RNG client socket to connect to a RNG server
def create_rng_client_socket(port = 5005):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:" + str(port))
    return(socket)

# Now we can start up all of the RNG clients to talk to all of the servers
def start_rng_clients(nClients = 1):
    global ports, rngClients
    startPort = 5005
    for p in range(nClients):
        port = startPort + p
        ports.append(port)
        print('rng client launching on', port )
        clientSocket = create_rng_client_socket(port)
        rngClients.append(clientSocket)
    return(ports, rngClients)

# This next part could be carried out in a separate file or command line, but
# I do it here for convenience.

# Launch a single RNG server
def start_single_rng(port):
    rngServer.create_socket(port)

# Start a number of different RNGs all in their own process.
def start_rngs(ports):
    # global rngJobs # @TODO: remove this
    for p in ports:
        print('rng launching on', p )
        # The standard multiprocessing code to launch a function in a separate process
        rng = multiprocessing.Process(target=start_single_rng, args=(p,))
        rngJobs.append(rng)
        rng.start()
    return(rngJobs)

# Code to clean up and stop the RNGs. Not completed yet:
def stop_rngs(rngJobs, rngClients):
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

# The brains of the program.
def engine(n = 1):
    print('starting RNG Clients')
    ports, rngClients = start_rng_clients(n)
    print('')
    print('starting RNGs')
    rngJobs = start_rngs(ports)
    print('')
    print('Beginning test loop')
    nLoop = 10 # We could change this to a "while True:" loop to make it a handler
    #for i in range(nLoop):
    try:
        while True:
            # First, we will query each of the RNGs for their bits and time stamp
            randBits = []
            currentTime = []
            for socket in rngClients:
                bits, tim = get_rng(socket)
                randBits.append(bits)
                currentTime.append(tim)
            print('Random Bits & Time: ' + str(randBits) + ' ' + str(currentTime))
            #print('Current Hashed Bits', hashedBits)
            time.sleep(0)
    except  AssertionError as error:         #use KeyboardInterrupt for future
        print (error)

    #print('')
    #print('Stopping RNGS')
    #stop_rngs(rngJobs, rngClients)

    #Then we could sign and store to a database

if __name__ == '__main__':
    n = 3 # number of RNGs to spawn.
    engine(n)