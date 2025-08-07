from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import Project
from ..forms import TaskForm, ProjectForm
from ..helpers import current_session_context

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
def project_archive(request, pk):
    project = get_object_or_404(Project, pk=pk, user = request.user)
    project.active = False
    project.save()
    return redirect("tracker:project-detail", pk=pk)

@login_required
def project_unarchive(request, pk):
    project = get_object_or_404(Project, pk=pk, user = request.user)
    project.active = True
    project.save()
    return redirect("tracker:project-detail", pk=pk)

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
