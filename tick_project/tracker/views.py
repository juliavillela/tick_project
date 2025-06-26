from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Task, Project
from .forms import TaskForm

@login_required
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

@login_required
def task_list(request):
    pending_tasks = Task.objects.filter(
        project__user=request.user,
        is_done=False  # pending tasks
    ).order_by('-last_edited')  # newest edited first
    
    context = {
        "pending_tasks": pending_tasks
    }
    return render(request, "task_list.html", context)

@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save()
            return redirect("tracker:tasks")
    else:
        template = "task_form.html"
        context = {
            "form": TaskForm(user=request.user),
            "referer": request.META.get("HTTP_REFERER", None)
        }
        return render(request,template, context)

@login_required    
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, project__user=request.user)
    sessions = task.sessions.all().order_by("-start_time")
    context = {
        "task": task,
        "sessions": sessions,
        "session_count": len(sessions)
    }
    return render(request, "task_detail.html", context)

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, project__user=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, user=request.user, instance=task)
        if form.is_valid():
            task = form.save()
            return redirect("tracker:task-detail", pk=task.pk)
    else:
        template = "task_form.html"
        context = {
            "form": TaskForm(user=request.user, instance=task),
            "referer": request.META.get("HTTP_REFERER", None)
        }
        return render(request,template, context)

@login_required   
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, project__user=request.user)
    referer = request.META.get("HTTP_REFERER", None)

    if request.method == "POST":
        task.delete()
        return redirect("tracker:tasks")
    else:    
        template = "task_delete_form.html"
        context = {
            "task":task,
            "referer": referer
        }
        return render(request, template, context)