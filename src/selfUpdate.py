import urllib.request
import sys
import os

def update():
    print("Downloading...")
    with urllib.request.urlopen("https://www.gkbrk.com/ittnet") as f:
        with open(os.path.dirname(__file__), "wb+") as f1:
            f1.write(f.read())
    print("execl", [sys.executable] + sys.argv)
    os.execl(sys.argv[0], *sys.argv)
