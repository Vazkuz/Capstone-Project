from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import ClassType, ClimbClass, Coupon, Enrollment, User
from .forms import ClimbClassForm, EnrollmentForm, EnrollmentFormStudents
from datetime import datetime, timedelta

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

@login_required
def enroll(request):
    enroll_form = EnrollmentFormStudents()
    return render(request, "escalada/enroll.html", {
        "enroll_form": enroll_form
    })
    
@login_required
def enroll_success(request):
    class_form = EnrollmentFormStudents(request.POST)
    climbClass = request.POST.get('climbClass')
    coupon = request.POST.get('coupon')
    begin_date = request.POST.get('begin_date')
    begin_date_DF = datetime.strptime(begin_date, '%Y-%m-%d')
    numberOfLessons = Coupon.objects.get(pk=coupon).getNumberOfClasses()
    
    print('____________________________________________________________')
    print(numberOfLessons)
    print('____________________________________________________________')
    
    if class_form.is_valid():
        if request.method == 'POST':
            climber = request.user
            lessonDays = ClimbClass.objects.get(pk=climbClass).getLessonDays()
            for i in range(numberOfLessons):
                for j in range(7):
                    newDay = begin_date_DF + timedelta(days=i*7+j)
                    if newDay.strftime('%A').upper() in str(lessonDays).upper():
                        EnrollToLesson(climbClass, coupon, begin_date,newDay, climber)
                    
    else:
        return render(request, "escalada/error_in_newclass.html")
    return HttpResponseRedirect(reverse("index"))

def EnrollToLesson(climbClass, coupon, begin_date, class_date,climber):
    # Check if the enrollment already exists:
    if Enrollment.objects.filter(climbClass=climbClass, coupon=coupon, begin_date=begin_date, class_date=class_date).count() > 0:
        # If the class already exists, then the climber is added to that lesson:
        enrollment = Enrollment.objects.get(climbClass=climbClass, coupon=coupon, begin_date=begin_date, class_date=class_date)
        enrollment.climbers.add(climber)
    else:
        # If not, then the lesson is created and the climber enrolled to it
        climbClass = ClimbClass.objects.get(pk=climbClass)
        coupon = Coupon.objects.get(pk=coupon)
        newEnrollment = Enrollment(climbClass=climbClass, coupon=coupon, begin_date=begin_date, class_date=class_date)
        newEnrollment.save()
        newEnrollment.climbers.add(climber)
