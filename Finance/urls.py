from django.urls import path
from . import views


urlpatterns = [
    path('ImprestRequisition', views.ImprestRequisition, name='imprestReq'),
    path('CreateImp', views.CreateImprest, name='create'),
    path('CreateImpLines/<str:pk>',
         views.CreateImprestLines, name='CreateImpLines'),
    path('Imp/<str:pk>', views.ImprestDetails, name='IMPDetails'),
    path('ImpApprove/<str:pk>', views.ImprestApproval, name='ImpApprove'),
    path('ImprestSurrender', views.ImprestSurrender, name='imprestSurr'),
    path('CreateSurrender', views.CreateSurrender, name="CreateSurrender"),
    path('ImpSurrender/<str:pk>', views.SurrenderDetails, name='IMPSurrender'),
    path('SurrenderApprove/<str:pk>',
         views.SurrenderApproval, name='SurrenderApprove'),
    path('ImpSurrenderLines/<str:pk>',
         views.CreateSurrenderLines, name='CreateSurrenderLines'),
    path('StaffClaim', views.StaffClaim, name='claim'),
    path("NewClaim", views.CreateClaim, name="NewClaim"),
    path('Claim/<str:pk>', views.ClaimDetails, name='ClaimDetail'),
    path('ClaimLines/<str:pk>', views.CreateClaimLines, name='ClaimLines'),
    path('ClaimApprove/<str:pk>', views.ClaimApproval, name='ClaimApprove'),
]
