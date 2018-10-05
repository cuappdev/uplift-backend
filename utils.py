import hashlib
import os

def generate_id(data):
  return hashlib.sha1(data.encode('utf-8')).hexdigest()
