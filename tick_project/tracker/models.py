from django.db import models
from django.utils import timezone

from django.conf import settings
# Create your models here.

class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7, default="#C3C3C3")
    created_at = models.DateTimeField(auto_now_add=True)  
    last_edited = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.name

    def total_time_spent(self):
        total_seconds = sum(task.total_time_spent() for task in self.taks)
        return total_seconds
    
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=280)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  
    last_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.project}"

    def total_time_spent(self):
        total_seconds = sum(session.duration for session in self.sessions.all())
        return total_seconds

class Session(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="sessions")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.task}({self.start_time})"
    
    def set_start_time(self):
        self.start_time = timezone.now()

    def set_end_time(self):
        self.end_time = timezone.now()

    @property
    def duration(self):
        return self.end_time - self.start_time