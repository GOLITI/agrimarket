# 🐳 Guide de déploiement avec Docker Hub

Ce guide explique comment déployer AgriMarket API en utilisant l'image Docker publiée sur Docker Hub.

---

## 📋 Prérequis

- Docker et Docker Compose installés
- Un serveur (VPS, cloud, etc.) avec accès SSH
- Variables d'environnement configurées

---

## 🚀 Déploiement rapide

### 1. Pull de l'image depuis Docker Hub

```bash
# Connectez-vous à Docker Hub (si image privée)
docker login

# Pull de la dernière version
docker pull marco225/agrimarket:latest

# Ou une version spécifique
docker pull marco225/agrimarket:abc1234
```

### 2. Création du fichier `.env`

Créez un fichier `.env` sur votre serveur :

```bash
# Variables Django
SECRET_KEY=votre-secret-key-super-securise
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# JWT
JWT_SIGNING_KEY=votre-cle-jwt-tres-secrete

# Base de données
DB_NAME=agrimarket
DB_USER=postgres
DB_PASSWORD=mot-de-passe-securise-postgres
DATABASE_URL=postgresql://postgres:mot-de-passe@db:5432/agrimarket

# Docker Hub (pour les mises à jour)
DOCKER_HUB_IMAGE=marco225/agrimarket

# URLs CORS
CORS_ALLOWED_ORIGINS=https://votre-frontend.com
```

### 3. Démarrage avec Docker Compose

```bash
# Utiliser le fichier production
docker-compose -f docker-compose.prod.yml up -d

# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs -f web

# Vérifier le statut
docker-compose -f docker-compose.prod.yml ps
```

### 4. Migrations et configuration initiale

```bash
# Exécuter les migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Créer un superutilisateur
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Collecter les fichiers statiques
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 🔄 Mise à jour de l'application

### Méthode 1 : Via GitLab CI/CD (automatique)

1. Push votre code sur la branche `main`
2. Le pipeline CI/CD se déclenche automatiquement
3. Une fois les tests passés, déclenchez manuellement le job `package:docker`
4. L'image est publiée sur Docker Hub

### Méthode 2 : Manuelle sur le serveur

```bash
# Pull de la nouvelle version
docker-compose -f docker-compose.prod.yml pull web

# Redémarrage avec la nouvelle image
docker-compose -f docker-compose.prod.yml up -d web

# Migrations (si nécessaire)
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Redémarrage pour appliquer les changements
docker-compose -f docker-compose.prod.yml restart web
```

---

## 🏷️ Gestion des versions

### Tags disponibles

- `latest` : Dernière version stable (branch main)
- `abc1234` : Version spécifique (commit SHA court)
- `build-12345` : Build spécifique (pipeline ID)

### Utilisation d'une version spécifique

Modifiez `docker-compose.prod.yml` :

```yaml
services:
  web:
    image: marco225/agrimarket:abc1234  # Version spécifique
    # ou
    image: marco225/agrimarket:latest   # Dernière version
```

---

## 📊 Monitoring et logs

### Voir les logs en temps réel

```bash
# Tous les services
docker-compose -f docker-compose.prod.yml logs -f

# Seulement Django
docker-compose -f docker-compose.prod.yml logs -f web

# Dernières 100 lignes
docker-compose -f docker-compose.prod.yml logs --tail=100 web
```

### Vérifier la santé des containers

```bash
# Status de tous les services
docker-compose -f docker-compose.prod.yml ps

# Infos détaillées
docker inspect agrimarket_web_prod

# Utilisation des ressources
docker stats agrimarket_web_prod
```

---

## 🔐 Sécurité

### Configuration HTTPS

1. Générez des certificats SSL (Let's Encrypt recommandé)
2. Placez les certificats dans `./ssl/`
3. Décommentez la section HTTPS dans `nginx.conf`
4. Redémarrez nginx :

```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

### Secrets et variables sensibles

**Ne jamais** commit les fichiers `.env` dans Git !

Utilisez Docker secrets pour les environnements de production :

```bash
# Créer un secret
echo "ma-clef-secrete" | docker secret create django_secret_key -

# Utiliser dans docker-compose
services:
  web:
    secrets:
      - django_secret_key
```

---

## 🛠️ Dépannage

### L'application ne démarre pas

```bash
# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs web

# Vérifier la connexion à la DB
docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell
```

### Erreur de connexion à PostgreSQL

```bash
# Vérifier que DB est démarrée
docker-compose -f docker-compose.prod.yml ps db

# Tester la connexion
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d agrimarket
```

### Permissions sur les volumes

```bash
# Fixer les permissions
docker-compose -f docker-compose.prod.yml exec web chown -R django:django /app/media
```

---

## 📝 Commandes utiles

```bash
# Entrer dans le container
docker-compose -f docker-compose.prod.yml exec web sh

# Exécuter des commandes Django
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Backup de la base de données
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres agrimarket > backup.sql

# Restaurer un backup
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres agrimarket < backup.sql

# Nettoyer les anciennes images
docker image prune -a
```

---

## 🌐 Configuration du domaine

### DNS

Pointez votre domaine vers l'IP de votre serveur :

```
A     @              123.456.789.0
A     www            123.456.789.0
```

### Nginx

Modifiez `nginx.conf` pour ajouter votre `server_name` :

```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;
    # ...
}
```

---

## 📞 Support

Pour toute question :
- Consultez les logs : `docker-compose -f docker-compose.prod.yml logs`
- Vérifiez la documentation : [docs/CICD_GUIDE.md](CICD_GUIDE.md)
- Contactez l'équipe de développement

---

**🎯 Bonne mise en production !**
