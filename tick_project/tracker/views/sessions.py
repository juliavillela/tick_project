from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import Task, Session

@login_required
def session_start(request, pk):
    task = get_object_or_404(Task, pk=pk, project__user=request.user)

    # If a session is already in progress: redirect to current_session.
    current_session = Session.objects.get_active_session(request.user)
    if current_session:
        if current_session.task != task:
            messages.error(request, f"You are already tracking a session for '{current_session.task.name}', please finish it before starting another one.")
        return redirect("tracker:session-active", pk=current_session.pk)
    
    # Create a new session for task
    if request.method == "POST":
        session = Session.objects.create_new_session(user=request.user,task=task)
        return redirect("tracker:session-active", pk=session.pk)
   
    # Display track starting page
    else:

        template = "track.html"
        context = {
            "task": task
        }
        return render(request, template, context)

@login_required
def session_active(request, pk):
    session = get_object_or_404(Session, pk=pk, task__project__user=request.user)
    task = session.task
    if request.method == "POST":
        session.set_end_time()
        session.save()

        return redirect("tracker:task-detail", pk=task.pk)
    else:
        template = "track.html"
        context = {
            "task": task,
            "session": session
        }
        return render(request, template, context)
    