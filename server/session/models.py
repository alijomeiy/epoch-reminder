from django.db import models


class Session(models.Model):
    class Status(models.TextChoices):
        UPCOMING = 'upcoming', 'Upcoming '
        ONGOING = 'ongoing', 'Ongoing '
        COMPLETED = 'completed', 'Completed'
        WAITING = 'waiting', 'Waiting'

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    start_register_time = models.DateTimeField()
    end_register_time = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.UPCOMING,
    )
    create_time = models.DateTimeField(auto_now_add=True)
    
    def get_previous_session(self):
        return (
            Session.objects
            .filter(start_time__lt=self.start_time)
            .order_by('-create_time')
            .first()
        )
    
    def change_status_to(self, status):
        self.status = status
        self.save()

    def __str__(self):
        return f"Session from {self.start_time} to {self.end_time} ({self.status})"
