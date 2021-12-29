from django.urls import path
from . import views

urlpatterns = [
    path('profile', views.profile_request, name="profile"),
    path('', views.login_request, name='auth'),
]
