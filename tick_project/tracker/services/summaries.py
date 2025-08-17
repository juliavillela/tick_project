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
        project.percentage = round(project.total_seconds/total_seconds * 100)
        project_summary.append(project)
    return project_summary

