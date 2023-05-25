#!/usr/bin/python3

import requests

URL = 'http://127.0.0.1:8008/upload'
files = [
    ('file', ('DATA_Files (1).zip', open('DATA_Files (1).zip', 'rb'))),
]
response = requests.post(URL, files=files)
print(response.text)