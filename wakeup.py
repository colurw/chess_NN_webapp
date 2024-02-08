""" When first started, the Chess_nn Gunicorn server listens for a HTTP request
    before loading the ML models and associated libraries. This causes a significant
    delay to the first user of the day.  Wakeup.py prevents this."""

from pythonping import ping
import time

target = 'http://www.ec2-18-169-205-217.eu-west-2.compute.amazonaws.com/play'

while True:
    print('pinging server now')
    try:
        ping(target)
        time.sleep(300)
    except:
        time.sleep(300)
