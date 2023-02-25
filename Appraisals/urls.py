from django.urls import path
from . import views


urlpatterns = [
    path('Appraisals', views.Appraisals.as_view(), name='Appraisals'),
    path('AppraisalDetails/<str:pk>', views.AppraisalDetails.as_view(), name='AppraisalDetails'),
    path('Supervisor/Appraisal/Scores/<str:pk>', views.SupervisorAppraisal.as_view(), name='SupervisorAppraisal'),
    path('AppraisalAttachments/<str:pk>', views.AppraisalAttachments.as_view(), name='AppraisalAttachments'),
    path('SupervisorAttachments/<str:pk>', views.SupervisorAttachments.as_view(), name='SupervisorAttachments'),
    path('FnAppraisalGoals/<str:pk>',views.FnAppraisalGoals.as_view(),name='FnAppraisalGoals'),
    path('FnAppraisalTrainingAndDevelopment/<str:pk>',views.FnAppraisalTrainingAndDevelopment.as_view(),name='FnAppraisalTrainingAndDevelopment'),
    path('FnGetAppraisalAttributes/<str:pk>',views.FnGetAppraisalAttributes.as_view(),name='FnGetAppraisalAttributes'),
    path('FnSubmitEmployeeAppraisal/<str:pk>',views.FnSubmitEmployeeAppraisal.as_view(),name='FnSubmitEmployeeAppraisal'),
    path('FnInitiateAppraisal/<str:pk>',views.FnInitiateAppraisal.as_view(),name='FnInitiateAppraisal'),
    path('FnSubmitAppraisalToSupervisor/<str:pk>',views.FnSubmitAppraisalToSupervisor.as_view(),name='FnSubmitAppraisalToSupervisor'),
    path('FnSubmitAppraisalToManagerial/<str:pk>',views.FnSubmitAppraisalToManagerial.as_view(),name='FnSubmitAppraisalToManagerial'),
]
