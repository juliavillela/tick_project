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

    # Get date reference
    today = timezone.now().date()

    # Fetch user-specific data
    projects = Project.objects.filter(user = request.user).order_by('-last_edited')
    today_tasks = Task.objects.by_user_and_done_date_within(user=request.user, date=today, days=1)
    pending_tasks = Task.objects.by_user_and_is_pending(user=request.user)
    today_sessions = Session.objects.by_user_and_start_date_within(user=request.user, date=today, days=1)

    # Sum duration of today's sessions
    today_time = sum(session.duration_in_seconds() for session in today_sessions)
    
    context["tasks"] = pending_tasks[:5]
    context["projects"] = projects[:5]
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

@login_required
def daily(request, days_ago):
    """
    Display a summary of the user's activity for a specific day.

    The view shows all sessions started on the selected day (today - days_ago),
    grouped by project. Only projects with tracked time are displayed.
    The user can navigate to previous or next days.
    """
    # Calculate the target date by subtracting `days_ago` from today
    date = timezone.now().date() - timedelta(days=days_ago)
    template = "daily.html"

    # Fetch all of the user's projects, ordered by most recently edited
    projects = Project.objects.filter(user = request.user).order_by('-last_edited')

    daily_sessions = [] # List to collect all sessions that occurred on the target date
    daily_projects = [] # List to collect only projects that had sessions on that date
    
    # Iterate through the user's projects to gather relevant sessions
    for project in projects:
        sessions = project.sessions_by_date(date)
        daily_sessions.extend(sessions)
        # Sum the total time spent across sessions for this project
        daily_seconds= sum(session.duration_in_seconds() for session in sessions)
        
        # If time was spent, store that info on the project and add it to the list
        if daily_seconds > 0:
            # Attach a human-readable time dictionary to the project (e.g., {'hours': 1, 'minutes': 30})
            project.daily_time_spent_dict = timedelta_to_dict(timedelta(seconds=daily_seconds))
            daily_projects.append(project)

    # Sort all sessions by their start time (earliest first)
    daily_sessions.sort(key=lambda s: s.start_time)

    context = current_session_context(request)
    context["projects"] = daily_projects
    context["sessions"] = daily_sessions
    context["date"] = date
    context["previous"] = days_ago + 1
    context["next"] = days_ago - 1 if days_ago > 0 else None

    return render(request, template, context)
