from django.urls import path

from users import views

urlpatterns = [
    path('', views.home, name='home'),
    path('denied_access/',views.access_denied,name='AccessDenied'),
    path('student/signup/', views.StudentSignUp, name='StudentSignup'),
    path('lecturar/signup/', views.LecturerSignUp, name='LecturerSignup'),
    path('login/', views.SignInView, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forstudent/', views.ForStudent, name='forStudent'),
    path('forlecturer/', views.ForLecturer, name='forLecturer'),
]
