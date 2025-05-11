from celery import shared_task
from .models import Session


@shared_task
def on_start_time(session_id):
    session = Session.objects.get(id=session_id)
    session.status = Session.Status.ONGOING
    session.save()

@shared_task
def on_end_time(session_id):
    session = Session.objects.get(id=session_id)
    session.status = Session.Status.COMPLETED
    session.save()

@shared_task
def on_start_register_time(session_id):
    session = Session.objects.get(id=session_id)
    session.status = Session.Status.UPCOMING
    session.save()

@shared_task
def on_end_register_time(session_id):
    session = Session.objects.get(id=session_id)
    session.status = Session.Status.WAITING
    session.save()
