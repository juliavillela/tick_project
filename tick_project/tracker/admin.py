from django.contrib import admin
from .models import Project, Task, Session
# Register your models here.

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Session)
