# GitHub Actions CI/CD - AgriMarket

Ce projet utilise un pipeline GitHub Actions avec les etapes suivantes:

1. build
2. test
3. quality (SonarQube)
4. package (push image vers GHCR)
5. canary
6. deploy
7. performance

## Workflow

Le workflow principal est defini dans `.github/workflows/ci-cd.yml`.

- `build`: verifie migrations/check Django
- `test`: execute pytest + couverture
- `quality`: scan SonarQube + Quality Gate
- `package`: build et push Docker image sur GHCR
- `canary`: smoke test sur URL canary
- `deploy`: deploiement distant via SSH + docker compose
- `performance`: test de perf rapide avec k6

## Secrets GitHub requis

Configurer ces secrets dans `Settings > Secrets and variables > Actions`:

- `SONAR_TOKEN`: token SonarQube
- `SONAR_HOST_URL`: URL SonarQube (ex: https://sonar.votre-domaine.com)
- `CANARY_URL`: URL a verifier en canary (optionnel)
- `DEPLOY_HOST`: hote SSH de deploiement (optionnel)
- `DEPLOY_USER`: utilisateur SSH (optionnel)
- `DEPLOY_SSH_KEY`: cle privee SSH (optionnel)
- `DEPLOY_PATH`: chemin du projet sur le serveur (optionnel)
- `PERFORMANCE_URL`: URL cible des tests performance (optionnel)

## Permissions GHCR

Le job `package` utilise `GITHUB_TOKEN` avec permission `packages: write` pour pousser sur:

- `ghcr.io/<owner>/<repo>`

## Notes de deploiement

Le compose de production utilise:

- `CONTAINER_IMAGE` (par defaut: `ghcr.io/goliti/agrimarket`)
- `IMAGE_TAG` (par defaut: `latest`)

Sur le serveur, verifier que Docker et Docker Compose sont installes et que le fichier `.env` contient les variables necessaires (DB, SECRET_KEY, etc.).
