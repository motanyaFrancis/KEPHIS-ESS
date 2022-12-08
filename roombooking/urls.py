from django.urls import path
from . import views

urlpatterns = [
    path('InternalRoomBooking', views.InternalRoomBooking.as_view(), name = 'InternalRoomBooking')
]