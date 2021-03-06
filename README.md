# Capstone-Project
In this capstone project I develop a web page for a climbing gym here in Lima, Perú. This web app is going to be used by climbers to enroll in classes, book climbs, check their calendars, and more.

# Distinctiveness and Complexity
## Distinctiveness
This project is different than any other because it is an app for managing a climbing gym. It has calendars, classes, free climbs, etc. that no other project performed had.

## Complexity
It uses Django with several models as well as JS to manage things like the navigation bar, creating and enrolling to classes, etc. It is also mobile-responsive

# Views.py
## index view:
Main page. Users can check the classes available and enroll in them. They have other buttons such as:
- My Calendar: check upcoming classes in a calendar as well as climbs booked
- My Classes: check classes enrolled
- My Coupons: coupons already bought
- Enroll: allows users enroll to classes using already bought coupons
- Buy a coupon: allows users to buy coupons to enroll to a class and/or book a climb

## createClass/newClass view:
If the user is logged in AND it is an admin (staff), then they will have the ability to create new climbing classes using this view. Non-admin users cannot create new climbing classes
but they can enroll in them (if they are available).

## login_view/logout_view/register views:
Login / logout / register functionalities

## enroll/enroll_success views:
Views that allow users enroll to lessons. Coupons are needed to enroll.

## buyCoupon/buyCouponSubmit views:
Views that allow users to buy coupons that will be used to enroll classes.

## Postpone_lesson / cancel_climb views:
Admins use these views to postpone classes for students or cancel climbs.

## Profile view
Users' profile. It displays info regarding their classes and coupons

## Gym Calendar view
Calendar that displays all climbers classes and climbs. It is only available for admins.

## Climb_json view
Displays climb json serialized

## Lesson_json view
Displays lesson json serialized

## Search view
Admins can use this view to search for other climbers

## Manage_climber view
Admins can use this view to postpone classes or cancel climbs for climbers.

## EnrollToLesson function:
Function that creates the lesson in the database.

## UseTicket function:
Function that takes the coupon used by the user and substract 1 to the ticketsAvailable variable. If ticketsAvailable is equal to 0 that means the user has used all their passes from that coupon, so the coupon is deleted from the user

# Models.py
## LessonDay
Utility for weekdays

## DayOfTheWeekField model
Model utility to use a weekday in other classes.

## User model
Users. They can also be instructors.

## ClassType model
Main type of classes: they may be 2/week classes, 1/week classes, etc.

## ClimbPassType model
Main type of passes: 1 time-use-only pass, 10 times-use pass...

## ClimbClass model
Specific class that is created using a classtype. For example, a climbclass can be of type 1/week starting at 6:30pm on Fridays, while other can be of 1/week type but start at 8:30pm on Tuesday. They can be available or not.

## Coupon model
A coupon is used to enroll in a class or to book a climb. They have different prices and are used to enroll/book different types of classes/climbs.

## Lesson model
A lesson is the instance of a ClimbClass. It has students and dates. For instance, while a climbclass can be of type 1/week starting at 6:30pm on Fridays, if no student is yet enrolled in that class, then the lesson isn't created. Once the lesson is created, it has students and dates: for instance a climber "Harry" has enrolled in a 1/week class that starts at 6:30 on Fridays using a coupon for 4 weeks and his classes start on  June 10, 2022. This means he'll have lessons every Friday at 6:30pm from June 10, 2022 until July 1th, 2022.

## FreeClimb model
A freeclimb is a climb that can be booked by any climber (it is not a lesson).

## MyCoupon model
Class that relates Coupons with Users. They are unique (no user can have the same coupon more than once). Once the user uses a coupon, it is deleted (and they can buy another one).

## WeekdaySchedule model
Model with the schedule of the week (opening and closing hours)

## Post model
Not used in this version.

## Income model
Not used in this version.

# Admin.py
All forms displayed in django-admin are here.

# Forms.py
All forms used in the app are here.

# External tools:
- django-multiselectfield (https://pypi.org/project/django-multiselectfield/). If needed install using this command: pip install django-multiselectfield
- FullCalendar (https://fullcalendar.io/docs/initialize-globals). Already installed.