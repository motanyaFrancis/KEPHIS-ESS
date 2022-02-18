from django.urls import path

from . import views

urlpatterns = [
    path('LeaveRequest', views.Leave_Request, name="leave"),
    path('CreateLeave', views.CreateLeave, name="CreateLeave"),
    path('LeaveDetail/<str:pk>', views.LeaveDetail, name='LeaveDetail'),
    path('LeaveApprove/<str:pk>', views.LeaveApproval, name='LeaveApprove'),
    path('Training', views.Training_Request, name='training_request'),
    path('TrainingRequest', views.CreateTrainingRequest,
         name='CreateTrainingRequest'),
    path('Loan', views.Loan_Request, name='loan'),
    path('NewLoan', views.CreateLoanRequest, name='NewLoan'),
    path('LoanLines/<str:pk>', views.LoanLines, name='LoanLines'),
    path('LoanCollateral/<str:pk>',
         views.FnLoanCollateral, name='FnLoanCollateral'),
]
