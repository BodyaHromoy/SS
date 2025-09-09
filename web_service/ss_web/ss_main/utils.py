from django.utils import timezone
from .models import Eventlogger

def log_event(user, shkaf_id, readable_name, action, door_state_before=None):
    Eventlogger.objects.create(
        user=user.username if user and user.is_authenticated else "anonymous",
        shkaf_id=str(shkaf_id),
        login=user.username if user and user.is_authenticated else "",
        action=action,
        time=timezone.now(),
        door_state_before=door_state_before
    )
