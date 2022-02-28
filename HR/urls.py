from django.urls import path

from . import views

urlpatterns = [
    path('LeaveRequest', views.Leave_Request, name="leave"),
    path('CreateLeave', views.CreateLeave, name="CreateLeave"),
    path('LeaveDetail/<str:pk>', views.LeaveDetail, name='LeaveDetail'),
    path('LeaveApprove/<str:pk>', views.LeaveApproval, name='LeaveApprove'),
    path('LeaveCancel/<str:pk>', views.LeaveCancelApproval, name='LeaveCancel'),
    path('Training', views.Training_Request, name='training_request'),
    path('TrainingDetail/<str:pk>', views.TrainingDetail, name='TrainingDetail'),
    path('TrainApprove/<str:pk>', views.TrainingApproval, name='TrainApprove'),
    path('TrainingRequest', views.CreateTrainingRequest,
         name='CreateTrainingRequest'),
]
