# 🐳 Configuration Docker Hub - Guide Rapide

Ce guide vous aide à configurer Docker Hub pour votre projet AgriMarket.

---

## 📝 Informations de votre compte

- **Username** : `marco225`
- **Repository** : `marco225/agrimarket`

---

## 🔑 Étape 1 : Créer un Access Token Docker Hub

**⚠️ IMPORTANT** : Pour GitLab CI/CD, n'utilisez **JAMAIS** votre mot de passe directement. Utilisez un **Access Token** qui est :
- Plus sécurisé (peut être révoqué sans changer votre mot de passe)
- Permet des permissions granulaires
- Recommandé par Docker Hub

### Instructions :

1. **Connectez-vous à Docker Hub**
   ```
   https://hub.docker.com/
   ```

2. **Allez dans les paramètres de sécurité**
   - Cliquez sur votre avatar (en haut à droite)
   - Sélectionnez **"Account Settings"**
   - Allez dans l'onglet **"Security"**

3. **Créez un nouveau Access Token**
   - Cliquez sur **"New Access Token"**
   - **Description** : `GitLab CI/CD AgriMarket`
   - **Access permissions** : `Read & Write`
   - Cliquez sur **"Generate"**

4. **Copiez le token**
   - ⚠️ **IMPORTANT** : Copiez le token immédiatement
   - Vous ne pourrez plus le voir après avoir fermé la fenêtre
   - Gardez-le en lieu sûr temporairement

---

## 📦 Étape 2 : Créer le repository Docker Hub

1. **Connectez-vous à Docker Hub**
   ```
   https://hub.docker.com/
   ```

2. **Créez un nouveau repository**
   - Cliquez sur **"Create Repository"**
   - **Namespace** : `marco225` (votre username)
   - **Repository Name** : `agrimarket`
   - **Visibility** : `Public` ou `Private` (selon votre choix)
   - **Description** : `API REST AgriMarket - Gestion marché agricole`
   - Cliquez sur **"Create"**

3. **Vérifiez l'URL du repository**
   ```
   https://hub.docker.com/r/marco225/agrimarket
   ```

---

## ⚙️ Étape 3 : Configurer GitLab CI/CD

1. **Allez dans votre projet GitLab**
   ```
   https://gitlab.com/marcgoliti/agrimarket
   ```

2. **Accédez aux variables CI/CD**
   - Allez dans **Settings** > **CI/CD**
   - Expandez la section **"Variables"**
   - Cliquez sur **"Add variable"**

3. **Ajoutez les 3 variables suivantes**

   **Variable 1 : DOCKER_HUB_USER**
   - **Key** : `DOCKER_HUB_USER`
   - **Value** : `marco225`
   - **Type** : Variable
   - **Environment scope** : All
   - **Protect variable** : ❌ Non
   - **Mask variable** : ✅ Oui
   - Cliquez sur **"Add variable"**

   **Variable 2 : DOCKER_HUB_TOKEN**
   - **Key** : `DOCKER_HUB_TOKEN`
   - **Value** : `[COLLEZ VOTRE ACCESS TOKEN ICI]`
   - **Type** : Variable
   - **Environment scope** : All
   - **Protect variable** : ✅ Oui
   - **Mask variable** : ✅ Oui
   - Cliquez sur **"Add variable"**

   **Variable 3 : DOCKER_HUB_IMAGE**
   - **Key** : `DOCKER_HUB_IMAGE`
   - **Value** : `marco225/agrimarket`
   - **Type** : Variable
   - **Environment scope** : All
   - **Protect variable** : ❌ Non
   - **Mask variable** : ❌ Non
   - Cliquez sur **"Add variable"**

---

## 🧪 Étape 4 : Tester en local

Testez que vous pouvez vous connecter à Docker Hub depuis votre machine :

```bash
# Se connecter à Docker Hub
docker login

# Entrez vos identifiants :
# Username: marco225
# Password: [votre mot de passe]

# Build de l'image localement
docker build -t marco225/agrimarket:test .

# Push de test
docker push marco225/agrimarket:test

# Vérifier sur Docker Hub que l'image est bien uploadée
```

Si tout fonctionne, vous pouvez ensuite supprimer le tag de test :

```bash
# Sur Docker Hub, allez dans le repository et supprimez le tag "test"
```

---

## ✅ Étape 5 : Vérification

Avant de pousser votre code, vérifiez que :

- ✅ Vous avez créé l'Access Token sur Docker Hub
- ✅ Le repository `marco225/agrimarket` existe sur Docker Hub
- ✅ Les 3 variables sont configurées dans GitLab CI/CD
- ✅ Le fichier `.env` n'est PAS versionné dans Git
- ✅ Vous avez testé `docker login` en local

---

## 🚀 Étape 6 : Premier déploiement

```bash
# Stage tous les fichiers
git add .

# Commit
git commit -m "feat: Configuration Docker Hub pour marco225"

# Push vers GitLab
git push origin main
```

Le pipeline GitLab CI/CD va :
1. ✅ Compiler le code (stage: build)
2. ✅ Exécuter les tests (stage: test)
3. ✅ Analyser la qualité (stage: quality)
4. ⏸️ Attendre votre validation pour publier sur Docker Hub (stage: package, job: package:docker)

Dans l'interface GitLab CI/CD :
- Allez dans **CI/CD** > **Pipelines**
- Attendez que les stages build, test et quality soient ✅ verts
- Cliquez sur le job **package:docker** (▶️ bouton play)
- Le job va publier l'image sur Docker Hub

---

## 🎯 Résultat final

Une fois le pipeline terminé, votre image sera disponible sur :

```
https://hub.docker.com/r/marco225/agrimarket
```

Vous pourrez la télécharger avec :

```bash
docker pull marco225/agrimarket:latest
```

---

## 🔒 Sécurité - Bonnes pratiques

1. **Ne jamais commit vos secrets dans Git**
   - ✅ `.env` est dans `.gitignore`
   - ❌ Ne mettez jamais de mots de passe en clair dans le code

2. **Utilisez des Access Tokens**
   - ✅ Access Token pour GitLab CI/CD
   - ✅ Révocable sans changer le mot de passe
   - ✅ Permissions granulaires

3. **Rotation des tokens**
   - Changez vos Access Tokens tous les 6-12 mois
   - Révoquez les tokens non utilisés

4. **Variables GitLab**
   - ✅ Markez les variables sensibles comme "Masked"
   - ✅ Protégez les variables de production

---

## 🆘 Dépannage

### Erreur : "unauthorized: authentication required"

```bash
# Vérifiez que vous êtes bien connecté
docker logout
docker login

# Vérifiez le nom de l'image
docker images | grep marco225
```

### Erreur : "denied: requested access to the resource is denied"

- Vérifiez que le repository `marco225/agrimarket` existe sur Docker Hub
- Vérifiez que vous avez les droits de push

### Pipeline GitLab échoue sur package:docker

- Vérifiez que les 3 variables sont bien configurées dans GitLab
- Vérifiez que l'Access Token est valide
- Consultez les logs du job pour plus de détails

---

**🎉 Configuration terminée ! Vous êtes prêt pour le déploiement continu.**
