from django.urls import path
from . import views

urlpatterns = [
    path('PurchaseRequisition', views.PurchaseRequisition, name='purchase'),
]
