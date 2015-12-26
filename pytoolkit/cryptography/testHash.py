#Hash functions take arbitrary strings as input, and produce an output of fixed size 
#that is dependent on the input; it should never be possible to derive the input data 
#given only the hash function's output. 
#For a hash function to be cryptographically secure, it must be very difficult to find 
#two messages with the same hash value, or to find a message with a given hash value.
#Examples of cryptographically secure hash functions include MD2, MD5, SHA, and HAVAL. 

#All the MDn algorithms produce 128-bit hashes; SHA produces a larger 160-bit hash
from Crypto.Hash import MD5
m = MD5.new()
m.update('abc')
print m.digest()
#'\x90\x01P\x98<\xd2O\xb0\xd6\x96?}(\xe1\x7fr'
print m.hexdigest()
#'900150983cd24fb0d6963f7d28e17f72'

