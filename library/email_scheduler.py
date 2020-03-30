# pylint: disable=invalid-name, unnecessary-lambda
"""Email Scheduler"""
from __future__ import print_function
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

app = Flask(__name__)

cron = BackgroundScheduler()

def print_date_time():
    """Print Date Time"""
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))

cron.add_job(func=print_date_time, trigger="interval", minutes=1)
cron.start()

# Shut down the cron when exiting the app
atexit.register(lambda: cron.shutdown())


if __name__ == '__main__':
    app.run()
