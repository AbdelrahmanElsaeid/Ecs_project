import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('proj')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'expire-login-history': {
        'task': 'project.tasks.expire_login_history',
        'schedule': crontab(day_of_month=1, hour=0, minute=20),
    },
    'expire-invitations': {
        'task': 'project.tasks.expire_invitations',
        'schedule': crontab(hour=4, minute=9),
    },
    'cull-cache-dir': {
        'task': 'project.tasks.cull_cache_dir',
        'schedule': crontab(hour=3, minute=28),
    },
    'send-download-warnings': {
        'task': 'project.tasks.send_download_warnings',
        'schedule': crontab(day_of_week=0, hour=23, minute=59),
    },
    'expire-download-history': {
        'task': 'project.tasks.expire_download_history',
        'schedule': crontab(day_of_month=1, hour=0, minute=15),
    },
    'send-reminder-messages': {
        'task': 'project.tasks.send_reminder_messages',
        'schedule': crontab(hour=9, minute=0),
    },
    'expire-votes': {
        'task': 'project.tasks.expire_votes',
        'schedule': crontab(hour=3, minute=58),
    },
    'clear-sessions': {
        'task': 'project.tasks.clearsessions',
        'schedule': crontab(hour=4, minute=5),
    },
   
}

app.autodiscover_tasks()





app.conf.beat_schedule = {
    'forward-messages': {
        'task': 'project.tasks.forward_messages',  
        'schedule': timedelta(days=1, hours=0, minutes=20), 
    },
}





# import os
# from celery import Celery

# # set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# # create the Celery application
# app = Celery('project')

# # Using a string here means the worker doesn't have to serialize
# # the configuration object to child processes.
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Load task modules from all registered Django app configs.
# app.autodiscover_tasks()
