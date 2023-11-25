from django.urls import path, include
from .views import *

urlpatterns = [
    path('oauth/', include('social_django.urls', namespace='social')),
    path('data-analyser/', print_database, name='data_analyser'),
]