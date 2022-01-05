from django.urls import path
from . import views

urlpatterns = [
    path('LeaveRequests', views.Leave_Requests, name="leaveApp"),
    path('SubResTenders', views.submittedResTenders, name="sub_res"),
    path('SubRFQ', views.submittedRFQ, name="sub_rfq"),
    path('SubInterest', views.submittedInterest, name="sub_int"),
]
