'''
Created on August 19, 2019
@author: Evariste2
'''

from yubihsm import YubiHsm
from yubihsm.defs import CAPABILITY, ALGORITHM
from yubihsm.objects import AsymmetricKey

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes       #for signing
from cryptography.hazmat.primitives.asymmetric import padding, ec, rsa   #for signing

from RNGs import RNGSources
from getpass import getpass
objectRNGs = RNGSources()

import logging
logging.basicConfig(filename='RNGLog.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
#logger=logging.getLogger(__name__)

'''
openSession function creates a session ID and returns it to the rngServer
This value, session ID, will be used to address the newly created session on the HSM.
The session ID will be used to authenticate the session or to establish the session.
'''
def openSession():
    try:
        #pwd = getpass('Enter password for authentication:')        #For later use: we may use password to establish the session.

        #*** Return a YubiHsm connected to the backend specified by the URL
        #*** In this case, the HSM is connected to a connector running on localhost using the default port.
        hsm = YubiHsm.connect('http://localhost:12345')
        #*** Create an authenticated session with the HSM
        session = hsm.create_session_derived(1, 'password')
        return session
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)

'''
authenticate function: authenticates secure session with a HSM
by using the given ID session to authenticate the session.
Upon authentication, an elliptic curve ECDSA or RSA PKCS#1v15 cryptography is used to create the key
for signing purpose. A random number, 512 bits, is also generated.
the generated key and random number are return for further pocessing.
'''
def authenticate(session):
    try:
        #asymkey = AsymmetricKey.generate(session, 0, 'Generate BP R1 Sign', 0xffff, CAPABILITY.SIGN_ECDSA, ALGORITHM.EC_BP256)
        #RSA
        keysize = 2048          #2048       https://thekernel.com/wp-content/uploads/2018/11/YubiHSM2-EN.pdf
        key = rsa.generate_private_key(public_exponent=0x10001, key_size=keysize, backend=default_backend())
        asymkey = AsymmetricKey.put(session, 0, 'RSA pkcs1v15', 0xffff, CAPABILITY.SIGN_PKCS, key)
        # PKCS1v15 does not offer 512 bit with the propose algorithm. A ticket has been addressed to Yubio developers team

        #pub = asymkey.get_public_key()
        randomHSM = session.get_pseudo_random(64)

        #data = os.urandom(16)
        hashtype = hashes.SHA512()
        #dataSigned = asymkey.sign_ecdsa(randomHSM, hashtype)     #Sign using ecdsa   resp = asymkey.sign_ecdsa(data, hashtype, length=0)
        #dataSigned = asymkey.sign_pkcs1v1_5(randomHSM, hashtype)           #Sign using pkcs1v1_5
        #pub.verify(resp, data, padding.PKCS1v15(), hashtype)        #verify using pkcs1v1_5

        return asymkey, randomHSM
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)

'''
ComplexSigning function is taking multiple messages to be hashed and signed. 
The hashed and signed are returned for further processing
'''
def ComplexSigning(message1, message2, messageHSM, paulRNG, priv_key):
    try:
        chosen_hash = hashes.SHA512()
        hasher = hashes.Hash(chosen_hash, default_backend())
        hasher.update(str(message1).encode('utf8'))
        hasher.update(str(message2).encode('utf8'))
        hasher.update(str(messageHSM).encode('utf8'))
        hasher.update(str(paulRNG).encode('utf8'))
        digest = hasher.finalize()

        #sig_ecda = priv_key.sign_ecdsa(digest, chosen_hash)      #sign using Elliptic Curve ecdsa     sig_ecda = priv_key.sign_ecdsa(digest, chosen_hash, length=0)
        sig_pkcs1 = priv_key.sign_pkcs1v1_5(digest, chosen_hash)            #sign using RSA pkcs1v1_5

        #return sig_ecda, digest
        return sig_pkcs1, digest
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)

'''
singleSigning function: receives a single message to be signed and returns it for further processing.
'''
def SingleSigning(message, priv_key):
    try:
        chosen_hash = hashes.SHA512()
        hasher = hashes.Hash(chosen_hash, default_backend())
        hasher.update(str(message).encode('utf8'))
        digest = hasher.finalize()
        sig_pkcs1 = priv_key.sign_pkcs1v1_5(digest, chosen_hash)            #sign using RSA pkcs1v1_5
        #sig_ecdsa = priv_key.sign_ecdsa(digest, chosen_hash)
        return sig_pkcs1
        #return sig_ecdsa
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)

'''
cleanUp function: deletes the generated key
'''
def cleanUp(priv_key):
    try:
        # Delete the key from the YubiHSM 2
        priv_key.delete()
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)


'''
main function do the following tasks:
    1. retrieve random numbers from different sources
    2. call for authentication given a session ID
    3. combine and sign retrieved random numbers
    4. sign individual random number
    5. return combinedMsgSigned and digest, and signed of different random sources.
'''
def main(session):
    try:
        #Retrieve RNGs from sources
        message1 =  objectRNGs.RNG()  #RNGOne()   Verify message authenticity
        message2 =  objectRNGs.RNG()                  #RNGTwo()  # Verify message authenticity
        paulRNG = objectRNGs.PaulRSASimple()

        #Authenticate to the open session
        priv_key, messageHSM = authenticate(session)
        combinedMsgSigned, digest = ComplexSigning(message1, message2, messageHSM, paulRNG, priv_key)    #Sign using the HSM

        #Signed RNGs with HSM
        signedMessage1 = SingleSigning(message1, priv_key)
        signedMessage2 = SingleSigning(message2, priv_key)
        signedPaulMsg = SingleSigning(paulRNG, priv_key)
        messageHSM = SingleSigning(messageHSM, priv_key)

        #Formatting and cleaning
        combinedMsgSigned = combinedMsgSigned.hex().upper().strip()
        digest = digest.hex().upper().strip()
        sourceRNG1 = signedMessage1.hex().upper().strip()
        sourceRNG2 = signedMessage2.hex().upper().strip()
        sourceHSM = messageHSM.hex().upper().strip()
        sourcePaul = signedPaulMsg.hex().upper().strip()

        #Delete key before returning data
        cleanUp(priv_key)

        return combinedMsgSigned, digest, sourceRNG1, sourceRNG2, sourceHSM, sourcePaul
        #return combinedMsgSigned, digest, sourceRNG1, sourceRNG2, sourceHSM, sourcePaul
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)

#if __name__ == '__main__':
    #main()
    #session = openSession()
    #main(session)

    #authenticate(session)
    #objectRSA = RSAEncryptionFunctions()
    #A=objectRSA.main()
    #print(A)
    #ciphertext=objectRSA.RSAEncryption(b"encrypted data")
    #objectRSA.RSADecryption(ciphertext)
    #message = b"encrypted data"
    #messageSigned = objectRSA.SimpleSigning(message)
    #objectRSA.SimpleVerification(messageSigned, message)
    #objectRSA.ComplexVerification()