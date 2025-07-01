from django.forms import ModelForm

from .models import Task, Project

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ["project", "name", "is_done"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = user.project_set.all()
        # set label for is_done field
        self.fields["is_done"].label = "Done"
        # set form-control bs class to fields
        for name, field in self.fields.items():
            if name in ["project", "name"]:
                field.widget.attrs.update({'class': 'form-control'})
            elif name == "is_done":
                field.widget.attrs.update({'class': 'form-check-input'})

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({'class': 'form-control'})