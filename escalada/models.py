from pyexpat import model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime, date, time, timedelta
from multiselectfield import MultiSelectField

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

LessonDay = (
    (MONDAY, 'Monday'),
    (TUESDAY, 'Tuesday'),
    (WEDNESDAY, 'Wednesday'),
    (THURSDAY, 'Thursday'),
    (FRIDAY, 'Friday'),
    (SATURDAY, 'Saturday'),
    (SUNDAY, 'Sunday'),
)

class DayOfTheWeekField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices']=LessonDay
        kwargs['max_length']=1 
        super(DayOfTheWeekField,self).__init__(*args, **kwargs)

class User(AbstractUser):
    isInstructor = models.BooleanField(default=False)

class ClassType(models.Model):
    type = models.CharField(max_length=64)
    lessonsPerWeek = models.IntegerField(default=1,
        validators=[
            MaxValueValidator(7),
            MinValueValidator(1)
        ])
    maxClimbers = models.IntegerField(default=1)
    onlyStaffEditable = models.BooleanField(default=True)
    durationInHours = models.IntegerField(default=2)
    
    def __str__(self):
        return self.type
    
    def getMaxClimbers(self):
        return self.maxClimbers
    
    def getLessonsPerWeek(self):
        return self.lessonsPerWeek

class ClimbPassType(models.Model):
    type = models.CharField(max_length=64)
    maxClimbers = models.IntegerField(default=1)
    onlyStaffEditable = models.BooleanField(default=True)
    durationInHours = models.IntegerField(default=2)
    
    def __str__(self):
        return self.type
    
    def getMaxClimbers(self):
        return self.maxClimbers
    
    def getLessonsPerWeek(self):
        return self.lessonsPerWeek
    
class ClimbClass(models.Model):
    classType = models.ForeignKey(ClassType, on_delete=models.CASCADE, null=True, related_name= "class_type")
    lessonDay = MultiSelectField(choices = LessonDay, blank=True)
    begin_time = models.TimeField(default=time(00, 00))
    end_time = models.TimeField()
    is_Available = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.classType} at {self.begin_time} ({self.lessonDay})'
    
    def save(self, *args, **kwargs):
        self.end_time = (datetime.combine(date(1,1,1),self.begin_time) + timedelta(hours=self.classType.durationInHours)).time()
        super().save(*args, **kwargs)
    
    def getLessonDays(self):
        return self.lessonDay
    
    def getClassType(self):
        return self.classType
    
class Coupon(models.Model):
    classType = models.ForeignKey(ClassType, on_delete=models.CASCADE, null=True, blank=True)
    climbPassType = models.ForeignKey(ClimbPassType, on_delete=models.CASCADE, null=True, blank=True)
    numberOfWeeks = models.IntegerField(default=4,
        validators=[
            MinValueValidator(0)
        ])
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def getClassType(self):
        return self.classType
    
    def getclimbPassType(self):
        return self.climbPassType
    
    def getMaxClimbers(self):
        if self.classType is not None:
            return self.classType.getMaxClimbers()
        else:
            return self.climbPassType.getMaxClimbers()
    
    def getNumberOfClasses(self):
        return self.numberOfWeeks
    
    def is_Recurring(self):
        if self.classType is None:
            return False
        else:
            return True
    
    def __str__(self):
        if self.classType is None:
            return f'{self.numberOfWeeks} climb pass at {self.price} soles ({self.climbPassType})'
        return f'{self.numberOfWeeks} weeks at {self.price} soles ({self.classType})'
    
class Lesson(models.Model):
    climbers = models.ManyToManyField(User, related_name="students")
    climbClass = models.ForeignKey(ClimbClass, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    class_date = models.DateField(default=date.today)
    
    def getClimbClass(self):
        return self.climbClass
    
    def serialize(self):
        climbers_list = list(self.climbers.values('id', 'username', 'first_name', 'last_name'))
        climbers_dict = dict(zip(range(len(climbers_list)), climbers_list))
        lessonDays = ""
        for day in self.climbClass.lessonDay:
            lessonDays += f"{LessonDay[int(day)][1]}, "
        lessonDays = lessonDays[:-2]
        return{
            "id": self.id,
            "begin_time": self.climbClass.begin_time.strftime("%I:%M %p"),
            "end_time": self.climbClass.end_time.strftime("%I:%M %p"),
            "class_date": self.class_date.strftime("%b %d, %Y"),
            "climbers": climbers_dict,
            "lessonDays": lessonDays,
            "durationInHours": self.climbClass.classType.durationInHours
        }
    
class FreeClimb(models.Model):
    climber = models.ForeignKey(User, related_name="freeClimber", on_delete=models.CASCADE)
    climbPassType = models.ForeignKey(ClimbPassType, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    begin_time = models.TimeField(default=time(00, 00))
    end_time = models.TimeField(default=time(2, 00))
    
    def save(self, *args, **kwargs):
        self.end_time = (datetime.combine(date(1,1,1),self.begin_time) + timedelta(hours=self.climbPassType.durationInHours)).time()
        super().save(*args, **kwargs)
    
    def getclimbPassType(self):
        return self.climbPassType
    
    def __str__(self):
        return f'{self.climbPassType} climb for {self.climber} {self.date} from {self.begin_time} to {self.end_time}'
    
    
class MyCoupon(models.Model):
    climber = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    ticketsAvailable = models.IntegerField(
        validators=[
            MinValueValidator(0)
        ])
    recentlyBought = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_relationships",
                fields=["climber", "coupon"],
            )
        ]
    
    def UseTicket(self):
        self.ticketsAvailable -= 1
        
class WeekdaySchedule(models.Model):
    weekday = models.IntegerField(choices=LessonDay,default=0)
    opening_hour = models.TimeField(default=time(00, 00))
    closing_hour = models.TimeField(default=time(23, 59))
    
class Post(models.Model):
    text = models.CharField(max_length=500)

# USAR ESTO PARA GUARDAR TODOS LOS INGRESOS DEL GIMNASIO
class Income(models.Model):
    climber = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    concept = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)