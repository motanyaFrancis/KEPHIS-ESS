from django.urls import path

from . import views

urlpatterns = [
    path('openTenders', views.open_tenders, name="open"),
    path('closedTenders', views.closed_tenders, name='closed'),
    path('restrictedTenders', views.Restricted_tenders, name='restricted'),
]
