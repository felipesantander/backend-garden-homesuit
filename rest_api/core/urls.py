from django.urls import path

from core.views.Data.views import ingest_data

urlpatterns = [
    path('data/ingest/', ingest_data, name='ingest_data'),
]
