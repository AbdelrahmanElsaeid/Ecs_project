# import logging

# from celery.signals import task_failure
# from celery.task import periodic_task
# from celery.schedules import crontab

# from django.core.management import call_command

# logger = logging.getLogger('task')

# def process_failure_signal(exception, traceback, sender, task_id, signal, args, kwargs, einfo, **kw):
#     exc_info = (type(exception), exception, traceback)
#     logger.error(
#         str(exception),
#         exc_info=exc_info,
#         extra={
#             'data': {
#                 'task_id': task_id,
#                 'sender': sender,
#                 'args': args,
#                 'kwargs': kwargs,
#             }
#         }
#     )
# task_failure.connect(process_failure_signal)

# # run once per day at 04:05
# @periodic_task(run_every=crontab(hour=4, minute=5))
# def clearsessions():
#     call_command('clearsessions')
import logging
from celery.signals import task_failure
from celery import shared_task
from celery.schedules import crontab
from django.core.management import call_command

logger = logging.getLogger('task')

import logging
import weakref
from celery.signals import task_failure

logger = logging.getLogger('task')

def process_failure_signal(sender, task_id, exception, args, kwargs, traceback, einfo, **kw):
    # Create weak references to objects that support weak references
    weak_sender = weakref.ref(sender) if hasattr(sender, '__weakref__') else sender
    weak_args = weakref.ref(args) if hasattr(args, '__weakref__') else args
    weak_kwargs = weakref.ref(kwargs) if hasattr(kwargs, '__weakref__') else kwargs

    exc_info = (type(exception), exception, traceback)
    logger.error(
        str(exception),
        exc_info=exc_info,
        extra={
            'data': {
                'task_id': task_id,
                'sender': weak_sender,
                'args': weak_args,
                'kwargs': weak_kwargs,
            }
        }
    )

task_failure.connect(process_failure_signal)


@shared_task
def clearsessions():
    call_command('clearsessions')
