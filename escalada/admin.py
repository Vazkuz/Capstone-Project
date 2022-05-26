from django.contrib import admin

from .models import User, ClassType, ClimbBooking

class ClimbBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'instructor', 'classType')

class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type')

# Register your models here.
admin.site.register(User)
admin.site.register(ClassType, ClassTypeAdmin)
admin.site.register(ClimbBooking, ClimbBookingAdmin)