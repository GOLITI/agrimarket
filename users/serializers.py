from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password],
        # Pour le navigateur(affiche des points au lieu du texte)
        style={'input_type': 'password'} 
    )
    password2 = serializers.CharField(
        write_only=True, 
        label='Confirmer le mot de passe',
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'ville', 'region', 'telephone', 'password', 'password2',
        ]
        extra_kwargs = {
             # L'email est obligatoire pour l'inscription
            'email': {'required': True},
             # Le username est obligatoire pour l'inscription 
            'username': {'required': True},
        }

    def validate_email(self, value):
        """Vérifier que l'email n'est pas déjà utilisé"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value

    def validate_username(self, value):
        """Vérifier que le username n'est pas déjà utilisé"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value

    def validate(self, attrs):
        # Vérifier que les mots de passe correspondent
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({
                'password': 'Les mots de passe ne correspondent pas.',
                'password2': 'Les mots de passe ne correspondent pas.'
            })
        return attrs

    def create(self, validated_data):
        """Créer l'utilisateur avec le mot de passe hashé"""
        user = User.objects.create_user(**validated_data)
        return user
    

class UserProfileSerializer(serializers.ModelSerializer):
    # Champ calculé pour afficher le nom complet
    full_name = serializers.SerializerMethodField()
    # Afficher le rôle en texte lisible
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'ville', 'region', 'telephone', 'bio', 
            'photo_profil', 'date_joined', 'last_login',
        ]
        # Certains champs sont en lecture seule pour éviter les modifications non autorisées
        read_only_fields = ['id', 'role', 'date_joined', 'last_login', 'role_display']
        # Certains champs sont optionnels pour la mise à jour du profil
        extra_kwargs = {
            'photo_profil': {'required': False},
            'bio': {'required': False},
        }

    def get_full_name(self, obj):
        """Retourner le nom complet ou le username si pas de nom"""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.first_name:
            return obj.first_name
        elif obj.last_name:
            return obj.last_name
        return obj.username

    def validate_photo_profil(self, value):
        """Valider la taille et le type de l'image"""
        if value:
            # Limiter la taille à 3MB
            if value.size > 3 * 1024 * 1024:
                raise serializers.ValidationError("L'image ne doit pas dépasser 3MB.")
            
            # Vérifier le type de fichier
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    "Format d'image non supporté. Utilisez JPEG, PNG ou GIF."
                )
        return value
    

class UserMinimalSerializer(serializers.ModelSerializer):
    """Sérialiseur léger pour les relations imbriquées."""
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'role', 'ville']
    
    def get_display_name(self, obj):
        """Retourne un nom d'affichage court"""
        if obj.first_name:
            return obj.first_name
        return obj.username
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        write_only=True
    )
    new_password2 = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True,
        label='Confirmer le nouveau mot de passe'
    )

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Mot de passe actuel incorrect.')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                'new_password': 'Les nouveaux mots de passe ne correspondent pas.',
                'new_password2': 'Les nouveaux mots de passe ne correspondent pas.'
            })
        
        # Éviter de changer pour le même mot de passe
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({
                'new_password': "Le nouveau mot de passe doit être différent de l'ancien."
            })
        
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    


class UserUpdateSerializer(serializers.ModelSerializer):
    """Pour la mise à jour du profil (sans mot de passe)"""
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'ville', 'region',
            'telephone', 'bio', 'photo_profil'
        ]
    
    def validate_photo_profil(self, value):
        if value and value.size > 3 * 1024 * 1024:
            raise serializers.ValidationError("Image trop grande (max 3MB)")
        return value