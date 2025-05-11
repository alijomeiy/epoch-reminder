from celery import shared_task
from .models import Session

@shared_task
def on_start_time(session_id):
    session = Session.objects.get(id=session_id)
    print(f"📢 [START] Session started: {session}")

@shared_task
def on_end_time(session_id):
    session = Session.objects.get(id=session_id)
    print(f"🛑 [END] Session ended: {session}")

@shared_task
def on_start_register_time(session_id):
    session = Session.objects.get(id=session_id)
    print(f"📝 [REGISTER OPEN] Registration opened: {session}")

@shared_task
def on_end_register_time(session_id):
    session = Session.objects.get(id=session_id)
    print(f"🔒 [REGISTER CLOSED] Registration closed: {session}")
