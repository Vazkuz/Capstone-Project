from xml.etree.ElementInclude import include
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createClass", views.createClass, name="createClass"),
    path("newClass", views.newClass, name="newClass"),
    path("enroll", views.enroll, name="enroll"),
    path("enroll_success", views.enroll_success, name="enroll_success"),
    path("buyCoupon", views.buyCoupon, name="buyCoupon"),
    path("buyCouponSubmit", views.buyCouponSubmit, name="buyCouponSubmit"),
    path("my_calendar", views.my_calendar, name="my_calendar"),
    path("bookAClimb", views.bookAClimb, name="bookAClimb"),
    path("bookingSubmitted", views.bookingSubmitted, name="bookingSubmitted"),
]
