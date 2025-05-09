from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class MessengerUser(models.Model):
    messenger_id = models.BigIntegerField(unique=True)

    def __str__(self):
        return str(self.messenger_id)


class User(models.Model):
    NUMBER_CHOICES = [(i, str(i)) for i in range(1, 121)]

    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(MessengerUser, on_delete=models.CASCADE,
                                   related_name='created_users')
    default_hezb = models.IntegerField(null=True, blank=True, default=None,
                                       validators=[MinValueValidator(1),
                                                   MaxValueValidator(120)])

    def __str__(self):
        return (f"User: {self.name} Created by: {self.created_by} ==> default "
                f"hezb: ({self.default_hezb})")
