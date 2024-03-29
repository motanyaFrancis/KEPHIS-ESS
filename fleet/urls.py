from django.urls import path
from . import views

urlpatterns = [
    # work Ticket
    path('workTicket/', views.WorkTicket.as_view(), name='workTicket'),
    path('get_prev_tickets/', views.get_prev_tickets.as_view(), name='get_prev_tickets'),
    path('WorkTicketDetails/<str:pk>', views.WorkTicketDetails.as_view(), name='WorkTicketDetails'),
    path('UploadTicketAttachment/<str:pk>', views.UploadTicketAttachment, name='UploadTicketAttachment'),
    path('DeleteTicketAttachment/<str:pk>', views.DeleteTicketAttachment, name='DeleteTicketAttachment'),
    path('FnSubmitWorkTicket/<str:pk>', views.FnSubmitWorkTicket.as_view(), name='FnSubmitWorkTicket'),
    path('FnCancelWorkTicket/<str:pk>', views.FnCancelWorkTicket, name='FnCancelWorkTicket'),
    path('FnIssueWorkTicket/<str:pk>', views.FnIssueWorkTicket.as_view(),name="FnIssueWorkTicket"),
    path('FnGenerateWorkTicketReport/<str:pk>', views.FnGenerateWorkTicketReport.as_view(), name='FnGenerateWorkTicketReport'),
    
    # VehicleInspection
    path('vehicleInspection', views.VehicleInspection.as_view(), name='vehicleInspection'),
    path('VehicleInspectionDetails/<str:pk>', views.VehicleInspectionDetails.as_view(), name='VehicleInspectionDetails'),
    path('UploadInspectionAttachment/<str:pk>', views.UploadInspectionAttachment, name='UploadInspectionAttachment'),
    path('DeleteInspectionAttachment/<str:pk>', views.DeleteInspectionAttachment, name='DeleteInspectionAttachment'),
    path('FnSubmitVehicleInspection/<str:pk>', views.FnSubmitVehicleInspection.as_view(), name='FnSubmitVehicleInspection' ),
    path('FnBookForInspection/<str:pk>', views.FnBookForInspection.as_view(), name='FnBookForInspection'),
    path('FnCancelBooking/<str:pk>', views.FnCancelBooking, name='FnCancelBooking'),
    path('InspectionDefects/<str:pk>', views.InspectionDefects, name='InspectionDefects'),
    path('Submit2_TO/<str:pk>', views.Submit2_TO.as_view(), name='Submit2_TO'),
    path('FnMarkInspected/<str:pk>', views.FnMarkInspected.as_view(), name='FnMarkInspected'),
    
    # repair request
    path('vehicleRepairRequest', views.VehicleRepairRequest.as_view(), name='vehicleRepairRequest'),
    path('vehicleRepairDetails/<str:pk>', views.VehicleRepairRequestDetails.as_view(), name='vehicleRepairDetails'),
    path('UploadRepairAttachment/<str:pk>', views.UploadRepairAttachment, name='UploadRepairAttachment'),
    path('DeleteRepairAttachment/<str:pk>', views.DeleteRepairAttachment, name='DeleteRepairAttachment'),
    path('FnRepairRequestLine/<str:pk>', views.FnRepairRequestLines, name='FnRepairRequestLine'),
    path('FnRaiseRepairRequest/<str:pk>', views.FnRaiseRepairRequest.as_view(), name='FnRaiseRepairRequest'),
    path('FnCancelRepairRequest/<str:pk>', views.FnCancelRepairRequest, name='FnCancelRepairRequest'),
    path('FnConfirmRepaireRequest/<str:pk>', views.FnConfirmRepaireRequest.as_view(), name=' FnConfirmRepaireRequest'),
    path('FNServiceInstructionsSheet/<str:pk>', views.FNServiceInstructionsSheet.as_view(), name='FNServiceInstructionsSheet'),
    
    # Transport Request
    path('TransportRequest', views.TransportRequest.as_view(), name='TransportRequest'),
    path('TransportRequestDetails/<str:pk>', views.TransportRequestDetails.as_view(), name='TransportRequestDetails'),
    path('FnTravelEmployeeLine/<str:pk>', views.FnTravelEmployeeLine, name='FnTravelEmployeeLine'),
    path('UploadTransportRequestAttachment/<str:pk>', views.UploadTransportRequestAttachment, name='UploadTransportRequestAttachment'),
    path('DeleteTransportRequestAttachment<str:pk>', views.DeleteTransportRequestAttachment, name='DeleteTransportRequestAttachment'),
    path('FnSubmitTravelRequest/<str:pk>', views.FnSubmitTravelRequest.as_view(), name='FnSubmitTravelRequest'),
    path('FnNotifyBothRequesterAndDrivers/<str:pk>', views.FnNotifyBothRequesterAndDrivers.as_view(), name='FnNotifyBothRequesterAndDrivers'),
    
    # Accidents
    path('Accidents', views.Accidents.as_view(), name='Accidents'),
    path('AccidentDetails/<str:pk>', views.AccidentDetails.as_view(), name='AccidentDetails'),
    path('UploadAccidentAttachment/<str:pk>', views.UploadAccidentAttachment, name='UploadAccidentAttachment'),
    path('DeleteAccidentAttachment/<str:pk>', views.DeleteAccidentAttachment, name='DeleteAccidentAttachment'),
    path('FnSubmitAccidents/<str:pk>', views.FnSubmitAccidents.as_view(), name='FnSubmitAccidents'),
    
    # Service Request
    path('ServiceRequest', views.ServiceRequest.as_view(), name='ServiceRequest'),
    path('ServiceRequestDetails/<str:pk>', views.ServiceRequestDetails.as_view(), name='ServiceRequestDetails' ),
    path('UploadServiceRequestAttachment/<str:pk>', views.UploadServiceRequestAttachment, name='UploadServiceRequestAttachment'),
    path('DeleteServiceRequestAttachment/<str:pk>', views.DeleteServiceRequestAttachment, name='DeleteServiceRequestAttachment'),
    path('FnSubmitServiceRequest/<str:pk>', views.FnSubmitServiceRequest.as_view(), name='FnSubmitServiceRequest'),
    path('FnServiceRequestLine/<str:pk>', views.FnServiceRequestLine, name='FnServiceRequestLine'),
    path('FnCancelServiceRequest/<str:pk>', views.FnCancelServiceRequest, name='FnCancelServiceRequest'),
    
    #Fuel Consumption
    path('fuel/consumption', views.FuelConsumption.as_view(), name='fuel'),
    path('fuel/consumption/<str:pk>',views.FuelDetails.as_view(), name='FuelDetails' ),
    path('FnSubmitFuelConsumption/<str:pk>', views.FnSubmitFuelConsumption.as_view(), name='FnSubmitFuelConsumption'),
    path('FnFuelConsumptionGenerator', views.FnFuelConsumptionGenerator.as_view(), name='FnFuelConsumptionGenerator'),
    path('FnFuelConsumptionVehicle', views.FnFuelConsumptionVehicle.as_view(), name='FnFuelConsumptionVehicle'),
    
    #Speed Govonor
    path('speed/governor', views.SpeedGovernor.as_view(), name='SpeedGovernor'),
    path('GovernorDetails/<str:pk>', views.GovernorDetails.as_view(), name='GovernorDetails'),
    path('FnSubmitSpeedGovernor/<str:pk>', views.FnSubmitSpeedGovernor.as_view(), name='FnSubmitSpeedGovernor'),
    path('UploadSpeedGovernorAttachment/<str:pk>', views.UploadSpeedGovernorAttachment.as_view(), name='UploadSpeedGovernorAttachment'),
    path('DeleteSpeedGovernor/<str:pk>', views.DeleteSpeedGovernor.as_view(), name='DeleteSpeedGovernor'),

    # Gvcu
    path('gvcu', views.GVCU.as_view(), name='gvcu'),
    path('gvcu/<str:pk>', views.GVCU_Details.as_view(), name='gvcuDetails'),
    path('FnSubmitGovermmentCheckUnit/<str:pk>', views.FnSubmitGovermmentCheckUnit.as_view(), name='FnSubmitGovermmentCheckUnit'),
    path('UploadGVCUAttachment/<str:pk>', views.UploadGVCUAttachment.as_view(), name='UploadGVCUAttachment'),
    path('DeleteGVCUAttachment/<str:pk>', views.DeleteGVCUAttachment.as_view(), name='DeleteGVCUAttachment'),
    path('FnGVCUPassangers/<str:pk>', views.FnGVCUPassangers.as_view(), name='FnGVCUPassangers'),
]