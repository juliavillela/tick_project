def timedelta_to_dict(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    return {
        "hours": hours,
        "minutes": minutes
    }

def current_session_context(request):
    from .models import Session
    return {
        "current_session": Session.objects.get_active_session(request.user)
    }