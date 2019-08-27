'''
Created on August 19, 2019
@author: Evariste
'''

from yubihsm import YubiHsm
from yubihsm.defs import CAPABILITY, ALGORITHM
from yubihsm.objects import AsymmetricKey

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes       #for signing
from cryptography.hazmat.primitives.asymmetric import utils     #for hashing larger message
from cryptography.hazmat.primitives.asymmetric import padding, ec   #for signing
import base64
import os
from os import urandom
from random import randrange
from hashlib import sha256

from RNG1 import RNGOne
from RNG2 import RNGTwo

#Open session, authenticate, create asymmetric key and public key
#Generate a random number from the HSM
def authenticate():
    hsm = YubiHsm.connect('http://localhost:12345')
    session = hsm.create_session_derived(1, "password")
    asymkey = AsymmetricKey.generate(session, 0, 'Generate BP R1 Sign', 0xffff, CAPABILITY.SIGN_ECDSA,
                                     ALGORITHM.EC_BP512)
    pub = asymkey.get_public_key()
    data = session.get_pseudo_random(16)
    data = os.urandom(64)
    hashtype = hashes.SHA512()
    resp = asymkey.sign_ecdsa(data, hashtype, length=0)
    bits512 = int.from_bytes(resp, byteorder='little')
    return session, asymkey, pub, bits512

#Signing one message
def SimpleSigning(priv_key, message):
    return priv_key.sign(message,padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())

#Signing complex messages
def ComplexSigning(message1, message2, messageHSM, priv_key):
    chosen_hash = hashes.SHA512()
    hasher = hashes.Hash(chosen_hash, default_backend())
    hasher.update(str(message1).encode('utf8'))
    hasher.update(str(message2).encode('utf8'))
    hasher.update(str(messageHSM).encode('utf8'))
    digest = hasher.finalize()
    #print(digest)
    bits512 = int.from_bytes(digest, byteorder='little')
    #print(format(bits512, 'b'))
    sig_ecda = priv_key.sign_ecdsa(digest, chosen_hash, length=0)      #padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
    #sig_pkcs1 = priv_key.sign_pkcs1v1_5(digest, hashes.SHA512)
    return sig_ecda, bits512
    # return sig_pkcs1, bits512

#Verification
def SimpleVerification(pub_key, signature, message):
    try:
        pub_key.verify(signature, message,padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        authentication = True
    except (ValueError, TypeError):
        authentication = False
    return authentication

# Clean up and closing session
def cleanUp(session, priv_key):
    # Delete the key from the YubiHSM 2
    priv_key.delete()
    session.close()

#verification
def verifyHSMSource(pub, resp, data):
    try:
        pub.verify(resp, str(data).encode('utf8'), hashes.SHA256)
    except Exception as e:
        raise e
    return True

#Define a function main to process external RNGs, open session
def main():
    message1, pub_key1, signedMessage1 = RNGOne()  # Verify message authenticity
    authentication1 = SimpleVerification(pub_key1, signedMessage1, str(message1).encode('utf8'))
    message2, pub_key2, signedMessage2 = RNGTwo()  # Verify message authenticity
    authentication2 = SimpleVerification(pub_key2, signedMessage2, str(message2).encode('utf8'))
    if authentication1 and authentication2:
        session, priv_key, pub_key, messageHSM = authenticate()
        combinedMsgSigned, bits512 = ComplexSigning(message1, message2, messageHSM, priv_key)
        #print(combinedMsgSigned)
        #print(bits512)
        #print(len(str(bits512)))
        #print(messageHSM)
        #print(len(str(messageHSM)))
        #print(verifyHSMSource(pub_key, combinedMsgSigned, bits512))
        cleanUp(session, priv_key)
        return bits512

#if __name__ == '__main__':
    #main()
    #objectRSA = RSAEncryptionFunctions()
    #A=objectRSA.main()
    #print(A)
    #ciphertext=objectRSA.RSAEncryption(b"encrypted data")
    #objectRSA.RSADecryption(ciphertext)
    #message = b"encrypted data"
    #messageSigned = objectRSA.SimpleSigning(message)
    #objectRSA.SimpleVerification(messageSigned, message)
    #objectRSA.ComplexVerification()