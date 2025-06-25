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
    today_tasks = []
    for task in tasks:
        if task.is_done:
            if task.done_at.date() == timezone.now().date():
                today_tasks.append(task)
        for session in task.sessions.all():
            if session.start_time.date() == timezone.now().date():
                today_sessions.append(session)
    today_time = sum(session.duration_in_seconds() for session in today_sessions)

    context["today_time"] = timedelta(seconds=today_time)
    context ["today_tasks"] = len(today_tasks)
    return render(request, template, context)

def task_list(request):
    pending_tasks = Task.objects.filter(
        project__user=request.user,
        is_done=False  # or False for pending tasks
    ).order_by('-last_edited')  # newest edited first
    
    context = {
        "pending_tasks": pending_tasks
    }
    return render(request, "task_list.html", context)
