from django.urls import path
from . import views

urlpatterns = [
    path('InternalRoomBooking', views.InternalRoomBooking.as_view(), name = 'InternalRoomBooking'),
    path('InternalRoomDetails/<str:pk>', views.InternalRoomBookingDetails.as_view(), name='InternalRoomDetails'),
    path('FnRoomBookingLine/<str:pk>', views.FnRoomBookingLine, name='FnRoomBookingLine'),
    path('DisabilityDetails/<str:pk>', views.DisabilityDetails.as_view(), name = 'DisabilityDetails'),
    path('FnAccommodationBookingLine/<str:pk>', views.FnAccommodationBookingLine, name='FnAccommodationBookingLine'),
    path('UploadRoomBookingAttachment/<str:pk>', views.UploadRoomBookingAttachment, name='UploadRoomBookingAttachment'),
    path('FnSubmitInternalRoomBooking/<str:pk>', views.FnSubmitInternalRoomBooking.as_view(), name='FnSubmitInternalRoomBooking'),
    path('FnCancelInternalRoomBooking/<str:pk>', views.FnCancelInternalRoomBooking.as_view(), name='FnCancelInternalRoomBooking'),
]