import hashlib
import os

def generate_id():
  return hashlib.sha1(os.urandom(64)).hexdigest()
