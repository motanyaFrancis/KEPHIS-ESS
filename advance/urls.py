from django.urls import path

from . import views

urlpatterns = [
    path("salary advance", views.advance.as_view(),name="advance"),
    path("advanceDetail/<str:pk>",views.advanceDetail.as_view(), name="advanceDetail"),
    path("FnRequestSalaryAdvanceApproval/<str:pk>",views.FnRequestSalaryAdvanceApproval, name="FnRequestSalaryAdvanceApproval"),
    path("FnCancelSalaryAdvanceApproval/<str:pk>",views.FnCancelSalaryAdvanceApproval, name="FnCancelSalaryAdvanceApproval"),
]