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

#from RNG1 import RNGOne
#from RNG2 import RNGTwo
from RNGs import RNGSources
from getpass import getpass
objectRNGs = RNGSources()

#Open session, authenticate, asymmetric key and public key
#Generate a random number from the HSM
def openSession():
    #pwd = getpass('Enter password for authentication:')
    hsm = YubiHsm.connect('http://localhost:12345')
    session = hsm.create_session_derived(1, 'password')
    return session

def authenticate(session):
    #Elliptic curve crypto api type
    #asymkey = AsymmetricKey.generate(session, 0, 'Generate BP R1 Sign', 0xffff, CAPABILITY.SIGN_ECDSA,
                                     #ALGORITHM.EC_BP512)
    #RSA
    keysize = 2048
    key = rsa.generate_private_key(public_exponent=0x10001, key_size=keysize, backend=default_backend())
    asymkey = AsymmetricKey.put(session, 0, 'RSA pkcs1v15', 0xffff, CAPABILITY.SIGN_PKCS, key)
    #End RSA
    #print(asymkey)

    pub = asymkey.get_public_key()
    data = session.get_pseudo_random(64)
    #data = os.urandom(16)
    hashtype = hashes.SHA512()
    #resp = asymkey.sign_ecdsa(data, hashtype, length=0)     #Sign using ecdsa
    resp = asymkey.sign_pkcs1v1_5(data, hashtype)           #Sign using pkcs1v1_5
    bits512 = int.from_bytes(resp, byteorder='little')
    #print(resp)
    #pub.verify(resp, data, ec.ECDSA(hashtype))                 #verify using ec.ECDSA
    pub.verify(resp, data, padding.PKCS1v15(), hashtype)        #verify using pkcs1v1_5
    #asymkey.delete()
    #return session, asymkey, pub, bits512
    return asymkey, pub, bits512

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
    #bits512 = int.from_bytes(digest, byteorder='little')
    #print(format(bits512, 'b'))

    #sig_ecda = priv_key.sign_ecdsa(digest, chosen_hash, length=0)      #sign using Elliptic Curve ecdsa
    sig_pkcs1 = priv_key.sign_pkcs1v1_5(digest, chosen_hash)            #sign using RSA pkcs1v1_5

    #return sig_ecda, digest
    return sig_pkcs1, digest

#Verification
def SimpleVerification(pub_key, signature, message):
    try:
        pub_key.verify(signature, message,padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        authentication = True
    except (ValueError, TypeError):
        authentication = False
    return authentication

# Clean up and closing session
def cleanUp(priv_key):
    # Delete the key from the YubiHSM 2
    priv_key.delete()

#Define a function main to process external RNGs, open session
def main(session):
    message1, pub_key1, signedMessage1 =  objectRNGs.RNG()  #RNGOne()   Verify message authenticity
    authentication1 = SimpleVerification(pub_key1, signedMessage1, str(message1).encode('utf8'))
    message2, pub_key2, signedMessage2 =  objectRNGs.RNG()                  #RNGTwo()  # Verify message authenticity
    authentication2 = SimpleVerification(pub_key2, signedMessage2, str(message2).encode('utf8'))
    if authentication1 and authentication2:
        priv_key, pub_key, messageHSM = authenticate(session)
        combinedMsgSigned, digest = ComplexSigning(message1, message2, messageHSM, priv_key)
        cleanUp(priv_key)
        #print(int.from_bytes(digest, byteorder='big'))
        return digest, combinedMsgSigned, pub_key

if __name__ == '__main__':
    #main()
    session = openSession()
    authenticate(session)
    #objectRSA = RSAEncryptionFunctions()
    #A=objectRSA.main()
    #print(A)
    #ciphertext=objectRSA.RSAEncryption(b"encrypted data")
    #objectRSA.RSADecryption(ciphertext)
    #message = b"encrypted data"
    #messageSigned = objectRSA.SimpleSigning(message)
    #objectRSA.SimpleVerification(messageSigned, message)
    #objectRSA.ComplexVerification()