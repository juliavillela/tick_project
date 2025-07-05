from datetime import timedelta
from django.db import models
from django.utils import timezone

from django.conf import settings

from .helpers import timedelta_to_dict
# Create your models here.

class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7, default="#C3C3C3")
    created_at = models.DateTimeField(auto_now_add=True)  
    last_edited = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.name
    
    def total_time_spent_dict(self):
        return timedelta_to_dict(timedelta(seconds=self.total_seconds_spent()))

    def total_seconds_spent(self):
        total_seconds = sum(task.total_seconds_spent() for task in self.tasks.all())
        return total_seconds
    
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=280)
    is_done = models.BooleanField(default=False)
    done_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # update done_at according to task.is_done 
        if self.is_done and not self.done_at:
            self.done_at = timezone.now()
        if not self.is_done and self.done_at:
            self.done_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.project}"

    def total_time_spent_dict(self):
        return timedelta_to_dict(timedelta(seconds=self.total_seconds_spent()))

    def total_seconds_spent(self):
        total_seconds = sum(session.duration_in_seconds() for session in self.sessions.all())
        return total_seconds

class SessionManager(models.Manager):
    def get_active_session(self, user):
        active_session = self.filter(
            task__project__user = user,
            end_time__isnull = True
        ).first()
        return active_session

    def end_current_session(self, user):
        active_session = self.get_active_session(user)
        if active_session:
            active_session.set_end_time()
            active_session.save()

class Session(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="sessions")
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    objects = SessionManager()

    def __str__(self):
        return f"{self.task}({self.start_time})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # update last_edited timestamp on task when a session is saved.
        Task.objects.filter(pk=self.task.pk).update(last_edited=timezone.now())
        Project.objects.filter(pk=self.task.project.pk).update(last_edited=timezone.now())

    def set_start_time(self):
        self.start_time = timezone.now()

    def set_end_time(self):
        self.end_time = timezone.now()

    def duration_in_seconds(self):
        if self.start_time is None or self.end_time is None:
            return 0
        duration = self.end_time - self.start_time
        return duration.total_seconds()
    
    def duration_dict(self):
        return timedelta_to_dict(timedelta(seconds=self.duration_in_seconds()))