from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
import logging

from .models import User
from .serializers import (
    UserRegisterSerializer, UserProfileSerializer, ChangePasswordSerializer,
    UserMinimalSerializer,
)
from .permissions import IsOwnerOrAdmin


class RegisterView(generics.CreateAPIView):
    """Inscription d'un nouvel utilisateur."""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'register'

    @extend_schema(
        summary='Inscription',
        tags=['Auth'],
        responses={201: UserProfileSerializer}  
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Surcharger pour retourner l'utilisateur créé."""
        user = serializer.save()
        return user

    def create(self, request, *args, **kwargs):
        """Personnaliser la réponse après création."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        
        # Générer un token JWT pour que l'utilisateur soit directement connecté
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data, # Retourner les données de l'utilisateur créé en json
            'access': str(refresh.access_token), # Token d'accès
            'refresh': str(refresh) # Token de rafraîchissement
        }, status=status.HTTP_201_CREATED)
 


class MeViewSet(viewsets.GenericViewSet):
    """ViewSet pour les actions sur le profil connecté."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(summary='Mon profil', tags=['Users'])
    def retrieve(self, request):
        """GET /me/ - Voir mon profil"""
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    @extend_schema(summary='Mettre à jour mon profil', tags=['Users'])
    def partial_update(self, request):
        """PATCH /me/ - Modifier mon profil"""
        serializer = self.get_serializer(
            self.get_object(), 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(summary='Supprimer mon compte', tags=['Users'])
    def destroy(self, request):
        """DELETE /me/ - Supprimer mon compte"""
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ChangePasswordView(APIView):
    """Changement de mot de passe."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: {'description': 'Mot de passe mis à jour avec succès'},
            400: {'description': 'Erreur de validation'}
        },
        summary='Changer le mot de passe',
        tags=['Users'],
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # La sauvegarde est déjà gérée dans le sérialiseur
        serializer.save() 
        
        return Response({
            'detail': 'Mot de passe mis à jour avec succès.',
            'message': 'Votre mot de passe a été modifié. Utilisez le nouveau mot de passe pour vos prochaines connexions.'
        })
    


class UserListView(generics.ListAPIView):
    """Liste de tous les utilisateurs (Admin uniquement)."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserMinimalSerializer
    permission_classes = [IsAdminUser]
    
    # Filtrage avancé
    filterset_fields = ['role', 'ville', 'region']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telephone']
    ordering_fields = ['date_joined', 'username', 'role']
    
    @extend_schema(
        summary='Liste des utilisateurs (Admin)',
        tags=['Admin'],
        description='Retourne la liste de tous les utilisateurs avec possibilité de filtrer.'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    #def get_queryset(self):
       # """Personnaliser le queryset si besoin."""
       # queryset = super().get_queryset()
        
        # Exemple: exclure certains utilisateurs si nécessaire
        # queryset = queryset.exclude(is_superuser=True)
        
        #return queryset



class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Gestion d'un utilisateur par l'admin."""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        summary='Détail utilisateur (Admin)',
        tags=['Admin'],
        responses={200: UserProfileSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Modifier utilisateur (Admin)',
        tags=['Admin'],
        description="L'admin peut modifier n'importe quel utilisateur"
    )
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        summary='Supprimer utilisateur (Admin)',
        tags=['Admin']
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        logger = logging.getLogger(__name__)
        old_data = UserProfileSerializer(self.get_object()).data
        serializer.save()
        new_data = serializer.data
        # Trouver les champs qui ont changé
        changed_fields = {
            field: (old_data[field], new_data[field])
            for field in old_data if old_data[field] != new_data[field]
        }
        logger.info(f"Admin {self.request.user} a modifié l'utilisateur {self.get_object().id}. Modifications : {changed_fields}")