# Guide de mise en place du Pipeline CI/CD

## 📋 Configuration du Pipeline GitLab CI/CD

Votre pipeline est configuré selon les **4 étapes de l'intégration continue** :

### 🏗️ Étape 1 : BUILD - Compilation et intégration du code
**Objectif** : Vérifier que le code compile et s'intègre correctement

- **build:install** : Installation des dépendances Python
- **build:check** : Vérification de la configuration Django
- **build:migrations** : Vérification et application des migrations
- **build:collectstatic** : Collecte des fichiers statiques

### 🧪 Étape 2 : TEST - Tests du code
**Objectif** : Exécuter tous les tests automatisés

- **test:users** : Tests de l'app users
- **test:products** : Tests de l'app products
- **test:orders** : Tests de l'app orders
- **test:payments** : Tests de l'app payments
- **test:dashboard** : Tests de l'app dashboard
- **test:integration** : Tests d'intégration avec couverture globale
- **test:performance** : Tests de performance (manuel)

### 📊 Étape 3 : QUALITY - Mesure de la qualité du code
**Objectif** : Analyser et garantir la qualité du code

- **quality:lint** : Analyse statique avec Ruff (PEP8, erreurs)
- **quality:coverage** : Mesure de la couverture de code (minimum 70%)
- **quality:security** : Audit de sécurité avec Safety et Bandit
- **quality:complexity** : Analyse de la complexité avec Radon

### 📦 Étape 4 : PACKAGE - Gestion des livrables
**Objectif** : Créer et gérer les artefacts de l'application

- **package:docs** : Génération de la documentation OpenAPI
- **package:docker** : Construction de l'image Docker
- **package:release** : Création de releases GitLab (tags)
- **package:archive** : Archivage des artefacts de production
- **deploy:staging** : Déploiement en staging (manuel)
- **deploy:production** : Déploiement en production (manuel)

---

## ⚙️ Configuration GitLab

### 1. Variables d'environnement GitLab

Allez dans **Settings > CI/CD > Variables** et ajoutez :

```
# Pour Docker Hub
DOCKER_HUB_USER = marco225
DOCKER_HUB_TOKEN = votre-access-token-dockerhub
DOCKER_HUB_IMAGE = marco225/agrimarket

# Pour le déploiement
SECRET_KEY = votre-secret-key-django
JWT_SIGNING_KEY = votre-jwt-signing-key
DATABASE_URL = postgresql://user:pass@host:5432/dbname

# Pour la production
PRODUCTION_SERVER = votre-serveur.com
PRODUCTION_SSH_KEY = votre-cle-ssh-privee (type: File)
```

**Note importante** : Pour créer un Access Token Docker Hub :
1. Connectez-vous sur [Docker Hub](https://hub.docker.com)
2. Allez dans **Account Settings > Security > New Access Token**
3. Créez un token avec les permissions **Read & Write**
4. Copiez le token (vous ne pourrez plus le voir après)

### 2. Créer un repository Docker Hub

1. Connectez-vous sur [Docker Hub](https://hub.docker.com)
2. Cliquez sur **Create Repository**
3. Nommez-le `agrimarket` (ou autre nom)
4. Configurez la visibilité (Public ou Private)
5. Le nom complet sera : `votre-username/agrimarket`

5. Le nom complet sera : `votre-username/agrimarket`

### 3. Configurer les Runners

GitLab utilise des runners partagés par défaut. Pour des runners dédiés :

1. Allez dans **Settings > CI/CD > Runners**
2. Suivez les instructions pour installer un runner

---

## 🐳 Utilisation Docker

### Développement local avec Docker

```bash
# Construire et démarrer les services
docker-compose up -d

# Voir les logs
docker-compose logs -f web

# Exécuter des commandes dans le conteneur
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Arrêter les services
docker-compose down

# Reconstruire après modification
docker-compose up -d --build
```

### Build manuel de l'image Docker

```bash
# Construire l'image
docker build -t agrimarket:latest .

# Lancer le conteneur
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret \
  -e DATABASE_URL=postgresql://... \
  agrimarket:latest
```

---

## 🚀 Workflow Git

### Branches principales

- **main** : Production (déploiement manuel)
- **develop** : Staging (déploiement manuel)
- **feature/*** : Fonctionnalités (tests automatiques)
- **hotfix/*** : Corrections urgentes

### Processus de développement

```bash
# 1. Créer une branche de fonctionnalité
git checkout -b feature/nouvelle-fonctionnalite

# 2. Développer et commiter
git add .
git commit -m "feat: ajout de la nouvelle fonctionnalité"

# 3. Pousser vers GitLab
git push -u origin feature/nouvelle-fonctionnalite

# 4. Créer une Merge Request sur GitLab
# Le pipeline s'exécute automatiquement

# 5. Après validation, merger dans develop
# Tests en staging

# 6. Merger develop dans main pour la production
```

---

## 📊 Visualisation des résultats

### Visualisation des résultats

### Pipeline Overview

Chaque étape du pipeline est visualisée dans GitLab :

```
BUILD (Compilation)
  ├─ install      ✅ Installation dépendances
  ├─ check        ✅ Vérification Django
  ├─ migrations   ✅ Vérification migrations
  └─ collectstatic ✅ Fichiers statiques

TEST (Tests)
  ├─ users        ✅ Tests users
  ├─ products     ✅ Tests products  
  ├─ orders       ✅ Tests orders
  ├─ payments     ✅ Tests payments
  ├─ dashboard    ✅ Tests dashboard
  └─ integration  ✅ Tests d'intégration (+ coverage)

QUALITY (Qualité)
  ├─ lint         ✅ Analyse statique (Ruff)
  ├─ coverage     ✅ Couverture ≥ 70%
  ├─ security     ✅ Audit sécurité (Safety + Bandit)
  └─ complexity   ✅ Complexité du code (Radon)

PACKAGE (Livrables)
  ├─ docs         ✅ Documentation OpenAPI
  ├─ docker       🔵 Build Docker (manuel)
  ├─ release      🔵 Release GitLab (tags)
  ├─ archive      ✅ Archive production
  ├─ staging      🔵 Deploy staging (manuel)
  └─ production   🔵 Deploy production (manuel)
```

### Coverage Reports

Les rapports de couverture sont disponibles dans :
- **CI/CD > Pipelines > [votre pipeline] > Tests**
- Artefacts téléchargeables (htmlcov/)

### Badges GitLab

Ajoutez ces badges à votre README :

```markdown
[![pipeline status](https://gitlab.com/marcgoliti/agrimarket/badges/main/pipeline.svg)](https://gitlab.com/marcgoliti/agrimarket/-/commits/main)
[![coverage report](https://gitlab.com/marcgoliti/agrimarket/badges/main/coverage.svg)](https://gitlab.com/marcgoliti/agrimarket/-/commits/main)
```

---

## 🔧 Personnalisation du Pipeline

### Modifier les jobs

Éditez le fichier `.gitlab-ci.yml` pour :

- Ajouter/supprimer des stages
- Modifier les commandes de test
- Changer les déclencheurs (only/except)
- Ajuster les artefacts conservés

### Désactiver des jobs

Ajoutez `when: manual` pour exécution manuelle :

```yaml
test:coverage:
  when: manual
```

---

## 📝 Checklist de déploiement

Avant de pousser vers GitLab :

- [ ] Tests passent localement : `pytest`
- [ ] Linting OK : `ruff check .`
- [ ] Migrations à jour : `python manage.py makemigrations --check`
- [ ] Variables d'environnement configurées dans GitLab
- [ ] `.env` ajouté au `.gitignore`
- [ ] Documentation à jour

---

## 🆘 Dépannage

### Pipeline échoue sur les tests

```bash
# Vérifier localement
pytest -v

# Vérifier les dépendances
pip install -r requirements.txt
```

### Problème de connexion PostgreSQL

Vérifiez les variables dans `.gitlab-ci.yml` :
- `POSTGRES_HOST=postgres`
- `DATABASE_URL` correctement formaté

### Docker build échoue

```bash
# Tester localement
docker build -t test .

# Vérifier .dockerignore
# Vérifier les paths dans Dockerfile
```

---

## 📚 Ressources

- [Documentation GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
- [GitLab Container Registry](https://docs.gitlab.com/ee/user/packages/container_registry/)
- [Docker Documentation](https://docs.docker.com/)
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)

---

## 🎯 Prochaines étapes

1. **Pousser le code vers GitLab**
2. **Configurer les variables d'environnement**
3. **Vérifier le premier pipeline**
4. **Configurer le déploiement**
5. **Ajouter les badges au README**
