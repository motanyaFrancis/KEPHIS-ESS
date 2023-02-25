from django.urls import path
from . import views


urlpatterns = [
    path('imprest/requisition', views.ImprestRequisition.as_view(), name='imprestReq'),
    path('CreateImpLines/<str:pk>',
         views.CreateImprestLines, name='CreateImpLines'),
    path('FnDeleteImprestLine/<str:pk>',
         views.FnDeleteImprestLine, name='FnDeleteImprestLine'),
    path('Impres/<str:pk>', views.FnRequestPaymentApproval, name='Impres'),
    path('FnGenerateImprestReport/<str:pk>',
         views.FnGenerateImprestReport, name='FnGenerateImprestReport'),
    path('ImpresCancel/<str:pk>', views.FnCancelPaymentApproval, name='ImpresCancel'),
    path('Imp/<str:pk>', views.ImprestDetails.as_view(), name='IMPDetails'),
    path('UploadAttachment/<str:pk>',
         views.UploadAttachment, name='UploadAttachment'),
    path('DeleteImprestAttachment/<str:pk>',
         views.DeleteImprestAttachment, name='DeleteImprestAttachment'),


    path('ImprestSurrender', views.ImprestSurrender.as_view(), name='imprestSurr'),
    path('ImpSurrender/<str:pk>',
         views.SurrenderDetails.as_view(), name='IMPSurrender'),
    path('SurrenderApprove/<str:pk>',
         views.SurrenderApproval, name='SurrenderApprove'),
    path('CancelSurrenderApproval/<str:pk>',
         views.FnCancelSurrenderApproval, name='CancelSurrenderApproval'),
    path('UploadSurrenderAttachment/<str:pk>',
         views.UploadSurrenderAttachment, name='UploadSurrenderAttachment'),
    path('FnGenerateImprestSurrenderReport/<str:pk>',
         views.FnGenerateImprestSurrenderReport, name='FnGenerateImprestSurrenderReport'),
    path('DeleteSurrenderAttachment/<str:pk>',
         views.DeleteSurrenderAttachment, name='DeleteSurrenderAttachment'),

    path('StaffClaim', views.StaffClaim.as_view(), name='claim'),
    path('Claim/<str:pk>', views.ClaimDetails.as_view(), name='ClaimDetail'),
    path('ClaimLines/<str:pk>', views.CreateClaimLines, name='ClaimLines'),
    path('ClaimApprove/<str:pk>', views.ClaimApproval, name='ClaimApprove'),
    path('ClaimCancel/<str:pk>', views.FnCancelClaimApproval, name='ClaimCancel'),
    path('FnDeleteStaffClaimLine/<str:pk>', views.FnDeleteStaffClaimLine,
         name='FnDeleteStaffClaimLine'),
    path('FnGenerateStaffClaimReport/<str:pk>', views.FnGenerateStaffClaimReport, 
         name='FnGenerateStaffClaimReport'),
    path('DeleteClaimAttachment/<str:pk>',views.DeleteClaimAttachment, name='DeleteClaimAttachment'),
    path('ClaimAttachment/<str:pk>',views.ClaimAttachment.as_view(), name='ClaimAttachment'),

]
