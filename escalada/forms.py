from pyexpat import model
from django import forms
from django.core.exceptions import ValidationError
import datetime as dt
from .models import ClimbClass, Enrollment

HOUR_CHOICES = [(dt.time(hour=x), '{:02d}:00'.format(x)) for x in range(0, 24)]
HOUR_CHOICES2 = [(dt.time(hour=x, minute=30), '{:02d}:30'.format(x)) for x in range(0, 24)]
HOUR_CHOICES3=[]
for i in range(len(HOUR_CHOICES)):
    HOUR_CHOICES3.append(HOUR_CHOICES[i])
    HOUR_CHOICES3.append(HOUR_CHOICES2[i]) 

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

        if cleaned_data.get('lessonDay') or is_Recurring:
            if numberOfLessonsPerWeek != lessonsPerWeek and is_Recurring:
                raise ValidationError(f"The number of lessons per week must be {lessonsPerWeek}")
        else:
            print("Lesson Day is not clean.")
            
class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = '__all__'
        
    def clean(self):
        cleaned_data = super().clean()
        lessonDays = cleaned_data.get('climbClass').getLessonDays()
        maxNumberOfClimbers = cleaned_data.get('coupon').getMaxClimbers()
        
        ##################################### VALIDATIONS #####################################
        # The begin date has to be on a weekday of class
        if cleaned_data.get('begin_date').strftime('%A').upper() not in str(lessonDays).upper():
            raise ValidationError(f"The begin date of the class must be: {lessonDays}")
        
        # # The class dates have to be on a weekday of class
        # if cleaned_data.get('class_date').strftime('%A').upper() not in str(lessonDays).upper():
        #     raise ValidationError(f"Class dates must be: {lessonDays}")
        
        # The begin date has to be set today or in the future, not in the past
        if cleaned_data.get('begin_date') < dt.date.today():
            raise ValidationError(f"The begin date can't be in the past")
        
        # # The class dates have to be the begin date or days after that
        # if cleaned_data.get('class_date') < cleaned_data.get('begin_date'):
        #     raise ValidationError(f"Class dates have to be the begin date or after.")
        
        # There can't be more climbers than the maximum set for the class type
        if cleaned_data.get('climbers'):
            if cleaned_data.get('climbers').count() > maxNumberOfClimbers:
                raise ValidationError(f"There can't be more than {maxNumberOfClimbers} climbers for this type of lesson.")
            
        if cleaned_data.get('climbClass').getClassType() != cleaned_data.get('coupon').getClassType():
            raise ValidationError(f'The type of the class does not coincide with the type of the coupon selected.')
        #######################################################################################

class DateInput(forms.DateInput):
    input_type = 'date'

class EnrollmentFormStudents(EnrollmentForm):
    begin_date = forms.DateField(widget=DateInput)
    class Meta:
        model = Enrollment
        exclude = ('climbers', 'class_date', )
