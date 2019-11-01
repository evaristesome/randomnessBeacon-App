'''
Generate a random number, encrypt, and sign
'''
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes       #for signing
from cryptography.hazmat.primitives.asymmetric import utils     #for hashing larger message
from cryptography.hazmat.primitives.asymmetric import padding   #for signing
import base64
import os
from os import urandom
from random import randrange
from hashlib import sha256

class RNGSources:

    # RSA Encryption
    def RSAEncryption(self, public_key, message):
        ciphertext = public_key.encrypt(message, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                                   algorithm=hashes.SHA256(), label=None))
        print(base64.b16encode((ciphertext)))
        return ciphertext

    # Signing message
    def SimpleSigning(self, private_key, message):
        return private_key.sign(message,
                                     padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                                     hashes.SHA256())

    # Generate random number
    def Random512(self):
        var = randrange(0, 2 ** 512)  # Use this section for HSM
        random_512_integer = int.from_bytes(urandom(64), byteorder="little")  # provides 512 bit in integer
        random_512_bit = format(random_512_integer, "b")
        return var

    def RNG(self):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        public_key = private_key.public_key()
        randomNumber = self.Random512()
        signedMessage = self.SimpleSigning(private_key, str(randomNumber).encode('utf8'))
        return randomNumber, public_key, signedMessage

if __name__ == '__main__':
    objectRNG = RNGSources()
