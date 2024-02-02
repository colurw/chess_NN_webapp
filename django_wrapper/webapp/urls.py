from django.urls import path, include
from . import views, boot


urlpatterns = [
path('play/', views.play),
]