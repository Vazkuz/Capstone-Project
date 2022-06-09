from dataclasses import fields
from pyexpat import model
from django import forms
from django.core.exceptions import ValidationError
import datetime as dt
from .models import ClimbClass, Lesson, Coupon, MyCoupon

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
        numberOfLessonsPerWeek = len(cleaned_data.get('lessonDay'))
        if numberOfLessonsPerWeek != lessonsPerWeek:
            raise ValidationError(f"The number of lessons per week must be {lessonsPerWeek}")
        else:
            print("Lesson Day is not clean.")
            
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = '__all__'
        
    def clean(self):
        cleaned_data = super().clean()
        lessonDays = cleaned_data.get('climbClass').getLessonDays()
        maxNumberOfClimbers = cleaned_data.get('coupon').getMaxClimbers()
        
        ##################################### VALIDATIONS #####################################
        # The begin date has to be on a weekday of class
        if cleaned_data.get('begin_date').strftime('%A').upper() not in str(lessonDays).upper():
            raise ValidationError(f"Lesson days must be: {lessonDays}")
        
        # The begin date has to be set today or in the future, not in the past
        if cleaned_data.get('begin_date') < dt.date.today():
            raise ValidationError(f"Lessons can't be set in the past")
        
        # There can't be more climbers than the maximum set for the class type
        if cleaned_data.get('climbers'):
            if cleaned_data.get('climbers').count() > maxNumberOfClimbers:
                raise ValidationError(f"There can't be more than {maxNumberOfClimbers} climbers for this type of lesson.")
        
        # Type of class of both lesson and coupon must be the same
        if cleaned_data.get('climbClass').getClassType() != cleaned_data.get('coupon').getClassType():
            raise ValidationError(f'The type of the class does not match the type of the coupon selected.')
        #######################################################################################

class DateInput(forms.DateInput):
    input_type = 'date'

class LessonFormStudents(LessonForm):
    begin_date = forms.DateField(widget=DateInput)
    class Meta:
        model = Lesson
        exclude = ('climbers', 'class_date', )
        
    def __init__(self, user=None, **kwargs):
        super(LessonFormStudents, self).__init__(**kwargs)
        if user:
            self.fields['coupon'].queryset = Coupon.objects.filter(pk__in = MyCoupon.objects.filter(climber=user).values('coupon'))
        
class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        classType = cleaned_data.get('classType')
        climbPassType = cleaned_data.get('climbPassType')
        
        if classType is not None and climbPassType is not None:
            raise ValidationError(f"The coupon can't be for both a class and a climb pass. Choose one of them and leave the other null.")
        
        if classType is None and climbPassType is None:
            raise ValidationError(f"Both a class type and a climb pass type can't be null.")
        
class MyCouponForm(forms.ModelForm):
    class Meta:
        model = MyCoupon
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        numberOfClasses = cleaned_data.get('coupon').getNumberOfClasses()
        if not cleaned_data.get('coupon').is_Recurring() and numberOfClasses != cleaned_data.get('ticketsAvailable') and cleaned_data.get('recentlyBought'):
            raise ValidationError(f"For this climb pass the initial number of tickets must be {numberOfClasses}")
        
class BuyCouponForm(MyCouponForm):
    class Meta:
        model = MyCoupon
        exclude = ('climber', 'ticketsAvailable', 'recentlyBought', )
            