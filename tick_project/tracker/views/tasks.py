from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import Task
from ..forms import TaskForm
from ..helpers import current_session_context

@login_required
def task_list(request):
    context = current_session_context(request)

    context["pending_tasks"] = Task.objects.filter(
        project__user=request.user,
        is_done=False  # pending tasks
    ).order_by('-last_edited')  # newest edited first
    
    context["done_tasks"] = Task.objects.filter(
        project__user=request.user,
        is_done=True
    ).order_by('-last_edited')  # newest edited first

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

        context = current_session_context(request)
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
        context = current_session_context(request)

        template = "task_form.html"
        
        context["form"] = TaskForm(user=request.user, instance=task),

        return render(request,template, context)

@login_required   
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, project__user=request.user)

    if request.method == "POST":
        task.delete()
        return redirect("tracker:tasks")
    else: 
        context = current_session_context(request)   
        template = "task_delete_form.html"

        context["task"] = task
        
        return render(request, template, context)
    