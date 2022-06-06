from django.contrib import admin

from .models import User, ClassType, ClimbClass, Coupon, Enrollment
from .forms import ClimbClassForm, EnrollmentForm

def duplicate_event(modeladmin, request, queryset):
    for object in queryset:
        object.id = None
        object.save()
duplicate_event.short_description = "Duplicate selected record"

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'isInstructor')

class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'maxClimbers', 'onlyStaffEditable', 'durationInHours', 'isRecurring')

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(ClassType, ClassTypeAdmin)
admin.site.register(Coupon)
            

@admin.register(ClimbClass)
class ClimbClassAdmin(admin.ModelAdmin):
    form = ClimbClassForm
    list_display = ('id', 'classType', 'lessonDay')
    
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    form = EnrollmentForm
    list_display = ('id', 'coupon', 'class_date', 'climbClass')