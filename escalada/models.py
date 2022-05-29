from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class ClassType(models.Model):
    type = models.CharField(max_length=64)
    
    def __str__(self):
        return self.type
    
class ClimbClass(models.Model):
    classType = models.ForeignKey(ClassType, on_delete=models.SET_NULL, null=True, related_name= "class_type")
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="class_instructor")
    date = models.DateTimeField()
    seatsAvailable = models.IntegerField(default=0)
    isAvailable = models.BooleanField(default=True)
    
class Post(models.Model):
    text = models.CharField(max_length=500)