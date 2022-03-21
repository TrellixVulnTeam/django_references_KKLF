from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from .views import GenerateOTP, ValidateOTP, register, index, UsersListView

# urlpatterns = [
#     re_path(r'^generate/$', GenerateOTP.as_view(), name="generate"),
#     re_path(r'^validate/$', ValidateOTP.as_view(), name="validate"),
# ]

urlpatterns = [
    path('', index, name='index'),
    path('register/', register),
    path('login/', auth_views.LoginView.as_view(template_name='login.html')),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html')),
    path('users/', UsersListView.as_view()),
]
