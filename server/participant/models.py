from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from session.models import Session
from user.models import User


class SessionParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    hezb = models.IntegerField(null=True, blank=True, default=None,
                                       validators=[MinValueValidator(1),
                                                   MaxValueValidator(120)])
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} in {self.session}"