from django.urls import path
from . import views

urlpatterns = [
    path('LeaveApproval', views.LeaveApproval, name="leaveApp"),
    path('TrainingApproval', views.TrainingApproval, name="TrainApp"),
    path('LoanApproval', views.LoansApproval, name="LoanApp"),
]
