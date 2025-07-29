from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from ..models import Task, Project, Session
from ..helpers import timedelta_to_dict, current_session_context


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
    today_tasks = Task.objects.by_user_and_done_date_within(user=request.user, date=today)
    pending_tasks = Task.objects.by_user_and_is_pending(user=request.user)
    today_sessions = Session.objects.by_user_and_start_date_within(user=request.user, date=today)

    # Sum duration of today's sessions
    today_time = sum(session.duration_in_seconds() for session in today_sessions)
    
    context["tasks"] = pending_tasks[:5]
    context["projects"] = projects[:5]
    context["today_time"] = timedelta_to_dict(timedelta(seconds=today_time))
    context ["today_tasks"] = len(today_tasks)
    return render(request, template, context)

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

    # Fetch all sessions started on this date
    all_daily_sessions = Session.objects.by_user_and_start_date_within(
        user=request.user, 
        date=date
        ).select_related("task", "task__project").order_by('start_time')
    
    # Fetch all tasks completed on this date
    daily_tasks = Task.objects.by_user_and_done_date_within(user=request.user, date=date)
    # Calculate total seconds spent focused on this date
    daily_seconds = sum(session.duration_in_seconds() for session in all_daily_sessions)

    # Group sessions by project
    sessions_by_project = {}
    for session in all_daily_sessions:
        project = session.task.project
        if project not in sessions_by_project:
            sessions_by_project[project] = []
        sessions_by_project[project].append(session)

    # Build project summaries
    daily_projects = []
    for project, project_sessions in sessions_by_project.items():
        project.daily_seconds = sum(session.duration_in_seconds() for session in project_sessions)
        project.daily_time_spent_dict = timedelta_to_dict(timedelta(seconds=project.daily_seconds))
        project.percentage = round(project.daily_seconds/daily_seconds * 100)
        daily_projects.append(project)

    context = current_session_context(request)
    context["projects"] = daily_projects
    context["sessions"] = all_daily_sessions
    context["daily_tasks"] = len(daily_tasks)
    context["daily_time"] = timedelta_to_dict(timedelta(seconds=daily_seconds))
    context["date"] = date.strftime("%A, %B %d")
    context["previous"] = days_ago + 1
    context["next"] = days_ago - 1 if days_ago > 0 else None

    return render(request, template, context)

@login_required
def weekly(request, weeks_ago):
    # Define the start date as 7 days ago from today
    today = timezone.now().date()
    date_start = today - timedelta(days=(weeks_ago * 7 + 6))
    date_end = today - timedelta(days=(weeks_ago * 7))
    template = "weekly.html"

    # Fetch all tasks marked as done by the user within the last 6 days (7 total days)
    weekly_tasks = Task.objects.by_user_and_done_date_within(user=request.user, date=date_start, extra_days=6)
    
    # Fetch all sessions started within week
    all_weekly_sessions = Session.objects.by_user_and_start_date_within(
        user=request.user, 
        date=date_start, 
        extra_days=6
        ).select_related("task", "task__project")
    
    # Calculate total seconds focused for the week
    weekly_seconds = sum(session.duration_in_seconds() for session in all_weekly_sessions)
    
    # Organize sessions by date and by project
    sessions_by_date = {}
    sessions_by_project = {}

    for session in all_weekly_sessions:
        date = session.start_time.date()
        if date not in sessions_by_date:
            sessions_by_date[date] = []
        sessions_by_date[date].append(session)
        project = session.task.project
        if project not in sessions_by_project:
            sessions_by_project[project] = []
        sessions_by_project[project].append(session)

    # Build daily summaries
    week_days = []

    for day_offset in range(7):
        date = date_start + timedelta(days=day_offset)
        daily_sessions = sessions_by_date.get(date)
        if daily_sessions:
            total_seconds_spent = sum(session.duration_in_seconds() for session in daily_sessions)
        else:
            total_seconds_spent = 0

        week_days.append({
            "weekday": date.strftime("%A"), # e.g., Monday, Tuesday 
            "total_seconds_spent": total_seconds_spent,
            "daily_time_spent_dict": timedelta_to_dict(timedelta(seconds=total_seconds_spent))
        })

    # Build project summaries
    weekly_projects = []
    for project, project_sessions in sessions_by_project.items():
        project.weekly_seconds = sum(session.duration_in_seconds() for session in project_sessions)
        project.weekly_time_spent_dict = timedelta_to_dict(timedelta(seconds=project.weekly_seconds))
        if weekly_seconds > 0:
            project.percentage = round((project.weekly_seconds/weekly_seconds)*100)
        else:
            project.percentage = 0
        weekly_projects.append(project)
    
    context = current_session_context(request)
    context.update({
        "weekly_time": timedelta_to_dict(timedelta(seconds=weekly_seconds)),
        "weekly_tasks": len(weekly_tasks),
        "week_date": f"{date_start.strftime("%A %B %d")} - {date_end.strftime("%B %d")}",
        "week_days": week_days,
        "projects": weekly_projects,
        "previous": weeks_ago + 1,
        "next": weeks_ago - 1 if weeks_ago > 0 else None
    })

    return render(request, template, context)