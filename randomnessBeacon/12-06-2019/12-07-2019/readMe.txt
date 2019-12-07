The program randomnessBeacon consists of generating truly random numbers. The program combined different tasks and naturally used several functions to reach its goal. The program contains essentially six python files.

cryptoHeaven.py:
it offers the possibility to 
Open a session on the HSM, openSession(), and return the session ID;
Authenticate, authenticate(x), and return the key and a random number generated from the HSM;
Sign multiple messages, complexSigning(x,y,z,w,k) where “k” is the key;
Sign a single message, SingleSigning(m, k);
Delete the HSM key, cleanUp(k);
Main function, main(session), that retrieves external sources RNG, authenticate the session, signed combined and individual random numbers. “main(session)” returns its outputs to rngServer.py assemble_message(session).

rngServer.py:
it offers the following functions:
Assemble messages, assemble_message(session), received from the HSM;
RNG Handler, rng_handler(x), looking for incoming process;
Create socket, create_socket(y), for the RNG server.

beaconEngine4.py
It offers the following:
Getting the random numbers, get_rng(socket),  from the server “rngServer.py”, and return it to engine(q1,q2);
Create RNG client socket, create_rng_client_socket(x);
Start the RNG clients, start_rng_clients(x);
Start a single RNG, start_single_rng(x);
Start RNGs in their own process, start_rngs(x);
Stop RNGs, stop_rngs(x,y), to clean up and stop the program;
Engine, engine(q1,q2), to enqueue data received from get_rng(socket)

RNGs.py:
Offers the following:
A generic function, RNG(), to generate a random number and return it to the HSM;
Paul RSA simple algorithm, PaulRSASimple(), to generate a random number and return it to the HSM;
Parsing function, parseHourDayMonthYear() --→ will be removed soon

dataContainment.py:
offers the following:
Sql table function, sqlTable();
store beacons, insertBeaconinfo(x) into the database;
Retrieval data from the queue, collectData(q1,q2) 

queueTransit.py:
Allows two different processes, beaconEngine4.py engine(q1,q2) and dataContainment colectData(q1,q2), to exchange data.



