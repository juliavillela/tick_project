from django.forms import ModelForm

from .models import Task

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ["project", "name"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = user.project_set.all()
        # set form-control bs class to fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})