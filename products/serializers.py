from rest_framework import serializers
from .models import Category, Product
from users.serializers import UserMinimalSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Sérialiseur pour les catégories avec nombre de produits disponibles."""
    nb_produits = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'nom', 'description', 'nb_produits', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_nb_produits(self, category):
        """Retourne le nombre de produits disponibles dans cette catégorie."""
        return category.produits.filter(disponible=True).count()


class ProductSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les produits.
    - En lecture : affiche le producteur (UserMinimalSerializer) et les noms des catégories.
    - En écriture : reçoit une liste d'IDs de catégories (categorie_ids) pour les associer.
    """
    producteur = UserMinimalSerializer(read_only=True)
    categories = serializers.StringRelatedField(many=True, read_only=True)
    categorie_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        write_only=True,
        required=False,
        help_text="Liste des IDs des catégories à associer au produit."
    )

    class Meta:
        model = Product
        fields = [
            'id', 'nom', 'description', 'prix', 'stock', 'unite',
            'image', 'categories', 'categorie_ids', 'producteur',
            'disponible', 'slug', 'created_at', 'updated_at',
        ]
        read_only_fields = ['producteur', 'slug', 'created_at', 'updated_at', 'categories']
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True},
            'description': {'required': True},
            'prix': {'min_value': 0},  # redondant avec validateur du modèle mais explicite
            'stock': {'min_value': 0},
        }

    def validate_prix(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le prix doit être strictement positif.")
        return value

    def validate_image(self, value):
        """Validation optionnelle de l'image (taille, format)."""
        if value:
            # Limite à 3 Mo
            if value.size > 3 * 1024 * 1024:
                raise serializers.ValidationError("L'image ne doit pas dépasser 3 Mo.")
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Format d'image non supporté (JPEG, PNG, GIF uniquement).")
        return value

    def validate(self, data):
        # si le stock final (existant + modification) est 0, disponible doit être False
        stock = data.get('stock')
        disponible = data.get('disponible')
        
        # Si on modifie le stock, on utilise la nouvelle valeur, sinon celle de l'instance
        if stock is None and self.instance:
            stock = self.instance.stock
        
        # Si on modifie la disponibilité, on utilise la nouvelle, sinon celle de l'instance
        if disponible is None and self.instance:
            disponible = self.instance.disponible
        
        if stock == 0 and disponible is True:
            raise serializers.ValidationError("Un produit avec stock nul ne peut pas être disponible.")
        
        return data

    def create(self, validated_data):
        """Création d'un produit : on extrait les catégories avant création."""
        categories = validated_data.pop('categorie_ids', [])
        product = Product.objects.create(**validated_data)
        if categories:
            product.categories.set(categories)
        return product

    def update(self, instance, validated_data):
        """Mise à jour : on gère les catégories si présentes."""
        categories = validated_data.pop('categorie_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if categories is not None:
            instance.categories.set(categories)
        return instance