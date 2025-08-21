from django.utils import timezone
from datetime import timedelta

from ..helpers import timedelta_to_dict

def group_sessions_by_project(sessions):
    """
    Groups a list of sessions by their associated project.

    Args:
        sessions (iterable): An iterable of Session instances.

    Returns:
        dict: A dictionary where keys are Project instances and values are lists of
              Session instances belonging to that project.
    """
    sessions_by_project = {}
    for session in sessions:
        project = session.task.project
        if project not in sessions_by_project:
            sessions_by_project[project] = []
        sessions_by_project[project].append(session)

    return sessions_by_project

def build_annotated_project_summary(sessions_by_project:dict, total_seconds:int):
    """
    Builds a summary of projects with annotated total time spent and percentage of total time.

    Each project in the summary will have three additional attributes:
        - `total_seconds`: total time spent on that project in seconds.
        - `time_spent_dict`: dictionary representation of total time spent (via `timedelta_to_dict`).
        - `percentage`: percentage of total_seconds that were spent on project.

    Args:
        sessions_by_project (dict): A dictionary mapping Project instances to a list of Session instances.
        total_seconds (int): Total seconds spent across all projects (used to calculate percentage).

    Returns:
        list: A list of Project instances with annotated attributes.
    """
    
    project_summary = []
    for project, project_sessions in sessions_by_project.items():
        project.total_seconds = sum(session.duration_in_seconds() for session in project_sessions)
        project.time_spent_dict = timedelta_to_dict(timedelta(seconds=project.total_seconds))
        if total_seconds > 0:
            project.percentage = round(project.total_seconds/total_seconds * 100)
        else:
            project.percentage = 0
        project_summary.append(project)
    return project_summary

def group_sessions_by_date(sessions):
    """
    Groups a list of sessions by start_time date.

    Args:
        sessions (iterable): An iterable of Session instances.

    Returns:
        dict: A dictionary where keys are dates and values are lists of
              Session instances started on that date.
    """
    sessions_by_date = {}
    for session in sessions:
        date = session.start_time.date()
        if date not in sessions_by_date:
            sessions_by_date[date] = []
        sessions_by_date[date].append(session)
    return sessions_by_date

def build_daily_summary(sessions_by_date, date_start, date_end, date_format):
    """
    Builds a daily summary of session durations within a given date range.

    For each day in the range, it calculates the total seconds spent on sessions and
    creates a dictionary representation of the time. If there are no sessions for a day,
    the total seconds is 0.

    Args:
        sessions_by_date (dict): A dictionary mapping dates (datetime.date) to lists of Session instances.
        date_start (datetime.date): The first date in the range.
        date_end (datetime.date): The last date in the range (inclusive).
        date_format (str): A format string used to label each day (e.g., "%A" for weekday name).

    Returns:
        list: A list of dictionaries, each representing a day with keys:
            - "date_label": Formatted date string according to `date_format`.
            - "total_seconds_spent": Total time spent in seconds for that day.
            - "daily_time_spent_dict": Dictionary representation of total time spent (from `timedelta_to_dict`).
    """
    daily_summary = []
    date = date_start
    while date <= date_end:
        daily_sessions = sessions_by_date.get(date)
        if daily_sessions:
            total_seconds_spent = sum(session.duration_in_seconds() for session in daily_sessions)
        else:
            total_seconds_spent = 0

        daily_summary.append({
            "date_label": date.strftime(date_format), 
            "total_seconds_spent": total_seconds_spent,
            "daily_time_spent_dict": timedelta_to_dict(timedelta(seconds=total_seconds_spent))
        })
        
        date = date + timedelta(days=1)

    return daily_summary