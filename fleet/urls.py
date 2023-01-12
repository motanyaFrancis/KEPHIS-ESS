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
    path('FnSubmitVehicleInspection/<str:pk>', views.FnSubmitVehicleInspection, name='FnSubmitVehicleInspection' ),
    path('FnBookForInspection/<str:pk>', views.FnBookForInspection, name='FnBookForInspection' ),
    path('FnCancelBooking/<str:pk>', views.FnCancelBooking, name='FnCancelBooking' ),

    # repair request
    path('vehicleRepairRequest', views.VehicleRepairRequest.as_view(), name='vehicleRepairRequest'),
    path('vehicleRepairDetails/<str:pk>', views.VehicleRepairRequestDetails.as_view(), name='vehicleRepairDetails'),
    path('UploadRepairAttachment/<str:pk>', views.UploadRepairAttachment, name='UploadRepairAttachment'),
    path('DeleteRepairAttachment/<str:pk>', views.DeleteRepairAttachment, name='DeleteRepairAttachment'),
    path('FnRepairRequestLine/<str:pk>', views.FnRepairRequestLines, name='FnRepairRequestLine'),
    path('FnRaiseRepairRequest/<str:pk>', views.FnRaiseRepairRequest, name='FnRaiseRepairRequest'),

    
    # Transport Request
    path('TransportRequest', views.TransportRequest.as_view(), name='TransportRequest'),
    path('TransportRequestDetails/<str:pk>', views.TransportRequestDetails.as_view(), name='TransportRequestDetails'),
    path('FnTravelEmployeeLine/<str:pk>', views.FnTravelEmployeeLine, name='FnTravelEmployeeLine'),
    path('UploadTransportRequestAttachment/<str:pk>', views.UploadTransportRequestAttachment, name='UploadTransportRequestAttachment'),
    path('DeleteTransportRequestAttachment<str:pk>', views.DeleteTransportRequestAttachment, name='DeleteTransportRequestAttachment'),
    path('FnSubmitTravelRequest/<str:pk>', views.FnSubmitTravelRequest, name='FnSubmitTravelRequest'),
    
    # Accidents
    path('Accidents', views.Accidents.as_view(), name='Accidents'),
    path('AccidentDetails/<str:pk>', views.AccidentDetails.as_view(), name='AccidentDetails'),
    path('UploadAccidentAttachment/<str:pk>', views.UploadAccidentAttachment, name='UploadAccidentAttachment'),
    path('DeleteAccidentAttachment/<str:pk>', views.DeleteAccidentAttachment, name='DeleteAccidentAttachment'),
    path('FnSubmitAccidents/<str:pk>', views.FnSubmitAccidents, name='FnSubmitAccidents'),
    
    # Service Request
    path('ServiceRequest', views.ServiceRequest.as_view(), name='ServiceRequest'),
    path('ServiceRequestDetails/<str:pk>', views.ServiceRequestDetails.as_view(), name='ServiceRequestDetails' ),
    path('UploadServiceRequestAttachment/<str:pk>', views.UploadServiceRequestAttachment, name='UploadServiceRequestAttachment'),
    path('DeleteServiceRequestAttachment/<str:pk>', views.DeleteServiceRequestAttachment, name='DeleteServiceRequestAttachment'),
    path('FnSubmitServiceRequest/<str:pk>', views.FnSubmitServiceRequest, name='FnSubmitServiceRequest'),
    path('FnServiceRequestLine/<str:pk>', views.FnServiceRequestLine, name='FnServiceRequestLine'),
    path('FnCancelServiceRequest/<str:pk>', views.FnCancelServiceRequest, name='FnCancelServiceRequest')

]