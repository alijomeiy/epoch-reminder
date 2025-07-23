import random 
import requests
from celery import shared_task
from participant.models import SessionParticipant
from user.models import MessengerUser
from .models import Session


def notify_users(user_ids):
    print(f"Notification sent to {user_ids}")
    url = "http://192.168.21.88:9000/notify-new-session/"
    data = {
        "user_ids": user_ids,
    }
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

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
    users =  list(MessengerUser.objects.values_list('messenger_id', flat=True))
    notify_users(users)


@shared_task
def on_end_register_time(session_id):
    current_session = Session.objects.get(id=session_id)
    current_session.change_status_to(Session.Status.WAITING)
    current_participants = SessionParticipant.objects.filter(session=current_session)
    previous_session = current_session.get_previous_session()
    
    available_hezb = set(range(1, 121))
    
    if previous_session:
        previous_participants = SessionParticipant.objects.filter(session=previous_session)
        used_hezb = set(participant.hezb for participant in previous_participants if participant.hezb)
        available_hezb -= used_hezb
    
    for participant in current_participants:
        # Check if the user was in the previous session
        if previous_session:
            previous_participant = SessionParticipant.objects.filter(
                session=previous_session, 
                user=participant.user
            ).first()
            
            if previous_participant and previous_participant.hezb:
                # If the user was in the previous session, reuse their previous hezb
                participant.hezb = previous_participant.hezb
            else:
                # If the user wasn't in the previous session, assign a random hezb
                if available_hezb:
                    participant.hezb = random.choice(list(available_hezb))
                    available_hezb.remove(participant.hezb)
        else:
            # If no previous session exists, assign a random hezb
            if available_hezb:
                participant.hezb = random.choice(list(available_hezb))
                available_hezb.remove(participant.hezb)
        participant.save()
    