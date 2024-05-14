""" When first started, the Chess_nn Gunicorn server listens for a HTTP request
    before loading the ML models and associated libraries. This causes a significant
    delay to the first user of the day.  Wakeup.py prevents this."""

import urllib3
import time

target = "http://ec2-18-169-205-217.eu-west-2.compute.amazonaws.com/play/"

time.sleep(180)
urllib3.request("GET", target)