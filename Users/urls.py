from rest_framework.urls import path
from . import views

urlpatterns = [
    path('login/', views.login),
    path('profile/', views.profile),
]
