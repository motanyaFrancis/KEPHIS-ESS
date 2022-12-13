from django.urls import path
from . import views

urlpatterns = [
    # work Ticket
    path('workTicket/', views.WorkTicket.as_view(), name='workTicket'),
    path('WorkTicketDetails/<str:pk>', views.WorkTicketDetails.as_view(), name='WorkTicketDetails'),
    path('UploadTicketAttachment/<str:pk>', views.UploadTicketAttachment, name='UploadTicketAttachment'),
    path('DeleteTicketAttachment/<str:pk>', views.DeleteTicketAttachment, name='DeleteTicketAttachment'),
    path('FnSubmitWorkTicket/<str:pk>', views.FnSubmitWorkTicket, name='FnSubmitWorkTicket'),
    
    # VehicleInspection
    path('vehicleInspection', views.VehicleInspection.as_view(), name='vehicleInspection'),
    path('VehicleInspectionDetails/<str:pk>', views.VehicleInspectionDetails.as_view(), name='VehicleInspectionDetails'),
    path('UploadInspectionAttachment/<str:pk>', views.UploadInspectionAttachment, name='UploadInspectionAttachment'),
    path('DeleteInspectionAttachment/<str:pk>', views.DeleteInspectionAttachment, name='DeleteInspectionAttachment'),

    # repair request
    path('vehicleRepairRequest', views.VehicleRepaiRequest.as_view(), name='vehicleRepairRequest'),
    path('vehicleRepairDetails/<str:pk>', views.VehicleRepairRequestDetails.as_view(), name='vehicleRepairDetails'),
    path('UploadRepairAttachment/<str:pk>', views.UploadRepairAttachment, name='UploadRepairAttachment'),
    path('DeleteRepairAttachment/<str:pk>', views.DeleteRepairAttachment, name='DeleteRepairAttachment'),
    # path('FnRepairRequestLine/<str:pk>', views.FnRepairRequestLine, name='FnRepairRequestLine'),

    
    # Tranxport Request
    path('TransportRequest', views.TransportRequest.as_view(), name='TransportRequest'),

    # Accidents
    path('Accidents', views.Accidents.as_view(), name='Accidents'),
    path('AccidentDetails/<str:pk>', views.AccidentDetails.as_view(), name='AccidentDetails'),
    path('UploadAccidentAttachment/<str:pk>', views.UploadAccidentAttachment, name='UploadAccidentAttachment'),
    path('DeleteAccidentAttachment/<str:pk>', views.DeleteAccidentAttachment, name='DeleteAccidentAttachment'),
    path('FnSubmitAccidents/<str:pk>', views.FnSubmitAccidents, name='FnSubmitAccidents'),
    
    # Service Request
    path('ServiceRequest', views.ServiceRequest.as_view(), name='ServiceRequest'),
    path('ServiceRequestDetails/<str:pk>', views.ServiceRequestDetails.as_view(), name='ServiceRequestDetails' ),

]