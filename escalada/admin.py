from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms

from .models import User, ClassType, ClimbClass

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'isInstructor')

class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'isRecurring')

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(ClassType, ClassTypeAdmin)

class ClimbClassForm(forms.ModelForm):
    class Meta:
        model = ClimbClass
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        maxClimbers = cleaned_data.get('classType').getMaxClimbers()
        lessonsPerWeek = cleaned_data.get('classType').getLessonsPerWeek()
        is_Recurring = cleaned_data.get('classType').is_Recurring()
        numberOfLessonsPerWeek = len(cleaned_data.get('lessonDay'))
        
        if cleaned_data.get('climbers'):
            if cleaned_data.get('climbers').count() > maxClimbers:
                raise ValidationError(f"There can't be more than {maxClimbers} climbers for this type of lesson.")

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