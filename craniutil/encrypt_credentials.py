import unittest

import yaml
from unittest.mock import patch


def load(filename,password) -> dict:
    d = load_yaml(filename)
    assert 'keep-plain' in d
    x = d['keep-plain']
    if d['encrypted'] is not None:
        cipher = AESCipher(password)
        for key,enc in d['encrypted'].items():
            x[key] = cipher.decrypt(enc.encode())
    return x

def load_yaml(filename)->dict:
    with open(filename, 'r') as stream:
        return yaml.load(stream)


class TestEncrypt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cipher = AESCipher('password')
        enc_ftp_password = cls.cipher.encrypt('plain ftp password').decode()
        cls.d = {
            'encrypted':{
                'ftp-password' : enc_ftp_password
            },
            'keep-plain':{
                'ftp-host' : 'abc.com'
            },
            'encrypt-plain':{
                'cex-user-id' : 'plain cex'
            }
        }


    def test_load(self):
        with patch(__name__ + ".load_yaml",return_value=self.d):
            result = load('','password')
            assert result['ftp-password'] == 'plain ftp password', result
            assert result['ftp-host'] == 'abc.com', result

    def test_encrypt(self):
        e = encrypt_dict(self.d,'password')
        assert self.cipher.decrypt(e['encrypted']['cex-user-id']) == 'plain cex', e
        assert not e['encrypt-plain']



def write_yaml(filename,data):
    with open(filename, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)


def encrypt_file(infile,outfile, password)->None:
    d = load_yaml(infile)
    encrypt_dict(d, password)
    write_yaml(outfile, d)


def encrypt_dict(d, password):
    if d['encrypted'] is None:
        d['encrypted'] = {}
    e = d['encrypted']
    cipher = AESCipher(password)
    for key, value in d['encrypt-plain'].items():
        e[key] = cipher.encrypt(value).decode()
    d['encrypt-plain'] = {}
    return d


import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


class TestAESCipher(unittest.TestCase):
    def test_round_trip(self):
        instance = AESCipher('password')
        enc = instance.encrypt('plain text')
        dec = instance.decrypt(enc)
        assert dec=='plain text',dec