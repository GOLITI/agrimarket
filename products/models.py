from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class Category(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'catégorie'
        verbose_name_plural = 'catégories'
        ordering = ['nom']
        
    def __str__(self):
        return self.nom


class Product(models.Model):
    class Unite(models.TextChoices):
        KG = 'kg', 'Kilogramme'
        SAC = 'sac', 'Sac'
        CARTON = 'carton', 'Carton'
        LITRE = 'litre', 'Litre'
        UNITE = 'unite', 'Unité'
        BOTTE = 'botte', 'Botte'

    nom = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    prix = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    stock = models.PositiveIntegerField(default=0)
    unite = models.CharField(max_length=20, choices=Unite.choices, default=Unite.KG)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='produits')
    producteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='produits',
    )
    disponible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'produit'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['producteur', 'disponible']),
            models.Index(fields=['-created_at']),
        ]
    

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nom)
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.nom} — {self.producteur.username}'