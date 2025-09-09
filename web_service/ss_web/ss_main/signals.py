from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import UserSession
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Cabinet, Eventlogger

@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    session_key = request.session.session_key
    UserSession.objects.update_or_create(user=user, defaults={'session_key': session_key})


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    UserSession.objects.filter(user=user).delete()


@receiver(pre_save, sender=Cabinet)
def log_cabinet_changes(sender, instance, **kwargs):
    if not instance.pk:
        return  # новая запись — пока пропускаем

    old_instance = Cabinet.objects.get(pk=instance.pk)
    changes = []
    for field in instance._meta.fields:
        fname = field.name
        old_val = getattr(old_instance, fname)
        new_val = getattr(instance, fname)
        if old_val != new_val:
            changes.append(f"{fname}: {old_val} → {new_val}")

    if changes and hasattr(instance, "_request_user"):
        Eventlogger.objects.create(
            user=instance._request_user.username,
            shkaf_id=str(instance.pk),
            login=instance._request_user.username,
            action="; ".join(changes),
            time=timezone.now(),
            door_state_before=getattr(old_instance, "door_state", None)
        )