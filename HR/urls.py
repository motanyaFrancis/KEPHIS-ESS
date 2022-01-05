from django.urls import path

from . import views

urlpatterns = [
    path('openTenders', views.Leave_Request, name="leave"),
    path('closedTenders', views.closed_tenders, name='closed'),
    path('restrictedTenders', views.Restricted_tenders, name='restricted'),
]
