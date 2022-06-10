from django.contrib import admin

from .models import User, ClassType, ClimbClass, Coupon, Lesson, MyCoupon, ClimbPassType
from .forms import ClimbClassForm, LessonForm, CouponForm, MyCouponForm

def duplicate_event(modeladmin, request, queryset):
    for object in queryset:
        object.id = None
        object.save()
duplicate_event.short_description = "Duplicate selected record"

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'isInstructor')

class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'maxClimbers', 'onlyStaffEditable', 'durationInHours')

class ClimbPassTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'maxClimbers', 'onlyStaffEditable', 'durationInHours')

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(ClassType, ClassTypeAdmin)
admin.site.register(ClimbPassType, ClimbPassTypeAdmin)
            

@admin.register(ClimbClass)
class ClimbClassAdmin(admin.ModelAdmin):
    form = ClimbClassForm
    list_display = ('id', 'classType', 'lessonDay', 'begin_time', 'end_time', 'is_Available')
    
@admin.register(Lesson)
class EnrollmentAdmin(admin.ModelAdmin):
    form = LessonForm
    list_display = ('id', 'coupon', 'class_date', 'climbClass')
    
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    form = CouponForm
    list_display = ('id', 'classType', 'climbPassType', 'numberOfWeeks', 'price')

@admin.register(MyCoupon)
class MyCouponAdmin(admin.ModelAdmin):
    form = MyCouponForm
    list_display = ('id', 'climber', 'coupon', 'ticketsAvailable')
    