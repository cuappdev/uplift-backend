import hashlib

def generate_id(data):
  return hashlib.sha1(data.encode('utf-8')).hexdigest()
