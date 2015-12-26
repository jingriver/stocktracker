import urllib2_file
import urllib2

data = {'name': 'value',
        'file':  open('/error.log')
       }
#data2 = [ 'the bus', 'felt near Coroico',
#          'userfile', open('/home/foo/bar.png')
#        ]
urllib2.urlopen('http://localhost/fileUpload.html', data)
