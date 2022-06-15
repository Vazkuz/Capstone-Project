from dataclasses import fields
from pyexpat import model
from django import forms
from django.core.exceptions import ValidationError
import datetime as dt
from datetime import datetime, date, time, timedelta
from .models import ClimbClass, Lesson, Coupon, MyCoupon, FreeClimb, WeekdaySchedule

HOUR_CHOICES = [(dt.time(hour=x), '{:02d}:00'.format(x)) for x in range(0, 24)]
HOUR_CHOICES2 = [(dt.time(hour=x, minute=30), '{:02d}:30'.format(x)) for x in range(0, 24)]
HOUR_CHOICES3=[]
for i in range(len(HOUR_CHOICES)):
    HOUR_CHOICES3.append(HOUR_CHOICES[i])
    HOUR_CHOICES3.append(HOUR_CHOICES2[i]) 

class ClimbClassForm(forms.ModelForm):
    class Meta:
        model = ClimbClass
        exclude = ('end_time',)
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
        
    def __init__(self, *args,**kwargs):
        climberFilter = kwargs.pop('climberFilter', None)
        super(LessonFormStudents, self).__init__(*args, **kwargs)
        # Filter only the coupons the climber has
        if climberFilter:
            self.fields['coupon'].queryset = Coupon.objects.filter(pk__in = MyCoupon.objects.filter(climber=climberFilter).values('coupon'))
        
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

class FreeClimbForm(forms.ModelForm):
    class Meta:
        model = FreeClimb
        exclude = ('end_time',)
        widgets = {'begin_time': forms.Select(choices=HOUR_CHOICES3)}
    
    def clean(self):
        cleaned_data = super().clean()
        end_time_of_climb = (datetime.combine(date(1,1,1), cleaned_data.get('begin_time')) + timedelta(hours=cleaned_data.get('climbPassType').durationInHours)).time()
        weekday = cleaned_data.get('date').weekday()
        scheduleOfTheDay = WeekdaySchedule.objects.filter(weekday = weekday)

        ##################################### VALIDATIONS #####################################
        # The begin date has to be set today or in the future, not in the past
        if cleaned_data.get('date') < dt.date.today():
            raise ValidationError(f"You can't book a climb in the past.")
        
        # A Free climb can't be set on the closing hour of the gym or after that
        if scheduleOfTheDay.filter(closing_hour__lte = cleaned_data.get('begin_time')).count() == scheduleOfTheDay.filter(opening_hour__lte = cleaned_data.get('begin_time')).count():
            raise ValidationError(f"Can't set a climb after gym's closure")
        # A Free climb can't finish after the gym closes
        elif scheduleOfTheDay.filter(closing_hour__lte = end_time_of_climb).count() == scheduleOfTheDay.filter(opening_hour__lte = end_time_of_climb).count():
            raise ValidationError(f'This climb would at {end_time_of_climb}, after the gym had closed.')
        # else:
            
        # if scheduleOfTheDay.filter(closing_hour__lt = end_time_of_climb) or (scheduleOfTheDay.filter(closing_hour__gt = end_time_of_climb) and end_time_of_climb < cleaned_data.get('begin_time')):
        #######################################################################################

class FreeClimbFormClimber(FreeClimbForm):
    date = forms.DateField(widget=DateInput)
    class Meta:
        model = FreeClimb
        exclude = ('climber', 'end_time')
        widgets = {'begin_time': forms.Select(choices=HOUR_CHOICES3)}
        
    def __init__(self, *args,**kwargs):
        climberFilter = kwargs.pop('climberFilter', None)
        super(FreeClimbFormClimber, self).__init__(*args, **kwargs)
        # Filter only the coupons the climber has
        if climberFilter:
            self.fields['coupon'].queryset = Coupon.objects.filter(pk__in = MyCoupon.objects.filter(climber=climberFilter).values('coupon'))

class WeekdayScheduleForm(forms.ModelForm):
    class Meta:
        model = WeekdaySchedule
        fields = '__all__'