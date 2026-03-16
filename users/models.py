from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        PRODUCTEUR = 'producteur', 'Producteur'
        CLIENT = 'client', 'Client'
        ADMIN = 'admin', 'Administrateur'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
    )
    ville = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    photo_profil = models.ImageField(upload_to='profils/', null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        verbose_name = 'utilisateur'
        verbose_name_plural = 'utilisateurs'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
        ]

    def is_producteur(self):
        return self.role == self.Role.PRODUCTEUR

    def is_client(self):
        return self.role == self.Role.CLIENT

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'