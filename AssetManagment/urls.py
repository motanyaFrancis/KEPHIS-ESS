from django.urls import path
from . import views

from django.urls import path
from AssetManagment.views import CreateAsset

urlpatterns = [
    path('create_asset/', CreateAsset.as_view(), name='create_asset'),
    # Other URL patterns...
]
