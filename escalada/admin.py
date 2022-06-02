from django.contrib import admin

from .models import User, ClassType, ClimbClass, Coupon, Enrollment
from .forms import ClimbClassForm


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'isInstructor')

class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'maxClimbers', 'onlyStaffEditable', 'durationInHours', 'isRecurring')

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(ClassType, ClassTypeAdmin)
admin.site.register(Coupon)
admin.site.register(Enrollment)
            

@admin.register(ClimbClass)
class ClimbClassAdmin(admin.ModelAdmin):
    form = ClimbClassForm
    list_display = ('id', 'classType', 'lessonDay')