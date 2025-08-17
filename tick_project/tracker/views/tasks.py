from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from ..models import Task
from ..forms import TaskForm
from ..helpers import current_session_context

@login_required
def task_list(request):
    context = current_session_context(request)
    context["pending_tasks"] = Task.objects.by_user_and_is_active(request.user,is_done=False)
    today = timezone.now().date()
    context["done_today"] = Task.objects.by_user_and_done_date_within(user=request.user, date=today)
    return render(request, "tracker/task_list.html", context)

@login_required
def task_create(request):
    template = "tracker/form.html"
    
    context = current_session_context(request)
    context.update(
        {
            "title": "Create new task",
            "action": "Save",
        }
    )

    if request.method == "POST":
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save()
            return redirect("tracker:tasks")
        else:
            context["form"] = form
            return render(request, template, context)
    else:
        context["form"] = TaskForm(user=request.user),
        return render(request,template, context)

@login_required    
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, project__user=request.user)
    context = current_session_context(request)
    
    sessions = task.sessions.all().order_by("-start_time")
    
    context["task"] = task
    context["sessions"] = sessions
    context["session_count"] = len(sessions)

    return render(request, "tracker/task_detail.html", context)

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, project__user=request.user)

    template = "tracker/form.html"
    
    context = current_session_context(request)
    context.update(
        {
            "title": "Edit task",
            "action": "Save",
        }
    )

    if request.method == "POST":
        form = TaskForm(request.POST, user=request.user, instance=task)
        if form.is_valid():
            task = form.save()
            return redirect("tracker:task-detail", pk=task.pk)
        else:
            context["form"] = form
            return render(request, template, context)
    else:
        
        context["form"] = TaskForm(user=request.user, instance=task),
        return render(request,template, context)

@login_required   
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, project__user=request.user)
    template = "tracker/form.html"
    
    context = current_session_context(request)
    context.update(
        {
            "title": "Delete task",
            "details": f"If you delete task <strong>{task.name}</strong> in project <strong>{task.project.name}</strong>, all recorded sessions will be removed. <strong>Are you sure you want to proceed?</strong>",
            "action": "Delete",
        }
    )
    if request.method == "POST":
        task.delete()
        return redirect("tracker:tasks")
    else: 
        context["task"] = task
        return render(request, template, context)
    