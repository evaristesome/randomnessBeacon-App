'''
Generate a random number, encrypt, and sign
'''
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes  # for signing
from cryptography.hazmat.primitives.asymmetric import utils  # for hashing larger message
from cryptography.hazmat.primitives.asymmetric import padding  # for signing
import base64
import os
from os import urandom
from random import randrange
from hashlib import sha256
import datetime

from sympy import *
import os
import binascii
import time
from multiprocessing import Process, Queue
from multiprocessing import Process, Queue

import logging

logging.basicConfig(filename='RNGLog.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')


# logger=logging.getLogger(__name__)

'''
This program generate random numbers using different algorithms and return them to the HSM for signing.
Currently, we hve a RNG algorithm proposed by Paul Beal, and a generic function to generate random number. 
This generic function, RNG, is just for testing purpose and will be removed later.
'''
class RNGSources:

    #RNG function to generate generic random number
    def RNG(self):
        try:
            randomNumber = randrange(0, 2 ** 512)       #self.Random512()
            return randomNumber      #return randomNumber, public_key, signedMessage
        except Exception as e:
            logging.error("Exception occured: ", exc_info=True)

    # Convert to hour, day, month, year
    #def parseHourDayMonthYear(self):
        #try:
            #date_time_str = self.utcTime()
            # date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
            #hour = date_time_str.hour
            #day = date_time_str.day
            #month = date_time_str.month
            #year = date_time_str.year
            #return date_time_str, hour, day, month, year
        #except Exception as e:
            #logging.error("Exception occured: ", exc_info=True)

    '''
    This algorithm has been designed by Paul Beale. There are three versions. The simplest version is currently 
    used for testing purpose. I am still looking for ways to enqueue its outputs and make it acessible to the HSM
    '''
    # calculate initial parameters p, q, lambda, etc
    def PaulRSASimple(self):
        e = 3
        nbits = 2048
        nbytes = int(nbits / 8)
        nbitsprime = int(nbits / 2)
        nbytesprime = int(nbitsprime / 8)

        # choose 2048 bit composite n=p*q
        # choose two 1024 bit primes p and q without any special properties or checks other than
        # the exponent e must be coprime to phi(n) by requiring gcd(e,p-1)=gcd(e,q-1)=1

        # print ("initializing primes p and q")

        p = int(binascii.hexlify(os.urandom(nbytesprime)), 16)
        twonprimebitsminus1 = pow(2, nbitsprime - 1)
        while p < twonprimebitsminus1:
            p = 2 * p
        p = nextprime(p)
        while igcd(e, p - 1) != 1:
            p = nextprime(p)
        q = int(binascii.hexlify(os.urandom(nbytesprime)), 16)
        while q < twonprimebitsminus1:
            q = 2 * q
        q = nextprime(q)
        while igcd(e, q - 1) != 1:
            q = nextprime(q)
        n = p * q
        lam = (p - 1) * (q - 1) // igcd(p - 1, q - 1)
        x0 = int(binascii.hexlify(os.urandom(nbytes - 1)), 16)
        # print ("p=",hex(p))
        # print ("q=",hex(q))
        # print ("n=",hex(n))
        # print ("e=",e)
        # print ("lam=",hex(lam))
        # print ("x0=",hex(x0))

        M = 2 ** 20
        N = 512
        # print ("setup initial pseudorandom parameters")
        t = int(time.time())
        t0 = t
        xt0 = pow(x0, pow(e, M * t0, lam), n)
        zt0 = 0
        twok = 1
        x = xt0
        for k in range(0, N):
            zt0 = zt0 + twok * (x % 2)
            x = pow(x, e, n)
            twok = 2 * twok
        ht0 = zt0 % 4294967296

        t1 = t0 + 1
        xt1 = pow(x0, pow(e, M * t1, lam), n)
        zt1 = 0
        twok = 1
        x = xt1
        for k in range(0, N):
            zt1 = zt1 + twok * (x % 2)
            x = pow(x, e, n)
            twok = 2 * twok
        ht1 = zt1 % 4294967296

        t2 = t1 + 1
        xt2 = pow(x0, pow(e, M * t2, lam), n)
        zt2 = 0
        twok = 1
        x = xt2
        for k in range(0, N):
            zt2 = zt2 + twok * (x % 2)
            x = pow(x, e, n)
            twok = 2 * twok
        ht2 = zt2 % 4294967296

        # print ("t0=",t0, time.asctime(time.gmtime(t0)))
        # print ("xt0=",hex(xt0))
        # print ("zt0=",hex(zt0))
        # print ("ht0=",hex(ht0))

        # print (" ")
        # print ("t1=",t1, time.asctime(time.gmtime(t1)))
        # print ("xt1=",hex(xt1))
        # print ("zt1=",hex(zt1))
        # print ("ht1=",hex(ht1))

        # print (" ")
        # print ("t2=",t2,time.asctime(time.gmtime(t2)))
        # print ("xt2=",hex(xt2))
        # print ("zt2=",hex(zt2))
        # print ("ht2=",hex(ht2))
        # print (" ")

        # post t0
        # print ("t0=",t0, time.asctime(time.gmtime(t0)))
        # print ("zt0=",hex(zt0))
        # print ("ht1=",hex(ht1))
        starttime = t0

        tlastpost = t0

        # reset
        t0 = t1
        xt0 = xt1
        zt0 = zt1
        ht0 = ht1

        t1 = t2
        xt1 = xt2
        zt1 = zt2
        ht1 = ht2

        t2 = t1 + 1
        xt2 = pow(x0, pow(e, M * t2, lam), n)
        zt2 = 0
        twok = 1
        x = xt2
        for k in range(0, N):
            zt2 = zt2 + twok * (x % 2)
            x = pow(x, e, n)
            twok = 2 * twok
        ht2 = zt2 % 4294967296

        #print("start broadcasting")
        count = 0
        t = time.time()
        while True:
            t = int(time.time())
            if (t > tlastpost):

                if (t0 % 3600 == 0):
                    # print (" ")
                    # print ("parameters used during previous hour were:")
                    # print ("p=",hex(plast))
                    # print ("q=",hex(qlast))
                    # print ("n=",hex(nlast))
                    # print ("e=",e)
                    # print ("lam=",hex(lamlast))
                    # print ("x0=",hex(x0last))
                    pass

                count = count + 1
                # post t0
                # print (" ")
                # print ("timestamp, UTC time, zt, and lowest four bytes of next zt")
                # print (t0, "  ", time.strftime("%H:%M:%S %m/%d/%Y UTC", time.gmtime(t0)))
                # print(type(zt0))
                paulRNG = (zt0)      #str(zt0).encode('utf8')
                return paulRNG
                # print(str(zt0).encode('utf8'))
                # print (hex(zt0))
                # print (hex(ht1))

                tlastpost = t0

                t0 = t1
                xt0 = xt1
                zt0 = zt1
                ht0 = ht1

                t1 = t2
                xt1 = xt2
                zt1 = zt2
                ht1 = ht2

                t2 = t1 + 1
                xt2 = pow(x0, pow(e, M * t2, lam), n)
                zt2 = 0
                twok = 1
                x = xt2
                for k in range(0, N):
                    zt2 = zt2 + twok * (x & 1)
                    x = pow(x, e, n)
                    twok = twok << 1
                ht2 = zt2 % 4294967296

                if (t0 % 3600 == 3558):
                    # print ("resetting primes before top of hour")
                    plast = p
                    qlast = q
                    nlast = n
                    lamlast = lam
                    x0last = x0
                    clock0 = time.clock()
                    p = int(binascii.hexlify(os.urandom(nbytesprime)), 16)
                    while p < twonprimebitsminus1:
                        p = 2 * p
                    p = nextprime(p)
                    while igcd(e, p - 1) != 1:
                        p = nextprime(p)
                    q = int(binascii.hexlify(os.urandom(nbytesprime)), 16)
                    while q < twonprimebitsminus1:
                        q = 2 * q
                    q = nextprime(q)
                    while igcd(e, q - 1) != 1:
                        q = nextprime(q)
                    n = p * q
                    lam = (p - 1) * (q - 1) // igcd(p - 1, q - 1)  # // instead of /
                    x0 = int(binascii.hexlify(os.urandom(nbytes - 1)), 16)
                    clock1 = time.clock()
                # print ("time to reset primes =",clock1-clock0)

#obj = RNGSources()
#print(obj.Random512())
#print(obj.PaulRSASimple())