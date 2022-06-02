from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms

from .models import User, ClassType, ClimbClass, Coupon
import datetime as dt

HOUR_CHOICES = [(dt.time(hour=x), '{:02d}:00'.format(x)) for x in range(0, 24)]
HOUR_CHOICES2 = [(dt.time(hour=x, minute=30), '{:02d}:30'.format(x)) for x in range(0, 24)]
HOUR_CHOICES3=[]
for i in range(len(HOUR_CHOICES)):
    HOUR_CHOICES3.append(HOUR_CHOICES[i])
    HOUR_CHOICES3.append(HOUR_CHOICES2[i]) 


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'isInstructor')

class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'maxClimbers', 'onlyStaffEditable', 'durationInHours', 'isRecurring')

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(ClassType, ClassTypeAdmin)
admin.site.register(Coupon)

class ClimbClassForm(forms.ModelForm):
    class Meta:
        model = ClimbClass
        fields = '__all__'
        widgets = {'begin_time': forms.Select(choices=HOUR_CHOICES3)}

    def clean(self):
        cleaned_data = super().clean()
        lessonsPerWeek = cleaned_data.get('classType').getLessonsPerWeek()
        is_Recurring = cleaned_data.get('classType').is_Recurring()
        numberOfLessonsPerWeek = len(cleaned_data.get('lessonDay'))
        
        # if cleaned_data.get('climbers'):
        #     if cleaned_data.get('climbers').count() > maxClimbers:
        #         raise ValidationError(f"There can't be more than {maxClimbers} climbers for this type of lesson.")

        if cleaned_data.get('lessonDay') or is_Recurring:
            if numberOfLessonsPerWeek != lessonsPerWeek and is_Recurring:
                print("DEBERÍA LLEGA AQUÍ")
                raise ValidationError(f"The number of lessons per week must be {lessonsPerWeek}")
        else:
            print("Lesson Day is not clean.")
            

@admin.register(ClimbClass)
class ClimbClassAdmin(admin.ModelAdmin):
    form = ClimbClassForm
    list_display = ('id', 'classType', 'lessonDay')