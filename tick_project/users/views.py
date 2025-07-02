from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .forms import RegisterForm

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
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request=request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect(login_redirect)
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, template)
    else:
        return render(request, template)

def logout_view(request):
    logout(request)
    return redirect("tracker:index")

@login_required
def user_detail(request):
    context = {
        "user": request.user
    }
    return render(request, "user_detail.html", context)