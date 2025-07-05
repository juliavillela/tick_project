from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .forms import RegisterForm, EmailAuthenticationForm, EmailUpdateForm, PasswordUpdateForm, UserDeleteForm
from tracker.models import Project, Session

login_redirect = 'tracker:dashboard'
logout_redirect = 'tracker:index'
User = get_user_model()

def register(request):
    template = "register.html"

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # create a default project for new user
            Project.objects.create(user=user, name="General")
            login(request,user)
            return redirect(login_redirect)
        else:
            messages.error(request, "Something went wrong! :( Please correct the errors bellow:")
            return render(request, template, {"form":form})
    else:
        context = {
        "form": RegisterForm()
        }
        return render(request, template, context)

def login_view(request):
    template = "login.html"
    if request.method == "POST":
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(login_redirect)
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, template, {"form":form})
    else:
        context = {
            "form": EmailAuthenticationForm(request)
        }
        return render(request, template, context)

def logout_view(request):
    # finish current session before logging user out.
    current_session_id = request.session.get("current_session_id")
    if current_session_id:
        current_session = Session.objects.get(pk=current_session_id)
        current_session.set_end_time()
        current_session.save()
    logout(request)
    return redirect(logout_redirect)

@login_required
def user_detail(request):
    context = {
        "user": request.user
    }
    return render(request, "user_detail.html", context)

@login_required
def user_update_email(request):
    template = "user_form.html"
    if request.method == "POST":
        form = EmailUpdateForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            updated_user = form.save()
            return redirect("users:account")
        else:
            return render(request, template, {"form": form})
    else:
        context = {
            "form": EmailUpdateForm(instance=request.user, user=request.user),
            "title": "Edit user email.",
            "actioin": "Save",
        }

        return render(request, template, context)
    
@login_required
def user_update_password(request):
    template = "user_form.html"
    if request.method == "POST":
        form = PasswordUpdateForm(data=request.POST, user=request.user)
        if form.is_valid():
            updated_user = form.save()
            return redirect("users:account")
        else:
            return render(request, template, {"form": form})
    else:
        context = {
            "form": PasswordUpdateForm(user=request.user),
            "title": "Choose a new password.",
            "details": "Once you change your password you will be logged out and required to log back in with the new password.",
            "action": "Save",
        }

        return render(request, template, context)
    
@login_required
def user_delete(request):
    template = "user_form.html"

    if request.method == "POST": 
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect(logout_redirect)
    else:
        context = {
            "form": UserDeleteForm(user=request.user),
            "title": "Delete your account.",
            "details": "This action will permanently delete your account and all data associated with it.",
            "action": "Delete",
        }

        return render(request, template, context)