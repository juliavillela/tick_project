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
    session_id = request.session.get("current_session_id")
    print(session_id)
    if session_id:
        current_session = Session.objects.get(pk=session_id)
        return {
            "current_session": current_session
        }
    else:
        return {
            "current_session": None
        }