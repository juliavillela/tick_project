from datetime import timedelta
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Task, Project, Session
from .forms import TaskForm, ProjectForm
from .helpers import timedelta_to_dict, current_session_context

def index(request):
    template = "index.html"
    return render(request, template)

@login_required
def dashboard(request):
    """
        Display the user's dashboard with summary of activity.

        Shows:
        - Total time tracked today
        - Number of tasks completed today
        - List of recent pending tasks
        - List of recent projects
    """
    template = "dashboard.html"
    context = current_session_context(request)

    # Get user's tasks and projects, ordered by most recently edited
    tasks = Task.objects.filter(project__user=request.user).order_by('-last_edited')
    projects = Project.objects.filter(user = request.user).order_by('-last_edited')

    # Add five most recently edited projects to context
    context["projects"] = projects[:5]

    # Collect tasks completed today and sessions started today
    today_sessions = []
    today_tasks = []
    for task in tasks:
        if task.is_done:
            if task.done_at.date() == timezone.now().date():
                today_tasks.append(task)
        for session in task.sessions.all():
            if session.start_time.date() == timezone.now().date():
                today_sessions.append(session)
    
    # Sum duration of today's sessions
    today_time = sum(session.duration_in_seconds() for session in today_sessions)
    
    # Get pending tasks and add five most recent to context
    pending_tasks = tasks.filter(is_done=False)
    context["tasks"] = pending_tasks[:5]

    # Add today's tracked time and number of tasks completed today to context
    context["today_time"] = timedelta_to_dict(timedelta(seconds=today_time))
    context ["today_tasks"] = len(today_tasks)
    return render(request, template, context)

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
        context ["referer"] = request.META.get("HTTP_REFERER", None)
        
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
        context["referer"] = request.META.get("HTTP_REFERER", None)

        return render(request,template, context)

@login_required   
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, project__user=request.user)
    referer = request.META.get("HTTP_REFERER", None)

    if request.method == "POST":
        task.delete()
        return redirect("tracker:tasks")
    else: 
        context = current_session_context(request)   
        template = "task_delete_form.html"

        context["task"] = task
        context["referer"] = referer
        
        return render(request, template, context)
    
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
        session = Session.objects.create(task=task)
        session.set_start_time()
        session.save()
 
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
    
@login_required
def project_list(request):
    context = current_session_context(request)

    context["projects"] = Project.objects.filter(user=request.user).order_by('-last_edited')

    return render(request, "project_list.html", context)

@login_required
def project_detail(request, pk):
    context = current_session_context(request)
    project = get_object_or_404(Project, pk=pk, user=request.user)
    context["project"] = project
    
    context["pending_tasks"] = project.tasks.filter(is_done=False).order_by('-last_edited')
    context["done_tasks"] = project.tasks.filter(is_done=True).order_by('-last_edited')
    
    return render(request, "project_detail.html", context)

@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect("tracker:project-detail", pk=project.pk)
    else:
        context = current_session_context(request)
        context["form"] = ProjectForm()

        return render(request, "project_form.html", context)

@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project.save()
            return redirect("tracker:project-detail", pk=project.pk)
    else:
        context = current_session_context(request)
        context["form"] = ProjectForm(instance=project)

        return render(request, "project_form.html", context)

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == "POST":
        project.delete()
        return redirect("tracker:projects")
    else:
        context = current_session_context(request)

        context["project"] = project

        return render(request, "project_delete_form.html", context)
    
@login_required
def create_task_for_project(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, user=request.user, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect("tracker:project-detail", pk=project.pk)

    else:
        context = current_session_context(request)
        context["form"] = TaskForm(project=project)
        context["project"] = project

        return render(request, "task_form.html", context)