from django import forms

from .models import Task, Project

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["project", "name", "is_done"]

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        # Filter project choices by user and only active projects
        if user:
            self.fields["project"].queryset = user.project_set.filter(active=True)

        # If a specific project is passed, remove field and use it in view
        if project:
            self.fields.pop("project")

        # set label for is_done field
        self.fields["is_done"].label = "Done"
        # set form-control bs class to fields
        for name, field in self.fields.items():
            if name in ["project", "name"]:
                field.widget.attrs.update({'class': 'form-control'})
            elif name == "is_done":
                field.widget.attrs.update({'class': 'form-check-input'})

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({'class': 'form-control'})

class SessionReviewForm(forms.Form):
    task_name = forms.CharField(label="Task name", max_length=255)
    duration_minutes = forms.IntegerField(label="Duration (minutes)", min_value=1)
    mark_done = forms.BooleanField(label="Mark task as done", required=False)

    def __init__(self, *args, **kwargs):
        session = kwargs.pop("session")
        super().__init__(*args, **kwargs)
        #set initial values
        self.fields["task_name"].initial = session.task.name
        self.fields["duration_minutes"].initial = session.duration_in_seconds() // 60
        self.fields["mark_done"].initial = session.task.is_done

        self.fields["task_name"].widget.attrs.update({'class': 'form-control'})
        self.fields["duration_minutes"].widget.attrs.update({'class': 'form-control'})
        self.fields["mark_done"].widget.attrs.update({'class': 'form-check-input'})