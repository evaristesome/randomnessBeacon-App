Randomness Beacon Generation Program

The program randomnessBeacon consists of generating truly random numbers. 
It combines different tasks and used several functions to reach its goal. 
The current version uses Yubico Hardware Security Module 2, but can be easily modified to run without HSM.
The program uses Python programming and contains essentially six files.

cryptoHeaven:
It offers the capability to 
	- Open a session on the HSM, openSession(), and return the session ID;
	- Authenticate, authenticate(ID), and return the key, and a random number generated from the HSM;
	- Sign multiple messages, complexSigning(x,y,z,w,k) where “k” is the key;
	- Sign a single message, SingleSigning(m, k);
	- Delete the key generated from the HSM, cleanUp(k);
	- Main function, main(session), retrieves RNG from external sources, authenticate the session, signed combined and individual random numbers. “main(session)” returns its outputs to rngServer assemble_message(session).

rngServer:
Offers the following tasks to:
	- Assemble messages, assemble_message(session), received from the HSM;
	- RNG Handler, rng_handler(x), look for incoming process;
	- Create socket, create_socket(y), for the RNG server.

beaconEngine4:
It offers the following tasks:
	- Getting the random numbers, get_rng(socket),  from the server rngServer, and return it to engine(q1,q2);
	- Create RNG client socket, create_rng_client_socket(x);
	- Start the RNG clients, start_rng_clients(x);
	- Start a single RNG, start_single_rng(x);
	- Start RNGs in their own process, start_rngs(x);
	- Stop RNGs, stop_rngs(x,y), to clean up and stop the program;
	- Engine, engine(q1,q2), to enqueue data received from get_rng(socket)

RNGs:
Offers the following tasks:
	- A generic function, RNG(), to generate a random number and return it to the HSM;
	- Paul RSA simple algorithm, PaulRSASimple(), to generate a random number and return it to the HSM;
	- Parsing function, parseHourDayMonthYear() ----→ will be removed soon

dataContainment:
offers the following tasks:
	- Sql table definition, sqlTable(), to define the dB structure. Current version uses SQLite3;
	- Retrieve data from the queue, collectData(q1,q2), and process it;
	- Store beacons, insertBeaconinfo(x) into the database;
	 
queueTransit:
Allows two different processes, beaconEngine4 engine(q1,q2) and dataContainment colectData(q1,q2), to exchange data, i.e. to enqueue and dequeue.



