from celery import shared_task
from .models import Session


@shared_task
def on_start_time(session_id):
    session = Session.objects.get(id=session_id)
    session.change_status_to(Session.Status.ONGOING)

@shared_task
def on_end_time(session_id):
    session = Session.objects.get(id=session_id)
    session.change_status_to(Session.Status.COMPLETED)

@shared_task
def on_start_register_time(session_id):
    session = Session.objects.get(id=session_id)
    session.change_status_to(Session.Status.UPCOMING)

@shared_task
def on_end_register_time(session_id):
    session = Session.objects.get(id=session_id)
    session.change_status_to(Session.Status.WAITING)
