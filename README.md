# AgriMarket API

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/django-6.0.2-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.16.1-red.svg)
[![pipeline status](https://gitlab.com/marcgoliti/agrimarket/badges/main/pipeline.svg)](https://gitlab.com/marcgoliti/agrimarket/-/commits/main)
[![coverage report](https://gitlab.com/marcgoliti/agrimarket/badges/main/coverage.svg)](https://gitlab.com/marcgoliti/agrimarket/-/commits/main)
[![Docker Hub](https://img.shields.io/badge/docker-hub-blue?logo=docker)](https://hub.docker.com/r/marco225/agrimarket)

API REST sécurisée pour la gestion d'un marché agricole, permettant la mise en relation entre producteurs et clients, la gestion des produits, des commandes et des paiements.

> 🚀 **CI/CD activé** - Pipeline automatisé avec GitLab CI/CD  
> 🐳 **Docker Hub** - Image disponible sur Docker Hub  
> ✅ **Tests complets** - Couverture de code avec pytest

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Technologies](#-technologies)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Utilisation](#-utilisation)
- [Documentation API](#-documentation-api)
- [Tests](#-tests)
- [Structure du projet](#-structure-du-projet)
- [Sécurité](#-sécurité)

---

## ✨ Fonctionnalités

### 🔐 Gestion des utilisateurs
- **Inscription et authentification** avec JWT (access + refresh tokens)
- **3 types d'utilisateurs** : Client, Producteur, Administrateur
- **Gestion de profil** : mise à jour, photo de profil, suppression de compte
- **Permissions granulaires** : chaque utilisateur ne peut modifier que son propre profil

### 🛒 Gestion des produits
- **CRUD complet** pour les produits (réservé aux producteurs)
- **Catégorisation** des produits
- **Gestion de stock** avec protection contre les valeurs négatives
- **Images de produits**
- **Filtres avancés** : par catégorie, producteur, disponibilité, prix

### 📦 Gestion des commandes
- **Création de commandes** avec décrémentation automatique du stock
- **Transactions atomiques** pour garantir la cohérence des données
- **Suivi des statuts** : En attente, Confirmée, Expédiée, Livrée, Annulée
- **Annulation possible** (si non expédiée)
- **Permissions** : client propriétaire, producteur concerné, ou admin

### 💳 Gestion des paiements
- **Simulation de paiement** (Mobile Money, Carte Bancaire, Espèces, Virement)
- **Référence de transaction** unique
- **Statuts de paiement** : En attente, Réussie, Échouée, Remboursée
- **Validation par l'administrateur**

### 📊 Tableau de bord
- **Dashboard Producteur** : statistiques sur produits, commandes, revenus
- **Dashboard Admin** : statistiques globales de la plateforme

---

## 🛠 Technologies

- **Backend** : Django 6.0.2
- **API** : Django REST Framework 3.16.1
- **Authentification** : JWT (djangorestframework-simplejwt)
- **Base de données** : SQLite (développement) / PostgreSQL (production)
- **Documentation** : drf-spectacular (Swagger/ReDoc)
- **Tests** : pytest, pytest-django, factory_boy
- **Validation** : django-filter, ruff
- **CI/CD** : GitLab CI/CD Pipeline
- **Conteneurisation** : Docker & Docker Compose
- **Serveur** : Gunicorn

---

## 🚀 Installation

### Prérequis
- Python 3.11 ou supérieur
- pip
- virtualenv (recommandé)

### Étapes

1. **Cloner le dépôt**
```bash
git clone https://github.com/votre-repo/agrimarket.git
cd agrimarket
```

2. **Créer et activer l'environnement virtuel**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Appliquer les migrations**
```bash
python manage.py migrate
```

5. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

6. **Lancer le serveur de développement**
```bash
python manage.py runserver

---

## 🐳 Installation avec Docker

### Prérequis
- Docker
- Docker Compose

### Démarrage rapide

```bash
# 1. Cloner le dépôt
git clone git@gitlab.com:marcgoliti/agrimarket.git
cd agrimarket

# 2. Copier le fichier d'environnement
cp .env.example .env

# 3. Démarrer les services
docker-compose up -d

# 4. Appliquer les migrations
docker-compose exec web python manage.py migrate

# 5. Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser

# 6. Accéder à l'API
# http://localhost:8000
```

### Commandes Docker utiles

```bash
# Voir les logs
docker-compose logs -f web

# Redémarrer les services
docker-compose restart

# Arrêter les services
docker-compose down

# Reconstruire après modification
docker-compose up -d --build

# Exécuter les tests
docker-compose exec web pytest
```
```

L'API sera accessible sur `http://localhost:8000`

### 🚀 Déploiement avec Docker Hub

Pour la production, utilisez l'image pré-construite depuis Docker Hub :

```bash
# 1. Pull de l'image
docker pull marco225/agrimarket:latest

# 2. Démarrer avec docker-compose en production
docker-compose -f docker-compose.prod.yml up -d

# 3. Migrations et setup initial
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

📖 **Guide complet** : Voir [docs/DOCKER_HUB_DEPLOYMENT.md](docs/DOCKER_HUB_DEPLOYMENT.md) pour plus de détails

---

## ⚙️ Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
SECRET_KEY=votre-cle-secrete-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT
JWT_SIGNING_KEY=votre-cle-jwt-secrete

# Base de données (PostgreSQL en production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=agrimarket
DB_USER=postgres
DB_PASSWORD=votre-mot-de-passe
DB_HOST=localhost
DB_PORT=5432
```

### Configuration JWT

Les tokens JWT sont configurés dans `config/settings.py` :
- **Access Token** : 15 minutes
- **Refresh Token** : 7 jours
- **Rotation automatique** des refresh tokens
- **Blacklist** après rotation

---

## 📖 Utilisation

### Authentification

1. **Inscription**
```bash
POST /api/auth/register/
{
  "username": "producteur1",
  "email": "producteur@example.com",
  "password": "MotDePasse123!",
  "password2": "MotDePasse123!",
  "role": "producteur",
  "ville": "Abidjan",
  "telephone": "0123456789"
}
```

2. **Connexion**
```bash
POST /api/auth/login/
{
  "username": "producteur1",
  "password": "MotDePasse123!"
}

# Réponse
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

3. **Utiliser le token**
```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Exemples d'endpoints

#### Produits
```bash
GET    /api/produits/                    # Liste des produits
GET    /api/produits/{id}/               # Détail d'un produit
POST   /api/produits/                    # Créer un produit (producteur)
PATCH  /api/produits/{id}/               # Modifier un produit (propriétaire)
DELETE /api/produits/{id}/               # Supprimer un produit (propriétaire)
GET    /api/produits/mes-produits/       # Mes produits (producteur)
```Tests avec Docker
```bash
docker-compose exec web pytest --cov
```

### Structure des tests

- **Tests unitaires** : modèles, serializers, services
- **Tests d'intégration** : endpoints API, permissions
- **Tests de règles métier** : transactions, stock, validations

---

## 🔄 CI/CD Pipeline

Le projet utilise **GitLab CI/CD** avec un pipeline automatisé en 4 stages :

### Pipeline Stages

1. **Lint** : Vérification de la qualité du code (Ruff, Django check)
2. **Test** : Exécution des tests avec couverture de code
3. **Build** : Construction de l'image Docker et vérification des migrations
4. **Deploy** : Déploiement en staging/production (manuel)

### Workflow Git

```bash
# Branche de fonctionnalité
git checkout -b feature/ma-fonctionnalite
git push -u origin feature/ma-fonctionnalite
# → Le pipeline s'exécute automatiquement

# Merge Request → Tests automatiques
# Merge vers develop → Déploiement staging (manuel)
# Merge vers main → Déploiement production (manuel)
```

### Configuration

Consultez [CICD_GUIDE.md](CICD_GUIDE.md) pour :
- Configuration des variables GitLab
- Personnalisation du pipeline
- Processus de déploiement
- Dépannage

---

## 📦 Déploiement

### Déploiement manuel

1. **Configurer les variables d'environnement**
   ```bash
   cp .env.example .env
   # Éditer .env avec vos valeurs de production
   ```

2. **Collecter les fichiers statiques**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Appliquer les migrations**
   ```bash
   python manage.py migrate
   ```

4. **Démarrer avec Gunicorn**
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```

### Déploiement avec Docker

```bash
# Build l'image
docker build -t agrimarket:latest .

# Lancer le conteneur
docker run -p 8000:8000 \
  --env-file .env \
  agrimarket:latest
```

### Variables d'environnement requises

Voir [.env.example](.env.example) pour la liste complète des variables.
POST   /api/commandes/                   # Créer une commande
GET    /api/commandes/{id}/              # Détail d'une commande
POST   /api/commandes/{id}/annuler/      # Annuler une commande
POST   /api/commandes/{id}/update_status/ # Changer statut (admin)
```

#### Dashboard
```bash
GET    /api/dashboard/producteur/        # Stats producteur
GET    /api/dashboard/admin/             # Stats admin
```

---

## 📚 Documentation API

La documentation interactive est disponible aux URLs suivantes :

- **Swagger UI** : http://localhost:8000/api/docs/
- **ReDoc** : http://localhost:8000/api/redoc/
- **Schéma OpenAPI** : http://localhost:8000/api/schema/

---

## 🧪 Tests

### Lancer tous les tests
```bash
pytest
```

### Avec couverture de code
```bash
pytest --cov=. --cov-report=html
```

### Tests par application
```bash
pytest users/tests.py
pytest products/tests.py
pytest orders/tests.py
pytest payments/tests.py
pytest dashboard/tests.py
```

### Structure des tests

- **Tests unitaires** : modèles, serializers, services
- **Tests d'intégration** : endpoints API, permissions
- **Tests de règles métier** : transactions, stock, validations

---

## 📁 Structure du projet

```
agrimarket/
├── config/                 # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                  # Gestion des utilisateurs
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   └── tests.py
├── products/               # Gestion des produits
│   ├── models.py
│   ├── serializers.py
│  x] API REST complète avec DRF
- [x] Authentification JWT sécurisée
- [x] Tests automatisés (248 tests)
- [x] Documentation Swagger/ReDoc
- [x] Pipeline CI/CD GitLab
- [x] Conteneurisation Docker
- [ ] Intégration réelle de paiement mobile (Orange Money, MTN Mobile Money)
- [ ] Notifications email/SMS pour les commandes
- [ ] Système de notation des produits
- [ ] Chat en temps réel producteur-client
- [ ] Application mobile (Flutter/React Native)
- [ ] Analytics avancés pour les producteurs
- [ ] Déploiement cloud (AWS/Azure/GCP)
- [ ] Monitoring avec Sentry/DataDog
│   ├── service.py          # Logique métier
│   ├── permissions.py
│   └── tests.py
├── payments/               # Gestion des paiements
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   └── tests.py
├── dashboard/              # Tableau de bord
│   ├── views.py
│   ├── services.py
│   ├── serializers.py
│   └── tests.py
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🔒 Sécurité

### Authentification
- **JWT sécurisé** avec rotation et blacklist
- **Algorithme HS256** pour la signature
- **Durée de vie limitée** des tokens

### Permissions
- **Permissions personnalisées** pour chaque ressource
- **IsOwnerOrAdmin** : modification de profil
- **IsProducteurOrReadOnly** : gestion des produits
- **IsClientOwnerOrAdmin** : gestion des commandes
- **IsPaymentOwnerOrAdmin** : gestion des paiements

### Protection des données
- **Throttling** : limitation du nombre de requêtes
  - Anonymes : 100/jour
  - Authentifiés : 2000/jour
  - Inscription : 10/heure
- **Validation stricte** des données entrantes
- **Transactions atomiques** pour les opérations critiques
- **CORS configuré** pour sécuriser les origines

### Bonnes pratiques
- Pas de données sensibles dans les logs
- Validation des fichiers uploadés (taille, type)
- Protection contre les injections SQL (ORM Django)
- CSRF protection activée

---

## 👥 Contributeurs

- Développeur principal : MARC GOLITI

---

## 📄 Licence

---

## 🤝 Support

Pour toute question ou problème :
- Créer une issue sur GitHub
- Consulter la documentation API
- Contacter l'équipe de développement

---

## 🎯 Roadmap

- [ ] Intégration réelle de paiement mobile (Orange Money, MTN Mobile Money)
- [ ] Notifications email/SMS pour les commandes
- [ ] Système de notation des produits
- [ ] Chat en temps réel producteur-client
- [ ] Application mobile (Flutter/React Native)
- [ ] Analytics avancés pour les producteurs
- [ ] Déploiement sur cloud (AWS/Azure/GCP)
