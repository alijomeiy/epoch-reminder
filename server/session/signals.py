from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import make_aware
from django_celery_beat.models import PeriodicTask, ClockedSchedule
import json
from .models import Session
from .tasks import (
    on_start_time, on_end_time,
    on_start_register_time, on_end_register_time
)

@receiver(post_save, sender=Session)
def schedule_session_tasks(sender, instance, created, **kwargs):
    if created:
        schedule_task(instance.start_time, on_start_time, instance.id, 'start_time')
        schedule_task(instance.end_time, on_end_time, instance.id, 'end_time')
        schedule_task(instance.start_register_time, on_start_register_time, instance.id, 'start_register')
        schedule_task(instance.end_register_time, on_end_register_time, instance.id, 'end_register')

def schedule_task(run_at, task_func, session_id, tag):
    clocked_time = make_aware(run_at)
    clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=clocked_time)

    PeriodicTask.objects.create(
        clocked=clocked,
        name=f"{task_func.__name__}_{session_id}_{tag}",
        task=f"{task_func.__module__}.{task_func.__name__}",
        one_off=True,
        args=json.dumps([session_id]),
    )
