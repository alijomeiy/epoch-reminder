import random 
import requests
import jdatetime
from datetime import datetime
from celery import shared_task
from participant.models import SessionParticipant
from user.models import MessengerUser
from .models import Session


def notify_users(data, action):
    url = f"http://192.168.21.88:9000/{action}/"
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

def generate_jalali_date_map(gregorian_date: datetime, begin_hezb: int, days: int = 120):
    start_date_jalali = jdatetime.date.fromgregorian(date=gregorian_date)
    hezb_days = {}
    for i in range(days):
        current_date = start_date_jalali + jdatetime.timedelta(days=i)
        date_str = current_date.strftime('%Y/%m/%d')
        hezb_days[date_str] = ((begin_hezb - 1 + i) % 120) + 1
    return hezb_days

@shared_task
def on_start_time(session_id):
    session = Session.objects.get(id=session_id)
    session.change_status_to(Session.Status.ONGOING)
    hezb_days = generate_jalali_date_map(session.start_time, 6)
    session_participants = SessionParticipant.objects.filter(session=session)
    for session_participant in session_participants:
        data = {
            "telegram_id": session_participant.user.created_by.messenger_id,
            "start_time": jdatetime.datetime.fromgregorian(datetime=session.start_time).strftime('%Y/%m/%d'),
            "end_time": jdatetime.datetime.fromgregorian(datetime=session.end_time).strftime('%Y/%m/%d'),
            "username": session_participant.user.name,
            "hezb_days": generate_jalali_date_map(session.start_time, session_participant.hezb)
        }
        notify_users(data, "send-info")

@shared_task
def on_end_time(session_id):
    session = Session.objects.get(id=session_id)
    session.change_status_to(Session.Status.COMPLETED)

@shared_task
def on_start_register_time(session_id):
    session = Session.objects.get(id=session_id)
    session.change_status_to(Session.Status.UPCOMING)
    users = list(MessengerUser.objects.values_list('messenger_id', flat=True))
    notify_users({"user_ids": users}, "notify-new-session")

@shared_task
def on_end_register_time(session_id):
    current_session = Session.objects.get(id=session_id)
    current_session.change_status_to(Session.Status.WAITING)
    current_participants = SessionParticipant.objects.filter(session=current_session)
    previous_session = current_session.get_previous_session()
    users = list(MessengerUser.objects.values_list('messenger_id', flat=True))
    notify_users({"user_ids": users}, "notify-end-register")
    
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
    