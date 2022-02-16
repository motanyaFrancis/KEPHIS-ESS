from django.urls import path

from . import views

urlpatterns = [
    path('LeaveRequest', views.Leave_Request, name="leave"),
    path('CreateLeave', views.CreateLeave, name="CreateLeave"),
    path('Training', views.Training_Request, name='training'),
    path('Loan', views.Loan_Request, name='loan'),
]
