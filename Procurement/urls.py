from django.urls import path
from . import views

urlpatterns = [
    path('PurchaseRequisition', views.PurchaseRequisition, name='purchase'),
    path('CreatePurchaseRequisition', views.CreatePurchaseRequisition,
         name='CreatePurchaseRequisition'),
    path('PurchaseDetail/<str:pk>',
         views.PurchaseRequestDetails, name='PurchaseDetail'),
    path('PurchaseApprove/<str:pk>',
         views.PurchaseApproval, name='PurchaseApprove'),
    path('RepairRequest', views.RepairRequest, name='repair'),
    path('CreateRepairRequest', views.CreateRepairRequest,
         name='CreateRepairRequest'),
    path('RepairDetail/<str:pk>',
         views.RepairRequestDetails, name='RepairDetail'),
    path('RepairApprove/<str:pk>',
         views.RepairApproval, name='RepairApprove'),
    path('RepairLines/<str:pk>',
         views.CreateRepairLines, name='RepairLines'),
    path('StoreRequest', views.StoreRequest, name='store'),
    path('CreateStoreRequest', views.CreateStoreRequisition,
         name='CreateStoreRequest'),
    path('StoreDetail/<str:pk>',
         views.StoreRequestDetails, name='StoreDetail'),
    path('StoreApprove/<str:pk>',
         views.StoreApproval, name='StoreApprove'),
    path('CreateStoreLine/<str:pk>',
         views.CreateStoreLines, name='CreateStoreLine'),
]
