from django.urls import path
from . import views

urlpatterns = [
    path('workTicket/', views.WorkTicket.as_view(), name='workTicket'),
    path('WorkTicketDetails/<str:pk>', views.WorkTicketDetails.as_view(), name='WorkTicketDetails'),
    path('vehicleInspection/', views.VehicleInspection.as_view(), name='vehicleInspection'),
    path('vehicleRepairRequest', views.VehicleRepaiRequest.as_view(), name='vehicleRepairRequest'),
    path('vehicleRepairDetails/<str:pk>', views.VehicleRepairRequestDetails.as_view(), name='vehicleRepairDetails'),
    path('TransportRequest', views.TransportRequest.as_view(), name='TransportRequest'),
    path('Accidents', views.Accidents.as_view(), name='Accidents'),
    path('AccidentDetails', views.AccidentDetails.as_view(), name='AccidentDetails')

]