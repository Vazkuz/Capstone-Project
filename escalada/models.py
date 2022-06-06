from pyexpat import model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime, date, time
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
    isRecurring = models.BooleanField(default=False)
    
    def __str__(self):
        return self.type
    
    def getMaxClimbers(self):
        return self.maxClimbers
    
    def getLessonsPerWeek(self):
        return self.lessonsPerWeek
    
    def is_Recurring(self):
        return self.isRecurring
    
class ClimbClass(models.Model):
    classType = models.ForeignKey(ClassType, on_delete=models.CASCADE, null=True, related_name= "class_type")
    lessonDay = MultiSelectField(choices = LessonDay, blank=True)
    begin_time = models.TimeField(default=time(00, 00))
    
    def __str__(self):
        return f'{self.classType} at {self.begin_time} ({self.lessonDay})'
    
    def getLessonDays(self):
        return self.lessonDay
    
    def getClassType(self):
        return self.classType
    
class Coupon(models.Model):
    classType = models.ForeignKey(ClassType, on_delete=models.CASCADE)
    numberOfWeeks = models.IntegerField(default=4,
        validators=[
            MinValueValidator(1)
        ])
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def getClassType(self):
        return self.classType
    
    def getMaxClimbers(self):
        return self.classType.getMaxClimbers()
    
    def getNumberOfClasses(self):
        return self.numberOfWeeks
    
    def __str__(self):
        return f'{self.numberOfWeeks} ({self.classType}) at {self.price} soles'
    
class Enrollment(models.Model):
    climbers = models.ManyToManyField(User)
    climbClass = models.ForeignKey(ClimbClass, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    class_date = models.DateField(default=date.today)
    
    def getClimbClass(self):
        return self.climbClass
    
class Post(models.Model):
    text = models.CharField(max_length=500)