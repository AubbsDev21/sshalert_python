#!/usr/bin/env python3

import logging
import os, time
import subprocess, select 

try: 
    import vonage
except:
    print("please pip install reqeuried libary")

##Init the logging
log = logging.getLogger('sshalert')
## Setting the verbose log level
log.setLevel(logging.INFO)


try: 
    soucre_number = os.getenv("SOURCE_PHONE_NUMBER")
    print(soucre_number)
    target_number = os.getenv("TARGET_PHONE_NUMBER")
    print(target_number)
    nexmo_key = os.getenv("NEXMO_KEY")
    print(nexmo_key)
    nexmo_secret = os.getenv("NEXMO_SECRET")
    print(nexmo_secret)

except:
    logging.critical("ERORR: Please export environments varaibles")
    exit(1)

## Init vonage
client = vonage.Client(key=nexmo_key, secret=nexmo_secret)
sms = vonage.Sms(client)



def readlogs(log):
    cmd = subprocess.Popen(["tail","-F","-n", "0", log], encoding="utf8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p = select.poll()
    p.register(cmd.stdout)

    while True:
        if p.poll(1):
            process_logfile(cmd.stdout.readline())

        time.sleep(1)


def process_logfile(logline):
    if all(x in logline for x in ["ssh", "Accepted"]):
            send_text(logline)
            return

def send_text(line):
    responseData = sms.send_message({
        "from" : soucre_number,
        "to" : target_number,
        "text" : line,
        })
    if responseData["messages"][0]["status"] == "0":
        logging.info("message was sent")
    else: 
        logging.error(f"Message failed with error: {responseData['messages'][0]['error-text']}")




if __name__ == "__main__":
    readlogs("/var/log/auth.log")
