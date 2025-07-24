from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("account/", views.user_detail, name="account"),
    path("account/edit/", views.user_update_email, name="update-email"),
    path("account/edit_password/", views.user_update_password, name="update-password"),
    path("account/edit_timezone/", views.user_update_timezone, name="update-timezone"),
    path("account/delete/", views.user_delete, name="delete"),

]