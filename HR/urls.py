from django.urls import path

from . import views

urlpatterns = [
    path('leave', views.Leave_Request.as_view(), name="leave"),
    path('leave/detail/<str:pk>', views.LeaveDetail.as_view(), name='LeaveDetail'),
    path('LeaveApprove/<str:pk>', views.LeaveApproval, name='LeaveApprove'),
    path('LeaveCancel/<str:pk>', views.LeaveCancelApproval, name='LeaveCancel'),
    path('FnGenerateLeave/<str:pk>', views.FnGenerateLeaveReport,name='FnGenerateLeaveReport'),
    path("DeleteLeaveAttachment/<str:pk>",views.DeleteLeaveAttachment,name ="DeleteLeaveAttachment"),


    path('training', views.Training_Request.as_view(), name='training_request'),
    path('training/detail/<str:pk>', views.TrainingDetail.as_view(), name='TrainingDetail'),
    path('TrainApprove/<str:pk>', views.TrainingApproval.as_view(), name='TrainApprove'),
    path('TrainCancel/<str:pk>', views.TrainingCancelApproval, name='TrainCancel'),
    path('FnGenerateTraining/<str:pk>', views.FnGenerateTrainingReport,name='FnGenerateTrainingReport'),
    path('UploadTrainingAttachment/<str:pk>', views.UploadTrainingAttachment,name='UploadTrainingAttachment'),
    path('FnTrainingEvaluation/<str:pk>',views.FnTrainingEvaluation.as_view(),name='FnTrainingEvaluation'),

    path('FnAdhocEdit/<str:pk>/<str:no>',views.FnAdhocTrainingEdit, name='FnAdhocEdit'),
    path('FnAdhocLineDelete/<str:pk>',views.FnAdhocLineDelete, name='FnAdhocLineDelete'),
    path('p9', views.PNineRequest.as_view(), name='pNine'),
    path('payslip', views.PayslipRequest.as_view(), name='payslip'),
    
    path('disciplinary',views.Disciplinary,name="disciplinary"),
    path('DisciplineDetails/<str:pk>', views.DisciplineDetail,name='DisciplineDetail'),
    path('DisciplineResponse/<str:pk>', views.DisciplinaryResponse, name='DisciplineResponse'),
]
