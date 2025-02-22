from django.urls import path
from contact.views import IdentifyView

urlpatterns = [
    path('identify', IdentifyView.as_view(), name='identify'),
]