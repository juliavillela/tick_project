from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import Task, Session
from ..forms import SessionReviewForm

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

        template = "tracker/session_track.html"
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

        return redirect("tracker:session-review", pk=session.pk)
    else:
        template = "tracker/session_track.html"
        context = {
            "task": task,
            "session": session
        }
        return render(request, template, context)
    
def session_review(request, pk):
    session = get_object_or_404(Session, pk=pk, task__project__user=request.user)

    template = "tracker/form.html"

    context = {
            "title": "Review session",
            "action": "Save",
            "disable_cancel": True,
        }
    
    if request.method == "POST":
        form = SessionReviewForm(request.POST, session=session)
        if form.is_valid():
            # update task
            task = session.task
            task.name = form.cleaned_data["task_name"]
            task.is_done = form.cleaned_data["mark_done"]
            task.save()

            # update session
            minutes = form.cleaned_data["duration_minutes"]
            session.set_custom_duration(minutes * 60)
            session.save()

            return redirect("tracker:task-detail", pk=task.pk)
        else:
            context["form"] = form
            return render(request, template, context)

    else:
        context["form"] = SessionReviewForm(session=session)
        return render(request, template, context)