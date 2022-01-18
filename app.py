import requests
import subprocess
import time
import schedule
import signal
import sys
import psutil
from os import listdir
from os.path import isfile, join, getmtime
from pathlib import Path
#tcpdump -i lo -s0 not port 22 -w -

interval = 10

p1 = subprocess.Popen("find ./caps -maxdepth 1 -type f -exec rm -fv {} \\;", shell=True)
p1.communicate()
p = subprocess.Popen(("tcpdump -i lo -s0 not port 22 -w caps/trace-%H.%M.%S.pcap -G "+str(interval)).split(), stdout=subprocess.PIPE)


#print(dir(p.stdout.raw))
#

uploaded_files = []


def signal_handler(sig, frame):
    print('Stop process!')
    p.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def clean():
    print("clean")
    subprocess.Popen("find ./caps -maxdepth 1 -mmin +2 -type f -exec rm -fv {} \\;", shell=True)


def upload(uploaded_files,interval):
    onlyfiles = [f for f in listdir("./caps") if isfile(join("./caps", f)) and not f in uploaded_files and is_good(join("./caps", f),interval) ]
    uploaded_files.extend(onlyfiles)
    for file in onlyfiles:
        with open("./caps/"+file,"rb") as f:
            data = f.read()
        r = requests.post("http://localhost:8080/upload/"+file, data=data)
        print("uploaded")
     #   p2 = subprocess.Popen("/home/jonas/ctf/tools/flower/services/importer.py "+"./caps/"+file, shell=True)
     #   out = p2.communicate()
      #  print(out)



def is_good(file_path,interval):
    return time.time()-getmtime(file_path)>interval*2

schedule.every(30).seconds.do(clean)
schedule.every(interval).seconds.do(upload, uploaded_files=uploaded_files, interval=interval)

while 1:
    schedule.run_pending()
    time.sleep(1)



