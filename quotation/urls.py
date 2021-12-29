from django.urls import path
from . import views


urlpatterns = [
    path('quotation', views.requestQuote, name='quote'),
    path('daraja', views.daraja, name='daraja'),
]
