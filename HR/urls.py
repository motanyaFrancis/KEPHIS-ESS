from django.urls import path

from . import views

urlpatterns = [
    path('LeavePlanner', views.Leave_Planner, name="LeavePlanner"),
    path('CreatePlanner', views.CreatePlanner, name="CreatePlanner"),
    path('PlanDetail/<str:pk>', views.PlanDetail, name='PlanDetail'),
    path('PlannerLine/<str:pk>', views.CreatePlannerLine, name='PlannerLine'),
    path('FnDeleteLeavePlannerLine/<str:pk>',
         views.FnDeleteLeavePlannerLine, name='FnDeleteLeavePlannerLine'),
    path('FnDeleteLeavePlanner', views.FnDeleteLeavePlannerHeader,
         name='FnDeleteLeavePlannerHeader'),

    path('LeaveRequest', views.Leave_Request, name="leave"),
    path('CreateLeave', views.CreateLeave, name="CreateLeave"),
    path('LeaveDetail/<str:pk>', views.LeaveDetail, name='LeaveDetail'),
    path('LeaveApprove/<str:pk>', views.LeaveApproval, name='LeaveApprove'),
    path('LeaveCancel/<str:pk>', views.LeaveCancelApproval, name='LeaveCancel'),
    path('FnGenerateLeave/<str:pk>', views.FnGenerateLeaveReport,
         name='FnGenerateLeaveReport'),
    path('FnDeleteLeaveApplication', views.FnDeleteLeaveApplication,
         name="FnDeleteLeaveApplication"),


    path('Training', views.Training_Request, name='training_request'),
    path('TrainingDetail/<str:pk>', views.TrainingDetail, name='TrainingDetail'),
    path('TrainApprove/<str:pk>', views.TrainingApproval, name='TrainApprove'),
    path('TrainCancel/<str:pk>', views.TrainingCancelApproval, name='TrainCancel'),
    path('TrainingRequest', views.CreateTrainingRequest,
         name='CreateTrainingRequest'),
    path('FnDeleteTraining', views.FnDeleteTrainingRequest,
         name='FnDeleteTrainingRequest'),
    path('FnGenerateTraining/<str:pk>', views.FnGenerateTrainingReport,
         name='FnGenerateTrainingReport'),

    path('FnAdhocTraining/<str:pk>', views.FnAdhocTrainingNeedRequest,
         name='FnAdhocTraining'),
    path('FnAdhocEdit/<str:pk>/<str:no>',
         views.FnAdhocTrainingEdit, name='FnAdhocEdit'),
    path('FnAdhocLineDelete/<str:pk>',
         views.FnAdhocLineDelete, name='FnAdhocLineDelete'),
    path('p9', views.PNineRequest, name='pNine'),
    path('payslip', views.PayslipRequest, name='payslip'),
]
