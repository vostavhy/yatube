from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from working_scripts import model_manipulations


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(model_manipulations.post_create_instance, 'interval', minutes=1)
    scheduler.start()
