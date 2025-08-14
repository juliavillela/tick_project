from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import Project
from ..forms import TaskForm, ProjectForm
from ..helpers import current_session_context

@login_required
def project_list(request):
    context = current_session_context(request)

    context["active_projects"] = Project.objects.filter(user=request.user, active=True).order_by('-last_edited')
    context["archived_projects"] = Project.objects.filter(user=request.user, active=False).order_by('-last_edited')
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
    template = "tracker/form.html"
    
    context = current_session_context(request)
    context.update(
        {
            "title": "Create new project",
            "action": "Save",
        }
    )

    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect("tracker:project-detail", pk=project.pk)
        else:
            context["form"] = form
            return render(request, template, context)
    else:
        context["form"] = ProjectForm()

        return render(request, template, context)

@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    
    template = "tracker/form.html"
    
    context = current_session_context(request)
    context.update(
        {
            "title": "Edit project",
            "action": "Save",
        }
    )

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project.save()
            return redirect("tracker:project-detail", pk=project.pk)
        else:
            context["form"] = form
            return render(request, template, context)
        
    else:
        context["form"] = ProjectForm(instance=project)
        return render(request, template, context)

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)

    template = "tracker/form.html"
    
    context = current_session_context(request)
    context.update(
        {
            "title": "Delete project",
            "details": f'If you delete <strong>{project.name}</strong>, all related tasks and recorded sessions will be permanently removed. <strong>This cannot be undone.</strong> Are you sure you want to continue?',
            "action": "Delete",
        }
    )

    if request.method == "POST":
        project.delete()
        return redirect("tracker:projects")
    else:
        return render(request, template, context)

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
    template = "tracker/form.html"
    
    context = current_session_context(request)
    context.update(
        {
            "title": f'Create task in project <strong>{project.name}</strong>',
            "action": "Save",
        }
    )
    if request.method == "POST":
        form = TaskForm(request.POST, user=request.user, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect("tracker:project-detail", pk=project.pk)
        else:
            context["form"] = form
            return render(request, template, context)
    else: 
        context["form"] = TaskForm(project=project)
        return render(request, template, context)
