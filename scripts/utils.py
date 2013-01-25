import os

def mkdir_p(path):
    try:
        os.makedirs(path)
    except:
        pass