# dashboard/urls.py
from django.urls import path
from .views import ProducteurDashboardView, AdminDashboardView

urlpatterns = [
    path('dashboard/producteur/', ProducteurDashboardView.as_view(), name='dashboard-producteur'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='dashboard-admin'),
]
