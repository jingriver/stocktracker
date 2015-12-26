# testing a simple xor encryption/decryption
# tested with Python24      vegaseat    02oct2005

import StringIO
import operator

def cryptXOR(filename, pw):
    """
    cryptXOR(filename, pw) takes the file in filename and xor encrypts/decrypts it against the password pw,
    if the file extension is .txt indicating a normal text file, then an encrypted file with extension .txp
    will be written, if the file extension indicates an encrypted file .txp then a decrypted normal text
    file with extension .txt will be written
    """
    f = open(filename, "rb")  # binary required
    str2 = f.read()
    f.close()
    # create two streams in memory the size of the string str2
    # one stream to read from and the other to write the XOR crypted character to
    sr = StringIO.StringIO(str2)
    sw = StringIO.StringIO(str2)
    # make sure we start both streams at position zero (beginning)
    sr.seek(0)
    sw.seek(0)
    n = 0
    #str3 = ""  # test
    for k in range(len(str2)):
        # loop through password start to end and repeat
        if n >= len(pw) - 1:
            n = 0
        p = ord(pw[n])
        n += 1
        
        # read one character from stream sr
        c = sr.read(1)
        b = ord(c)
        # xor byte with password byte
        t = operator.xor(b, p)
        z = chr(t)
        # advance position to k in stream sw then write one character
        sw.seek(k)
        sw.write(z)
        #str3 += z  # test
    # reset stream sw to beginning
    sw.seek(0)
    # if filename was a normal text file, stream sw now contains the encrypted text
    # and is written (binary required) to a file ending with .txp
    if filename.endswith('.txt'):
        outfile = filename[:-4] + '.txp'
        f = open(outfile, "wb")
        f.write(sw.read())
        f.close()
        print "File %s written!" % outfile
    # if filename was encrypted text, stream sw now contains normal text
    # and is written to a file ending with .txt
    elif filename.endswith('.txp'):
        outfile = filename[:-4] + '.txt'
        f = open(outfile, "w")
        f.write(sw.read())
        f.close()
        print "File %s written!" % outfile
        #print str3  # test
    else:
        print "File %s does not have proper extension!" % filename
    
    # clean up
    sr.close()
    sw.close()
    

        
# allows cryptXOR() to be used as a module
if __name__ == '__main__':

    str1 = \
        '''A list of quotes from Grade School Essays on the History of Classical Music:
        "J.S. Bach died from 1750 to the present"
        "Agnus Dei was a woman composer famous for her church music."
        "Refrain means don't do it.  A refrain in music is the part you better not try  to sing."
        "Handel was half German, half Italian, and half English.  He was rather large."
        "Henry Purcell is a well-known composer few people have ever heard of."
        "An opera is a song of bigly size."
        "A harp is a nude piano."
        "A virtuoso is a musician with real high morals."
        "Music sung by two people at the same time is called a duel."
        "I know what a sextet is but I'd rather not say."
        "Most authorities agree that music of antiquity was written long ago."
        "My favorite composer is opus."
        "Probably the most marvelous fugue was between the Hatfields and the McCoys."
        "My very best liked piece is the bronze lullaby." '''
    
    # save the string as a normal text file so we have it
    fout = open("Music101.txt", "w")
    fout.write(str1)
    fout.close()
    
    # let's use a fixed password for testing
    password = "nixon"
    
    # encrypt the text file to "Music101.txp" (check with an editor, shows a mess)
    cryptXOR("Music101.txt", password)
    
    # decrypt the text file back to "Music101.txt" (check with an editor, normal text again)
    cryptXOR("Music101.txp", password)