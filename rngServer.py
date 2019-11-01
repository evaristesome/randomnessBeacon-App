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
from cryptography.hazmat.primitives.asymmetric import padding, ec   #for signing

import zmq
import sys
from datetime import datetime
from cryptoHeaven import main, openSession
import convertion
#session = openSession()

#Define function UTC time  ???In case of no internet connection, how utc gets updated?
def utcTime():
    currentTime = datetime.utcnow()
    timeFormat = datetime.strftime(currentTime, '%Y-%m-%d %H:%M:%S')
    return timeFormat

# Retrieve  message from HSM and assemble with
def assemble_message(session):
    #digest, messageSigned, pub = main(session)
    digest, messageSigned, pub = main(session)
    hashtype = hashes.SHA512()
    pub.verify(messageSigned, digest, ec.ECDSA(hashtype))              # verify using ec.ECDSA
    #pub.verify(messageSigned, digest, padding.PKCS1v15(), hashtype)     #verify using pkcs1v15

    message = str(messageSigned) +  '*****' + str(digest) + '*****' + str(utcTime())
    return(message)         #must be concatenated: signMessage, pub_key

# This is the loop to run to process incoming requests
def rng_handler(socket):
    # sleepTime = 10
    session = openSession()
    while True:
        remoteRequest = socket.recv()
        #print(remoteRequest.decode())
        # Magic word to terminate the handler.
        if remoteRequest.decode() == "END":
            print('Ending RNG on port', socket)
            break

        msgToSend = assemble_message(session)
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
