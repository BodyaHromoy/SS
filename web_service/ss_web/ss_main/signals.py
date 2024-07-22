from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import UserSession


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    session_key = request.session.session_key
    UserSession.objects.update_or_create(user=user, defaults={'session_key': session_key})


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    UserSession.objects.filter(user=user).delete()
