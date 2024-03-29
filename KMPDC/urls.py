"""KMPDC URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('', include('HR.urls')),
    path('', include('Finance.urls')),
    path('', include('Procurement.urls')),
    path('', include('Approvals.urls')),
    path('', include('accounts.urls')),
    path('', include('advance.urls')),
    path('', include('fleet.urls')),
    path('', include('roombooking.urls')),
    path('', include('Appraisals.urls')),
    path('', include('AssetManagment.urls')),
    # path('forest', include('django_forest.urls')),
]
