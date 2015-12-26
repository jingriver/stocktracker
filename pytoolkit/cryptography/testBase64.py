import base64

encoded = base64.b64encode("data to be encoded")
print encoded
data = base64.b64decode(encoded)
print data
