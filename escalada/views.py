from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import ClassType, ClimbClass, ClimbPassType, Coupon, FreeClimb, Lesson, MyCoupon, User
from .forms import ClimbClassForm, LessonFormStudents, BuyCouponForm, MyCouponForm, FreeClimbFormClimber
from datetime import datetime, date, time, timedelta

# Create your views here.
def index(request):
    availableClasses = ClimbClass.objects.filter(is_Available = True)
    return render(request, "escalada/index.html", {
        "availableClasses": availableClasses
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
    enroll_form = LessonFormStudents(climberFilter=request.user)
    return render(request, "escalada/enroll.html", {
        "enroll_form": enroll_form
    })
    
@login_required
def enroll_success(request):
    class_form = LessonFormStudents(request.POST)
    climbClass = request.POST.get('climbClass')
    coupon = request.POST.get('coupon')
    begin_date = request.POST.get('begin_date')
    begin_date_DF = datetime.strptime(begin_date, '%Y-%m-%d')
    numberOfLessons = Coupon.objects.get(pk=coupon).getNumberOfClasses()
    if class_form.is_valid():
        if request.method == 'POST':
            climber = request.user
            lessonDays = ClimbClass.objects.get(pk=climbClass).getLessonDays()
            # First check class availability (by number of students)
            availability = 0
            for i in range(numberOfLessons):
                for j in range(7):
                    newDay = begin_date_DF + timedelta(days=i*7+j)
                    if Lesson.objects.filter(climbClass=climbClass, coupon=coupon, class_date=newDay).count() > 0:
                        enrollment = Lesson.objects.get(climbClass=climbClass, coupon=coupon, class_date=newDay)
                        if enrollment.climbers.all().count() >= enrollment.getClimbClass().getClassType().getMaxClimbers():
                            newDayClass = newDay.strftime("%d/%m/%Y")
                            availability += 1
            # If availability is 0, that means that there is room in the lesson for another climber
            if availability == 0:
                for i in range(numberOfLessons):
                    for j in range(7):
                        newDay = begin_date_DF + timedelta(days=i*7+j)
                        if newDay.strftime('%A').upper() in str(lessonDays).upper():
                            EnrollToLesson(climbClass, coupon, newDay, climber)
                UseTicket(climber, coupon)
                return HttpResponseRedirect(reverse("index"))
                
            # If not, then the lesson is full
            enroll_form = LessonFormStudents(climberFilter=request.user)
            return render(request, "escalada/enroll.html", {
                "enroll_form": enroll_form,
                "error_message": f"Error: Class is full until {newDayClass}"
            })

    enroll_form = LessonFormStudents(climberFilter=request.user)
    return render(request, "escalada/enroll.html", {
        "enroll_form": enroll_form,
        "error_message": "Error: " + list(class_form.errors.as_data()['__all__'][0])[0]
    })
    
@login_required
def buyCoupon(request):
    buyForm = BuyCouponForm()
    return render(request, "escalada/buy_coupon.html", {
        "buyForm": buyForm
    })
    
@login_required
def buyCouponSubmit(request):
    climber = request.user    
    # If the coupon is for a recurring class, then its a one time use only, otherwise the number of tickets available is given by the coupon itself
    if Coupon.objects.get(pk=request.POST.get('coupon')).is_Recurring():
        ticketsAvailable = 1
    else:
        ticketsAvailable = Coupon.objects.get(pk=request.POST.get('coupon')).getNumberOfClasses()
    
    updated_request = request.POST.copy()
    updated_request['climber'] = climber
    updated_request['ticketsAvailable'] = ticketsAvailable
    myCouponForm = MyCouponForm(updated_request)
    if myCouponForm.is_valid():
        myCouponForm.save()
    else:
        buyForm = BuyCouponForm()
        if list(myCouponForm.errors.as_data()['__all__'][0])[0] == 'My coupon with this Climber and Coupon already exists.':
            return render(request, "escalada/buy_coupon.html", {
                "buyForm": buyForm,
                "error_message": "You already have that Coupon"
            })
        else:                    
            return render(request, "escalada/buy_coupon.html", {
                "buyForm": buyForm,
                "error_message": "Error: " + list(myCouponForm.errors.as_data()['__all__'][0])[0]
            })
                    
    
    return HttpResponseRedirect(reverse('index'))

@login_required
def my_calendar(request):
    myLessons = Lesson.objects.filter(climbers__in=[request.user])
    myClimbs = FreeClimb.objects.filter(climber = request.user)
    return render(request, "escalada/calendar.html",{
        "myLessons": myLessons,
        "myClimbs": myClimbs
    })

@login_required
def bookAClimb(request):
    bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
    return render(request, "escalada/bookAClimb.html", {
        "bookClimbForm": bookClimbForm
    })
    
@login_required
def bookingSubmitted(request):
    booking_form = FreeClimbFormClimber(request.POST)
    climbPassType = ClimbPassType(pk=request.POST.get('climbPassType'))
    coupon = Coupon(pk=request.POST.get('coupon'))
    date_ofClimb = request.POST.get('date')
    begin_time = request.POST.get('begin_time')
    begin_time = datetime.strptime(begin_time, '%H:%M:%S').time()
    if booking_form.is_valid():
        if request.method == 'POST':
            climber = request.user
            todays_climbs = FreeClimb.objects.filter(climber=climber, climbPassType=climbPassType, date=date_ofClimb)
            begin_time_plus = (datetime.combine(date(1,1,1),begin_time) + timedelta(hours=climbPassType.durationInHours)).time()
            begin_time_minus = (datetime.combine(date(1,1,1),begin_time) - timedelta(hours=climbPassType.durationInHours)).time()
            if todays_climbs.filter(begin_time = begin_time):
                bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
                return render(request, "escalada/bookAClimb.html", {
                "bookClimbForm": bookClimbForm,
                "error_message": f"Error: You have already booked for this hour."
                })
            # A climber can't book a climb that conflicts with another one
            elif todays_climbs.filter(begin_time__gt = begin_time) and todays_climbs.filter(begin_time__lte = begin_time_plus):
                bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
                return render(request, "escalada/bookAClimb.html", {
                "bookClimbForm": bookClimbForm,
                "error_message": f"Error: You can't book this climb, it starts just before the start of another climb you've already booked."
                })
            elif todays_climbs.filter(begin_time__lt = begin_time) and todays_climbs.filter(begin_time__gte = begin_time_minus):
                bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
                return render(request, "escalada/bookAClimb.html", {
                "bookClimbForm": bookClimbForm,
                "error_message": f"Error: You can't book this climb, it starts just after the start of another climb you've already booked."
                })
            else:
                newClimbBooked = FreeClimb(climber=climber, coupon = coupon,climbPassType=climbPassType, date=date_ofClimb, begin_time= begin_time)
                newClimbBooked.save()
                UseTicket(climber, coupon)
                return HttpResponseRedirect(reverse("index"))
            

def EnrollToLesson(climbClass, coupon, class_date,climber):
    # Check if the enrollment already exists:
    if Lesson.objects.filter(climbClass=climbClass, coupon=coupon, class_date=class_date).count() > 0:
        # If the class already exists, then the climber is added to that lesson:
        enrollment = Lesson.objects.get(climbClass=climbClass, coupon=coupon, class_date=class_date)
        enrollment.climbers.add(climber)
    else:
        # If not, then the lesson is created and the climber enrolled to it
        climbClass = ClimbClass.objects.get(pk=climbClass)
        coupon = Coupon.objects.get(pk=coupon)
        newEnrollment = Lesson(climbClass=climbClass, coupon=coupon, class_date=class_date)
        newEnrollment.save()
        newEnrollment.climbers.add(climber)


def UseTicket(climber, coupon):
    editMyCoupon = MyCoupon.objects.get(climber = climber, coupon=coupon)
    editMyCoupon.ticketsAvailable -= 1
    editMyCoupon.save()
    if editMyCoupon.ticketsAvailable <= 0:
        editMyCoupon.delete()
    