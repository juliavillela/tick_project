from django.urls import path
from . import views

app_name = "tracker"

urlpatterns = [
    path("", views.index, name="index"),
    path("tasks/", views.task_list, name="tasks"),
    path("task/", views.task_create, name="task-create"),
    path("task/<int:pk>", views.task_detail, name="task-detail"),
]
