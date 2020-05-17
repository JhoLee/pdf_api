import os
import string
import random

# REF. https://wayhome25.github.io/django/2017/07/11/django-settings-secret-key/
chars = ''.join([string.ascii_letters, string.digits, string.punctuation]) \
    .replace('\'', '') \
    .replace('"', '') \
    .replace('\\', '')

SECRET_KEY = ''.join([random.SystemRandom().choice(chars) for i in range(50)])

with open('secret_key.txt', 'w') as f:
    f.write(SECRET_KEY)
