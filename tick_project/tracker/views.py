from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone
from .models import Task, Project
# Create your views here.
def index(request):
    template = "index.html"
    context = {}
    tasks = Task.objects.filter(project__user=request.user)
    context["tasks"] = tasks
    context["projects"] = Project.objects.filter(user = request.user)
    today_sessions = []
    for task in tasks:
        for session in task.sessions.all():
            if session.start_time.date() == timezone.now().date():
                today_sessions.append(session)
    today_time = sum(session.duration_in_seconds() for session in today_sessions)
    context["today_time"] = timedelta(seconds=today_time)
    return render(request, template, context)