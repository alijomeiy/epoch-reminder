from django.db import models

class Session(models.Model):
    class Status(models.TextChoices):
        REGISTER = 'upcoming', 'Upcoming '
        RUN = 'ongoing', 'Ongoing '
        FINISH = 'completed', 'Completed'
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    start_register_time = models.DateTimeField()
    end_register_time = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.REGISTER,
    )

    def __str__(self):
        return f"Session from {self.start_time} to {self.end_time} ({self.status})"
