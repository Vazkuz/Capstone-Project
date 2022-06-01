from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import ClassType, ClimbClass, User
from .admin import ClimbClassForm
from django.forms import ModelForm        

# Create your views here.
def index(request):
    # availableClasses = ClimbClass.objects.filter(isAvailable = True)
    return render(request, "escalada/index.html", {
        # "availableClasses": availableClasses
    })

@staff_member_required(login_url=reverse_lazy('index'))
def createClass(request):
    newClassForm = ClimbClassForm()
    return render(request, "escalada/create_class.html", {
        "newClassForm": newClassForm,
        "errorInCreation": False
    })
    
@staff_member_required(login_url=reverse_lazy('index'))
def newClass(request):
    class_form = ClimbClassForm(request.POST)
    if request.method == 'POST':
        classType = ClassType.objects.get(pk=request.POST["classType"])
        lessonDay = request.POST.getlist('lessonDay')
        if len(lessonDay) > 0:
            newClass = ClimbClass(classType=classType, lessonDay=lessonDay)
        else:
            newClass = ClimbClass(classType=classType)
            
        if class_form.is_valid():
            newClass.save()
        else:
            return render(request, "escalada/error_in_newclass.html")
        return HttpResponseRedirect(reverse("index"))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "escalada/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "escalada/login.html")
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "escalada/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "escalada/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "escalada/register.html")