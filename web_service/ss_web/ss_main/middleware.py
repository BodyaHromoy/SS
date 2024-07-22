from django.conf import settings
from django.contrib.auth import logout
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from .models import UserSession
from django.contrib.sessions.models import Session


class OneDeviceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            current_session_key = request.session.session_key
            user_session = UserSession.objects.filter(user=request.user).first()

            if user_session:
                if user_session.session_key != current_session_key:
                    session = Session.objects.filter(session_key=user_session.session_key).first()
                    if session:
                        session.delete()
                    logout(request)
                else:
                    user_session.last_activity = timezone.now()
                    user_session.save()
            else:
                UserSession.objects.create(user=request.user, session_key=current_session_key)
