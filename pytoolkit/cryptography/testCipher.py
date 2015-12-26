#Encryption algorithms transform their input data, or plaintext, in some way that 
#is dependent on a variable key, producing ciphertext. This transformation can 
#easily be reversed, if (and, hopefully, only if) one knows the key. 
#The key can be varied by the user or application and chosen from some very large space of possible keys. 

#Private key ciphers: the same key is used for both encryption and decryption, so all correspondents must know it. 
#Block ciphers take multibyte inputs of a fixed size (frequently 8 or 16 bytes long) and encrypt them
#Electronic Code Book (ECB mode)
#Cipher Block Chaining (CBC mode)
#Cipher FeedBack (CFB mode)
#PGP mode
#    Cipher  Key Size/Block Size  
#    ARC2 Variable/8 bytes 
#    Blowfish Variable/8 bytes 
#    CAST Variable/8 bytes 
#    DES 8 bytes/8 bytes 
#    DES3 (Triple DES) 16 bytes/8 bytes 
#    IDEA 16 bytes/8 bytes 
#    RC5 Variable/8 bytes 

#Stream ciphers encrypt data bit-by-bit; practically, stream ciphers work on a character-by-character basis. 
#Stream ciphers use exactly the same interface as block ciphers, with a block length that will always be 1; 
#this is how block and stream ciphers can be distinguished. The only feedback mode available for stream ciphers is ECB mode.
#    Cipher Key Size 
#    ARC4(Alleged RC4) Variable 

#An all-or-nothing package transformation is one in which some text is transformed into message blocks, such that all blocks must be obtained before the reverse transformation can be applied. Thus, if any blocks are corrupted or lost, the original message cannot be reproduced. An all-or-nothing package transformation is not encryption, although a block cipher algorithm is used. The encryption key is randomly generated and is extractable from the message blocks.
#Winnowing and chaffing is a technique for enhancing privacy without requiring strong encryption. In short, the technique takes a set of authenticated message blocks (the wheat) and adds a number of chaff blocks which have randomly chosen data and MAC(message authentication code) fields. This means that to an adversary, the chaff blocks look as valid as the wheat blocks, and so the authentication would have to be performed on every block. By tailoring the number of chaff blocks added to the message, the sender can make breaking the message computationally infeasible. There are many other interesting properties of the winnow/chaff technique.  
from Crypto.Cipher import DES
print DES.block_size, DES.key_size
obj=DES.new('abcdefgh', DES.MODE_ECB)
plain="Guido van Rossum is a space alien."
ciph=obj.encrypt(plain+'XXXXXX')
print ciph
print obj.decrypt(ciph)

#Public key cryptography
#In a public key system, there are two different keys: one for encryption and one for decryption. The encryption key can be made public by listing it in a directory or mailing it to your correspondent, while you keep the decryption key secret. Your correspondent then sends you data encrypted with your public key, and you use the private key to decrypt it.
#The currently available public key algorithms are listed in the following table: 
#    Algorithm  Capabilities  
#    RSA Encryption, authentication/signatures 
#    ElGamal Encryption, authentication/signatures 
#    DSA Authentication/signatures 
#    qNEW Authentication/signatures 

#An example of using the RSA module to sign a message:
  
from Crypto.Hash import MD5
from Crypto.PublicKey import RSA
from Crypto.Util.randpool import RandomPool
RSAkey=RSA.generate(384, RandomPool().get_bytes)   # This will take a while...
hash=MD5.new(plain).digest()
signature=RSAkey.sign(hash, "")
print signature   # Print what an RSA sig looks like--you don't really care.
RSAkey.verify(hash, signature)     # This sig will check out
 