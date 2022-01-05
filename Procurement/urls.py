from django.urls import path
from . import views

urlpatterns = [
    path('PurchaseRequisition', views.PurchaseRequisition, name='purchase'),
    path('RepairRequest', views.RepairRequest, name='repair'),
    path('StoreRequest', views.StoreRequest, name='store'),
]
