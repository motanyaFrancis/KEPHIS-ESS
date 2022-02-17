from django.urls import path
from . import views

urlpatterns = [
    path('PurchaseRequisition', views.PurchaseRequisition, name='purchase'),
    path('PurchaseDetail/<str:pk>',
         views.PurchaseRequestDetails, name='PurchaseDetail'),
    path('RepairRequest', views.RepairRequest, name='repair'),
    path('RepairDetail/<str:pk>',
         views.RepairRequestDetails, name='RepairDetail'),
    path('StoreRequest', views.StoreRequest, name='store'),
]
