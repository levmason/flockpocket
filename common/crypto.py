import json
import zlib

# encoding
def encode (data, secure = False):
    # encode to json
    data = json.dumps(data)
    # encode to bytes
    data = data.encode()
    # compress
    data = zlib.compress(data)
    # encrypt
    if secure:
        data = cfg.crypto.encrypt(data)

    return data

def decode (data, secure = False):
    if data:
        # decrypt
        if secure:
            data = cfg.crypto.decrypt(data)
        # decompress
        data = zlib.decompress(data)
        # decode bytes
        data = data.decode()
        # decode json
        data = json.loads(data)

    return data
