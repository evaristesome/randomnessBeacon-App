
'''
This is the RNG server code. This is what would be talking to the HSM in order
to get random bits and so on. Right now we use simple functions to replicate
some of this behavior.
'''

import zmq
import sys
from datetime import datetime
from cryptoHeaven import main, openSession
session = openSession()

import logging
logging.basicConfig(filename='RNGLog.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
#logger=logging.getLogger(__name__)

'''
utcTime function return the UTC time in a given format for further processing
'''
def utcTime():
    try:
        currentTime = datetime.utcnow()
        timeFormat = datetime.strftime(currentTime, '%Y-%m-%d %H:%M:%S')
        return timeFormat
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)


'''
assemble_message function:
    1. retrieves signed messages from cryptoHeaven/main
    2. concatenates all retrieved message including utcTime
    3. returns the concatenate message to rng_handler function for further processing.
'''
def assemble_message(session):
    try:
        messageSigned, digest, sourceRNG1, sourceRNG2, sourceHSM, sourcePaul = main(session)
        message = str(messageSigned) + "*****" + str(digest) + "*****" + str(utcTime()) + "*****" + str(sourceRNG1) + "*****" + str(sourceRNG2) + "*****" + str(sourceHSM) + "*****" + str(sourcePaul)
        if len(message) < 20:
            assemble_message(session)
        return(message)        #must be concatenated
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)

'''
rng_handler function continuously run and look for process incoming requests. 
'''
def rng_handler(socket):
    try:
        while True:
            remoteRequest = socket.recv()
            if remoteRequest.decode() == "END":
                print('Ending RNG on port', socket)
                break

            msgToSend = assemble_message(session)
            # Return the requested message
            socket.send_string("%s" % (msgToSend))
            # time.sleep(sleepTime)
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)

'''
create_socket function creates the approriate REP socket for the RNG server
'''
def create_socket(port = 5005):
    try:
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
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)

if __name__ == '__main__':
    try:
        port = None
        # Check to see if there are command line inputs for the port.
        # Can all this from the command line as "python3 rngServer 5005" for example
        for arg in sys.argv[1:]:
            if arg is not None:
                port = arg
        create_socket(port)
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)
