from datetime import timedelta
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import Task, Project
from .forms import TaskForm

def index(request):
    template = "index.html"
    context = {}
    tasks = Task.objects.filter(project__user=request.user).order_by('-last_edited')
    context["tasks"] = tasks[:5]
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
        is_done=False  # pending tasks
    ).order_by('-last_edited')  # newest edited first
    
    context = {
        "pending_tasks": pending_tasks
    }
    return render(request, "task_list.html", context)

def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save()
            return redirect("tracker:tasks")
    else:
        template = "task_form.html"
        context = {
            "form": TaskForm(user=request.user)
        }
        return render(request,template, context)
    

