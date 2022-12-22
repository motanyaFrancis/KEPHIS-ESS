from django.urls import path
from . import views


urlpatterns = [
    path('Appraisals', views.Appraisals.as_view(), name='Appraisals'),
    path('AppraisalDetails/<str:pk>', views.AppraisalDetails.as_view(), name='AppraisalDetails')
]
