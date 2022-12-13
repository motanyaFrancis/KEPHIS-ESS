from django.urls import path
from . import views

urlpatterns = [
    path('InternalRoomBooking', views.InternalRoomBooking.as_view(), name = 'InternalRoomBooking'),
    path('InternalRoomDetails/<str:pk>', views.InternalRoomBookingDetails.as_view(), name='InternalRoomDetails'),
    path('FnRoomBookingLine/<str:pk>', views.FnRoomBookingLine, name='FnRoomBookingLine'),
]