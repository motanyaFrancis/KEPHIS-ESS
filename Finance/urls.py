from django.urls import path
from . import views


urlpatterns = [
    path('ImprestRequisition', views.ImprestRequisition, name='imprestReq'),
    path('ImprestSurrender', views.ImprestSurrender, name='imprestSurr'),
]
