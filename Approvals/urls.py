from django.urls import path
from . import views

urlpatterns = [
    path('LeaveApproval', views.LeaveApproval, name="leaveApp"),
    path('TrainingApproval', views.TrainingApproval, name="TrainApp"),
    path('SubRFQ', views.submittedRFQ, name="sub_rfq"),
    path('SubInterest', views.submittedInterest, name="sub_int"),
]
