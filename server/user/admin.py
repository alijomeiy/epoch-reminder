from django.contrib import admin
from .models import User, MessengerUser


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(MessengerUser)
class MessengerUserAdmin(admin.ModelAdmin):
    pass
