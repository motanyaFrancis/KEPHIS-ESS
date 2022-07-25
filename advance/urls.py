from django.urls import path

from . import views

urlpatterns = [
    path("salary advance", views.advance,name="advance"),
    path("RequestAdvance",views.RequestAdvance, name="RequestAdvance"),
    path("advanceDetail/<str:pk>",views.advanceDetail, name="advanceDetail"),
    path("FnRequestSalaryAdvanceApproval/<str:pk>",views.FnRequestSalaryAdvanceApproval, name="FnRequestSalaryAdvanceApproval"),
]