# users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView, 
    TokenBlacklistView,
    TokenVerifyView,
)

from .views import (
    RegisterView, 
    MeViewSet, 
    ChangePasswordView, 
    UserListView, 
    UserDetailView,
)

urlpatterns = [
    # 1. AUTHENTIFICATION JWT
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('auth/logout/', TokenBlacklistView.as_view(), name='logout'),
    path('auth/verify/', TokenVerifyView.as_view(), name='verify'),  
    
    # 2. PROFIL UTILISATEUR CONNECTÉ
    path('users/me/', MeViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='me'),
    path('users/me/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # 3. ADMINISTRATION (réservé admin)
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]