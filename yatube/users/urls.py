from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordChangeView)

from django.urls import path, reverse_lazy
from . import views

app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        LogoutView.as_view(
            template_name='users/logged_out.html'),
        name='logout'
    ),
    path('signup/', views.SignUp.as_view(),
         name='signup'),
    path('login/',
         LoginView.as_view(
             template_name='users/login.html'),
         name='login'),
    path('password_change/',
         PasswordChangeView.as_view(
             template_name='users/password_change_form.html',
             success_url=reverse_lazy('users:pass_change_done')),
         name='pass_change'),
    path('password_change/done',
         PasswordChangeDoneView.as_view(
             template_name='users/password_change_done.html'),
         name='pass_change_done')
]
