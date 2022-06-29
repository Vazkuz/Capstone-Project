from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from .models import ClassType, ClimbClass, ClimbPassType, Coupon, FreeClimb, Lesson, MyCoupon, User
from .forms import ClimbClassForm, LessonFormStudents, BuyCouponForm, MyCouponForm, FreeClimbFormClimber, SearchForm, PostponeLessonForm
from datetime import datetime, date, time, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.db.models import Q

# Create your views here.
def index(request):
    availableClasses = ClimbClass.objects.filter(is_Available = True)
    return render(request, "escalada/index.html", {
        "availableClasses": availableClasses,
        "form": SearchForm()
    })

@staff_member_required(login_url=reverse_lazy('index'))
def createClass(request):
    newClassForm = ClimbClassForm()
    return render(request, "escalada/create_class.html", {
        "newClassForm": newClassForm,
        "errorInCreation": False,
        "form": SearchForm()
    })
    
@staff_member_required(login_url=reverse_lazy('index'))
def newClass(request):
    class_form = ClimbClassForm(request.POST)
    if request.method == 'POST':
        classType = ClassType.objects.get(pk=request.POST["classType"])
        lessonDay = request.POST.getlist('lessonDay')
        begin_time = datetime.strptime(request.POST.get('begin_time'), '%H:%M:%S').time()
        if len(lessonDay) > 0:
            newClass = ClimbClass(classType=classType, lessonDay=lessonDay, begin_time=begin_time)
        else:
            newClass = ClimbClass(classType=classType, begin_time=begin_time)
            
        if class_form.is_valid():
            newClass.save()
        else:
            return render(request, "escalada/error_in_newclass.html", {
                "form": SearchForm()
            })
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
        "enroll_form": enroll_form,
        "form": SearchForm()
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
            # Check if the climber has the coupon
            try:
                MyCoupon.objects.get(climber = climber, coupon=coupon)
            except ObjectDoesNotExist:
                # If not, tell them
                enroll_form = LessonFormStudents(climberFilter=request.user)
                return render(request, "escalada/enroll.html", {
                    "enroll_form": enroll_form,
                    "error_message": f"Error: You don't have a coupon for that class",
                    "form": SearchForm()
                })
                
        render_v = CheckAvailAndEnroll(request, numberOfLessons, lessonDays, begin_date_DF, climber, climbClass, coupon)
        
        return render_v

    enroll_form = LessonFormStudents(climberFilter=request.user)
    return render(request, "escalada/enroll.html", {
        "enroll_form": enroll_form,
        "error_message": "Error: " + list(class_form.errors.as_data()['__all__'][0])[0],
        "form": SearchForm()
    })

@staff_member_required(login_url=reverse_lazy('index'))
def postpone_lesson(request, lesson_id, user_id):
    if request.method == 'POST':
        postpone_lesson = PostponeLessonForm(request.POST)
        if postpone_lesson.is_valid():
            new_begin_date = postpone_lesson.cleaned_data['begin_date']
            new_begin_date_DF = datetime.strptime(new_begin_date, '%Y-%m-%d')
            profile_user = User.objects.get(pk=user_id)
            current_class_date = Lesson.objects.get(pk=lesson_id).class_date
            climbClass = Lesson.objects.get(pk=lesson_id).climbClass
            next_lessons = Lesson.objects.filter(climbers__in = [profile_user], class_date__gte = current_class_date, climbClass = climbClass).order_by('class_date')
            # render = CheckAvailAndEnroll(request, next_lessons.count(), lessonDays, new_begin_date_DF, profile_user, climbClass, coupon)
    
    
    # for i in range(len(next_lessons)):
    #     if i > 0:
    #         next_lessons[i].climbers.remove(profile_user)

    print("____________________________________________________________________________")
    print(next_lessons)
    print(next_lessons[0].climbers.all().count())
    print(next_lessons.count())
    print("____________________________________________________________________________")
    # next_lessons.first().climbers.remove(profile_user)
    return HttpResponseRedirect(reverse('manage_climber', args=(user_id, ))) 

def CheckAvailAndEnroll(request, numberOfLessons, lessonDays, begin_date_DF, climber, climbClass, coupon):
    # First check class availability (by number of students)
            availability = 0
            isClimberOnClass = 0
            climbClass_CLASS = ClimbClass.objects.filter(pk=climbClass)
            begin_time = climbClass_CLASS.values('begin_time')[0]['begin_time']
            durationInHours = ClassType.objects.filter(pk__in=climbClass_CLASS.values('classType')).values('durationInHours')[0]['durationInHours']
            begin_time_plus = (datetime.combine(date(1,1,1),begin_time) + timedelta(hours=durationInHours)).time()
            begin_time_minus = (datetime.combine(date(1,1,1),begin_time) - timedelta(hours=durationInHours)).time()            

            for i in range(numberOfLessons):
                for j in range(7):
                    newDay = begin_date_DF + timedelta(days=i*7+j)
                    if newDay.strftime('%A').upper() in str(lessonDays).upper():
                        todays_climbs = FreeClimb.objects.filter(climber=climber, date=newDay)
                        if todays_climbs.count() > 0:
                            if todays_climbs.filter(begin_time = begin_time):
                                enroll_form = LessonFormStudents(climberFilter=climber)
                                return render(request, "escalada/enroll.html", {
                                    "enroll_form": enroll_form,
                                    "error_message": f"Error: You have a climb booked that conflicts with this class. Check your calendar.",
                                    "form": SearchForm()
                                })
                            elif todays_climbs.filter(begin_time__gt = begin_time) and todays_climbs.filter(begin_time__lt = begin_time_plus):
                                enroll_form = LessonFormStudents(climberFilter=climber)
                                return render(request, "escalada/enroll.html", {
                                    "enroll_form": enroll_form,
                                    "error_message": f"Error: You have a climb booked that conflicts with this class. Check your calendar.",
                                    "form": SearchForm()
                                })
                            elif todays_climbs.filter(begin_time__lt = begin_time) and todays_climbs.filter(begin_time__gt = begin_time_minus):
                                enroll_form = LessonFormStudents(climberFilter=climber)
                                return render(request, "escalada/enroll.html", {
                                    "enroll_form": enroll_form,
                                    "error_message": f"Error: You have a climb booked that conflicts with this class. Check your calendar.",
                                    "form": SearchForm()
                                })
                        if Lesson.objects.filter(climbClass=climbClass, coupon=coupon, class_date=newDay).count() > 0:
                            enrollment = Lesson.objects.get(climbClass=climbClass, coupon=coupon, class_date=newDay)
                            if Lesson.objects.filter(climbClass=climbClass, coupon=coupon, class_date=newDay,climbers__in = [climber]).count() > 0:
                                isClimberOnClass += 1
                            if enrollment.climbers.all().count() >= enrollment.getClimbClass().getClassType().getMaxClimbers():
                                newDayClass = newDay.strftime("%d/%m/%Y")
                                availability += 1
            # If isClimberOnClass > 0, that means the climber is already on that class for at least one of the days they are trying to enroll
            if isClimberOnClass > 0:
                enroll_form = LessonFormStudents(climberFilter=climber)
                return render(request, "escalada/enroll.html", {
                    "enroll_form": enroll_form,
                    "error_message": f"Error: You are already on that class",
                    "form": SearchForm()
                })
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
            enroll_form = LessonFormStudents(climberFilter=climber)
            return render(request, "escalada/enroll.html", {
                "enroll_form": enroll_form,
                "error_message": f"Error: Class is full until {newDayClass}",
                "form": SearchForm()
            })
            
@login_required
def buyCoupon(request):
    buyForm = BuyCouponForm()
    return render(request, "escalada/buy_coupon.html", {
        "buyForm": buyForm,
        "form": SearchForm()
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
                "error_message": "You already have that Coupon",
                "form": SearchForm()
            })
        else:                    
            return render(request, "escalada/buy_coupon.html", {
                "buyForm": buyForm,
                "error_message": "Error: " + list(myCouponForm.errors.as_data()['__all__'][0])[0],
                "form": SearchForm()
            })
                    
    
    return HttpResponseRedirect(reverse('index'))

@login_required
def my_calendar(request):
    myLessons = Lesson.objects.filter(climbers__in=[request.user])
    myClimbs = FreeClimb.objects.filter(climber = request.user)
    return render(request, "escalada/calendar.html",{
        "myLessons": myLessons,
        "myClimbs": myClimbs,
        "form": SearchForm()
    })

@login_required
def bookAClimb(request):
    bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
    return render(request, "escalada/bookAClimb.html", {
        "bookClimbForm": bookClimbForm,
        "form": SearchForm()
    })
    
@login_required
def bookingSubmitted(request):
    booking_form = FreeClimbFormClimber(request.POST)
    climbPassType = ClimbPassType.objects.filter(pk=request.POST.get('climbPassType'))
    climbPassType_instance = climbPassType.get(pk=request.POST.get('climbPassType'))
    durationInHours = climbPassType_instance.durationInHours
    maxClimbersForPassType = climbPassType_instance.maxClimbers
    coupon = Coupon(pk=request.POST.get('coupon'))
    date_ofClimb = request.POST.get('date')
    begin_time = request.POST.get('begin_time')
    begin_time = datetime.strptime(begin_time, '%H:%M:%S').time()
    if booking_form.is_valid():
        if request.method == 'POST':
            climber = request.user
            my_climbs_today = FreeClimb.objects.filter(climber=climber, climbPassType__in=climbPassType, date=date_ofClimb)
            my_lessons_today = Lesson.objects.filter(climbers__in = [climber], class_date = date_ofClimb)
            my_lessons_today_bt = ClimbClass.objects.filter(pk__in=my_lessons_today.values('climbClass')).values('begin_time')
            begin_time_plus = (datetime.combine(date(1,1,1),begin_time) + timedelta(hours=durationInHours)).time()
            begin_time_minus = (datetime.combine(date(1,1,1),begin_time) - timedelta(hours=durationInHours)).time()
            
            todays_climbs = FreeClimb.objects.filter(climbPassType__in=climbPassType, date=date_ofClimb)
            possible_conflicts = todays_climbs.filter(begin_time__gt=begin_time_plus, end_time__lt=begin_time)
            if possible_conflicts:
                if possible_conflicts.count() >= maxClimbersForPassType:
                    bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
                    return render(request, "escalada/bookAClimb.html", {
                    "bookClimbForm": bookClimbForm,
                    "error_message": f"Error: You can't book this climb because this hour is full (there are {maxClimbersForPassType} climbers).",
                    "form": SearchForm()
                    })
            if my_climbs_today.filter(begin_time = begin_time):
                bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
                return render(request, "escalada/bookAClimb.html", {
                "bookClimbForm": bookClimbForm,
                "error_message": f"Error: You have already booked for this hour.",
                "form": SearchForm()
                })
            # A climber can't book a climb that conflicts with another free climb
            elif my_climbs_today.filter(begin_time__gt = begin_time) and my_climbs_today.filter(begin_time__lt = begin_time_plus):
                bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
                return render(request, "escalada/bookAClimb.html", {
                "bookClimbForm": bookClimbForm,
                "error_message": f"Error: You can't book this climb, it starts just before the start of another climb you've already booked.",
                "form": SearchForm()
                })
            elif my_climbs_today.filter(begin_time__lt = begin_time) and my_climbs_today.filter(begin_time__gt = begin_time_minus):
                bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
                return render(request, "escalada/bookAClimb.html", {
                "bookClimbForm": bookClimbForm,
                "error_message": f"Error: You can't book this climb, it starts just after the start of another climb you've already booked.",
                "form": SearchForm()
                })
            # Prevent conflicts: free climbs cannot conflict with classes
            elif my_lessons_today_bt.filter(begin_time = begin_time):
                bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
                return render(request, "escalada/bookAClimb.html", {
                "bookClimbForm": bookClimbForm,
                "error_message": f"Error: You can't book this climb because it conflicts with a class you are enrolled in.",
                "form": SearchForm()
                })
            elif my_lessons_today_bt.filter(begin_time__gt = begin_time) and my_lessons_today_bt.filter(begin_time__lt = begin_time_plus):
                bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
                return render(request, "escalada/bookAClimb.html", {
                "bookClimbForm": bookClimbForm,
                "error_message": f"Error: You can't book this climb because it conflicts with a class you are enrolled in.",
                "form": SearchForm()
                })
            elif my_lessons_today_bt.filter(begin_time__lt = begin_time) and my_lessons_today_bt.filter(begin_time__gt = begin_time_minus):
                bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
                return render(request, "escalada/bookAClimb.html", {
                "bookClimbForm": bookClimbForm,
                "error_message": f"Error: You can't book this climb because it conflicts with a class you are enrolled in.",
                "form": SearchForm()
                })
            else:                
                # Check if the climber has the coupon
                try:
                    MyCoupon.objects.get(climber = climber, coupon=coupon)
                except ObjectDoesNotExist:
                    # If not, tell them
                    bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
                    return render(request, "escalada/bookAClimb.html", {
                        "bookClimbForm": bookClimbForm,
                        "error_message": f"Error: You don't have a coupon for that climb",
                        "form": SearchForm()
                    })
                    
                newClimbBooked = FreeClimb(climber=climber, coupon = coupon, climbPassType=climbPassType_instance, date=date_ofClimb, begin_time= begin_time)
                newClimbBooked.save()
                UseTicket(climber, coupon)
                return HttpResponseRedirect(reverse("index"))
    bookClimbForm = FreeClimbFormClimber(climberFilter=request.user)
    return render(request, "escalada/bookAClimb.html", {
        "bookClimbForm": bookClimbForm,
        "error_message": "Error: " + list(booking_form.errors.as_data()['__all__'][0])[0],
        "form": SearchForm()
    })

@login_required
def profile(request, user_id):
    if user_id == request.user.id or request.user.is_superuser:
        is_my_profile = True
        if user_id != request.user.id:
            is_my_profile = False
        profile_user = User.objects.get(pk=user_id)
        myLessons = Lesson.objects.filter(climbers__in = [profile_user], class_date__gte = datetime.today())
        myEnrollments_list = ClimbClass.objects.filter(pk__in = myLessons.values('climbClass').distinct())
        remaining_classes = myLessons.values('climbClass').annotate(Count('climbClass'))
        myEnrollments = zip(myEnrollments_list, remaining_classes)
        nextLesson = myLessons.order_by("class_date").first()
        myCoupons = MyCoupon.objects.filter(climber = user_id)
        return render(request, "escalada/profile.html", {
            "profile_user": profile_user,
            "myCoupons": myCoupons,
            "nextLesson": nextLesson,
            "myEnrollments": myEnrollments,
            "myEnrollments_length": len(myEnrollments_list),
            "is_my_profile": is_my_profile,
            "form": SearchForm()
        })
    else:
        return HttpResponseRedirect(reverse('index'))
    
@staff_member_required(login_url=reverse_lazy('index'))
def gymCalendar(request):
    # Free climbs:
    climbs = FreeClimb.objects.all()
    
    # Lessons
    lessons = Lesson.objects.all()
    gymCalendar = True
    return render(request, "escalada/calendar.html",{
        "myLessons": lessons,
        "myClimbs": climbs,
        "gymCalendar": gymCalendar,
        "form": SearchForm()
    })
      
@staff_member_required(login_url=reverse_lazy('index'))
def lesson_json(request, lesson_id):
    data=Lesson.objects.get(pk=lesson_id).serialize()
    if request.method == 'GET':
        return JsonResponse(data)
  
@staff_member_required(login_url=reverse_lazy('index'))
def climb_json(request, climb_id):
    data=FreeClimb.objects.get(pk=climb_id).serialize()
    if request.method == 'GET':
        return JsonResponse(data)

@staff_member_required(login_url=reverse_lazy('index'))
def search(request):
    if request.method == "POST":
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search = search_form.cleaned_data["searchBox"]
            fn_search = search.split(' ', 1)[0]
            try:
                ln_search = search.split(' ', 1)[1]
            except IndexError:
                ln_search = '///////ººººº+++++'
            results = User.objects.filter(Q(username__icontains = search) 
                                          | Q(first_name__icontains = search) 
                                          | Q(last_name__icontains = search) 
                                          | Q(first_name__icontains = fn_search) 
                                          | Q(last_name__icontains = ln_search))
            return render(request, 'escalada/search_climber.html', {
                "search": search,
                "results": results,
                "form": SearchForm()
            })
        return HttpResponseRedirect(reverse('index'))
    return HttpResponseRedirect(reverse('index'))

@staff_member_required(login_url=reverse_lazy('index'))
def manage_climber(request, user_id):
    profile_user = User.objects.get(pk=user_id)
    future_climbs = FreeClimb.objects.filter(climber=user_id, date__gte = datetime.today())
    future_lessons = Lesson.objects.filter(climbers__in = [profile_user], class_date__gte = datetime.today()).order_by('class_date')
    return render(request, 'escalada/manage_climber.html', {
        "future_climbs":future_climbs,
        "profile_user": profile_user,
        "future_lessons": future_lessons,
        "new_date_form": PostponeLessonForm(),
        "form": SearchForm()
    })

@staff_member_required(login_url=reverse_lazy('index'))
def cancel_climb(request, climb_id):
    climb = FreeClimb.objects.get(pk=climb_id)
    climber_id_number = climb.climber_id
    climber_id = User.objects.get(pk=climb.climber_id)
    try:
        myCoupon = MyCoupon.objects.get(climber=climber_id, coupon=climb.coupon)
    except ObjectDoesNotExist:
        myCoupon = MyCoupon(climber=climber_id, coupon=climb.coupon, ticketsAvailable=0)
    myCoupon.ticketsAvailable += 1
    myCoupon.save()
    FreeClimb.objects.get(pk=climb_id).delete()
    return HttpResponseRedirect(reverse('manage_climber', args=(climber_id_number, )))

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
