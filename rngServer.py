'''
This is the RNG server code. This is what would be talking to the HSM in order
to get random bits and so on. Right now we use simple functions to replicate
some of this behavior.
'''
'''
This is the RNG server code. This is what would be talking to the HSM in order
to get random bits and so on. Right now we use simple functions to replicate
some of this behavior.
'''
from cryptography.hazmat.primitives import hashes       #for signing
from cryptography.hazmat.primitives.asymmetric import utils     #for hashing larger message
from cryptography.hazmat.primitives.asymmetric import padding, ec   #for signing

import zmq
from random import randrange
import time
import sys
import datetime
#from test import RSAEncryptionFunctions
from cryptoHeaven import main
#from test2 import main

#objectEncrypt = RSAEncryptionFunctions()


#Define function UTC time  ???In case of no internet connection, how utc gets updated?
def utcTime():
    return datetime.datetime.utcnow()

#verification
def verifyHSMSource(pub, resp, data):
    try:
        pub.verify(resp, str(data).encode('utf8'), ec.ECDSA(hashes.SHA512))
    except Exception as e:
        raise e
    return True

# mesage to reurn
def assemble_message():
    randomMessage = main()
    print(randomMessage)
    #randomMessage = objectEncrypt.main()
    #randomMessage = objectEncrypt.Random256()
    #randomMessage = main()
    timeUTC = utcTime()
    message = str(randomMessage) + ',' + str(timeUTC)
    return(message)         #must be concatenated: signMessage, pub_key

# This is the loop to run to process incoming requests
def rng_handler(socket):
    # sleepTime = 10
    while True:
        remoteRequest = socket.recv()
        # Magic word to terminate the handler.
        if remoteRequest.decode() == "END":
            print('Ending RNG on port', socket)
            break

        msgToSend = assemble_message()
        # Return the requested message
        socket.send_string("%s" % (msgToSend))
        # time.sleep(sleepTime)

# Create the approriate REP socket for the RNG server
def create_socket(port = 5005):
    if port is None:
        port = 5005
    for arg in sys.argv[1:]:
        if arg is not None:
            port = arg
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:" + str(port))
    # Launch the handler
    rng_handler(socket)

if __name__ == '__main__':
    port = None
    # Check to see if there are command line inputs for the port.
    # Can all this from the command line as "python3 rngServer 5005" for example
    for arg in sys.argv[1:]:
        if arg is not None:
            port = arg
    create_socket(port)
