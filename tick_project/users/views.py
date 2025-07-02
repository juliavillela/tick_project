from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

login_redirect = 'tracker:dashboard'
User = get_user_model()

def register(request):
    template = "register.html"
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirmation = request.POST.get("password-confirmation")
        # check password matches confirmation
        if password != password_confirmation:
            messages.error(request, "Passwords do not match.")
            return render(request, template)
        # check email is unique in database: 
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, template)
        user = User.objects.create_user(email=email, password=password)
        login(request,user)
        return redirect(login_redirect)
        
    else:
        return render(request, template)

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