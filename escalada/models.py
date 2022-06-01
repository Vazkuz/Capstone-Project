from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime, date
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
    # startHour = models.IntegerField(default=36,
    #     validators=[
    #         MaxValueValidator(0),
    #         MinValueValidator(47)
    #     ]) # startHour is something between 0 and 47. The real hour is half startHour: 0 is 00:00h, 1 is 00:30h, 2 is 01:00h and so on...

    
class Post(models.Model):
    text = models.CharField(max_length=500)