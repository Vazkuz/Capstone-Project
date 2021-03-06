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
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("gymCalendar", views.gymCalendar, name="gymCalendar"),
    path("lesson/<int:lesson_id>", views.lesson_json, name="lesson"),
    path("climb/<int:climb_id>", views.climb_json, name="climb"),
    path("search", views.search, name="search"),
    path("manage_climber/<int:user_id>", views.manage_climber, name="manage_climber"),
    path("cancel_climb/<int:climb_id>", views.cancel_climb, name="cancel_climb"),
    path("postpone_lesson/<int:lesson_id>/<int:user_id>", views.postpone_lesson, name="postpone_lesson")
]
