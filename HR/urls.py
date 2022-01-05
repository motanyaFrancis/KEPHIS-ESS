from django.urls import path

from . import views

urlpatterns = [
    path('LeaveRequest', views.Leave_Request, name="leave"),
    path('Training', views.Training_Request, name='training'),
    path('Loan', views.Loan_Request, name='loan'),
]
