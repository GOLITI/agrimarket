# Schéma du Pipeline CI/CD - AgriMarket API

## Vue d'ensemble

```
INTÉGRATION CONTINUE (4 ÉTAPES)
│
├─ 1. BUILD (Compilation et Intégration)
│   ├─ build:install ................ Installation des dépendances
│   ├─ build:check .................. Vérification Django
│   ├─ build:migrations ............. Vérification migrations
│   └─ build:collectstatic .......... Fichiers statiques
│
├─ 2. TEST (Tests automatisés)
│   ├─ test:users ................... Tests app users
│   ├─ test:products ................ Tests app products
│   ├─ test:orders .................. Tests app orders
│   ├─ test:payments ................ Tests app payments
│   ├─ test:dashboard ............... Tests app dashboard
│   ├─ test:integration ............. Tests d'intégration + coverage
│   └─ test:performance ............. Tests de charge (manuel)
│
├─ 3. QUALITY (Mesure de la qualité)
│   ├─ quality:lint ................. Analyse statique (Ruff)
│   ├─ quality:coverage ............. Couverture ≥ 70%
│   ├─ quality:security ............. Audit sécurité (Safety + Bandit)
│   └─ quality:complexity ........... Complexité (Radon)
│
└─ 4. PACKAGE (Gestion des livrables)
    ├─ package:docs ................. Documentation OpenAPI
    ├─ package:docker ............... Image Docker (manuel)
    ├─ package:release .............. Release GitLab (tags)
    ├─ package:archive .............. Archive production
    ├─ deploy:staging ............... Déploiement staging (manuel)
    └─ deploy:production ............ Déploiement production (manuel)
```

## Déclencheurs par branche

### Branche `main` (Production)
✅ BUILD : Tous les jobs  
✅ TEST : Tous les tests + coverage  
✅ QUALITY : Toutes les analyses  
✅ PACKAGE : Tous les jobs disponibles  

### Branche `develop` (Staging)
✅ BUILD : Tous les jobs  
✅ TEST : Tous les tests  
✅ QUALITY : Toutes les analyses  
🔵 PACKAGE : deploy:staging (manuel)  

### Merge Requests
✅ BUILD : build:install, build:check, build:migrations  
✅ TEST : Tous les tests + coverage  
✅ QUALITY : lint, coverage, security  
❌ PACKAGE : Aucun  

### Tags
✅ PACKAGE : docs, release, archive  

## Artefacts générés

| Job | Artefact | Durée | Description |
|-----|----------|-------|-------------|
| build:install | venv/ | 1h | Environnement virtuel |
| build:collectstatic | staticfiles/ | 1 jour | Fichiers statiques |
| test:* | htmlcov/ | 1 semaine | Rapports coverage HTML |
| test:integration | coverage.xml, report.xml | 30 jours | Coverage + JUnit |
| quality:lint | ruff-report.json | 1 semaine | Rapport Ruff |
| quality:security | safety-report.json, bandit-report.json | 1 semaine | Audits sécurité |
| package:docs | schema.yml | 90 jours | Documentation OpenAPI |
| package:archive | agrimarket-*.tar.gz | 6 mois | Archive complète |

## Métriques et seuils

### Couverture de code
- **Minimum** : 70%
- **Objectif** : 80%+
- **Échec si** : < 70%

### Complexité cyclomatique (Radon)
- **A** : 1-5 (Faible) ✅
- **B** : 6-10 (Moyenne) ⚠️
- **C** : 11-20 (Élevée) ⚠️
- **D** : 21-30 (Très élevée) ❌
- **E** : 31-40 (Extrême) ❌
- **F** : 41+ (Instable) ❌

### Maintenabilité (MI)
- **A** : 100-80 (Excellent) ✅
- **B** : 79-60 (Bon) ✅
- **C** : 59-40 (Moyen) ⚠️
- **D** : 39-20 (Faible) ❌
- **F** : < 20 (Très faible) ❌

## Temps d'exécution estimé

| Stage | Durée moyenne | Parallélisation |
|-------|---------------|-----------------|
| BUILD | ~3-5 min | Non |
| TEST | ~5-8 min | Oui (5 jobs) |
| QUALITY | ~2-4 min | Oui (4 jobs) |
| PACKAGE | Variable | Selon jobs activés |

**Total pipeline complet** : ~10-20 minutes

## Environnements

### Staging
- **URL** : https://staging.agrimarket.example.com
- **Branche** : develop
- **Base de données** : PostgreSQL staging
- **Déploiement** : Manuel
- **Tier** : staging

### Production
- **URL** : https://agrimarket.example.com
- **Branche** : main, tags
- **Base de données** : PostgreSQL production
- **Déploiement** : Manuel
- **Tier** : production

## Variables d'environnement requises

### Obligatoires
```yaml
SECRET_KEY              # Clé secrète Django
JWT_SIGNING_KEY         # Clé signature JWT
DATABASE_URL            # URL PostgreSQL
```

### Pour Docker Registry
```yaml
CI_REGISTRY             # registry.gitlab.com
CI_REGISTRY_USER        # Utilisateur registry
CI_REGISTRY_PASSWORD    # Token registry
```

### Pour déploiement
```yaml
PRODUCTION_SERVER       # Serveur de production
PRODUCTION_SSH_KEY      # Clé SSH (type: File)
STAGING_SERVER          # Serveur de staging (optionnel)
```

## Workflow recommandé

```bash
# 1. Créer une branche de fonctionnalité
git checkout -b feature/nouvelle-fonctionnalite

# 2. Développer et commiter
git add .
git commit -m "feat: nouvelle fonctionnalité"

# 3. Pousser et créer une MR
git push -u origin feature/nouvelle-fonctionnalite
# → Pipeline s'exécute (BUILD, TEST, QUALITY)

# 4. Review et ajustements si nécessaire
# → Le pipeline re-exécute à chaque push

# 5. Merger dans develop après validation
# → Pipeline complet + option deploy staging

# 6. Tester en staging

# 7. Merger develop dans main
# → Pipeline complet + options deploy production

# 8. Créer un tag pour release
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
# → Pipeline avec package:release
```
