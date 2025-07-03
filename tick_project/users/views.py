from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .forms import RegisterForm, EmailAuthenticationForm, EmailUpdateForm

login_redirect = 'tracker:dashboard'
User = get_user_model()

def register(request):
    template = "register.html"

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
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
    logout(request)
    return redirect("tracker:index")

@login_required
def user_detail(request):
    context = {
        "user": request.user
    }
    return render(request, "user_detail.html", context)

@login_required
def user_update_email(request):
    template = "user_email_form.html"
    if request.method == "POST":
        form = EmailUpdateForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            updated_user = form.save()
            return redirect("users:account")
        else:
            return render(request, template, {"form": form})
    else:
        context = {
            "form": EmailUpdateForm(instance=request.user, user=request.user)
        }

        return render(request, template, context)