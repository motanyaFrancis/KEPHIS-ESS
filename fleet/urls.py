from django.urls import path
from . import views

urlpatterns = [
    path('workTicket/', views.WorkTicket.as_view(), name='workTicket'),
    path('WorkTicketDetails', views.WorkTicketDetails.as_view(), name=' WorkTicketDetails'),
    path('vehicleInspection/', views.VehicleInspection.as_view(), name='vehicleInspection'),
    path('vehicleRepairRequest', views.VehicleRepaiRequest.as_view(), name='vehicleRepairRequest'),
    path('vehicleRepairDetails/<str:pk>', views.VehicleRepaiRequestDetails.as_view(), name='vehicleRepairDetails'),

]