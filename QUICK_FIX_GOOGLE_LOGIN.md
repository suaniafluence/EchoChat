# 🚨 Quick Fix: Google Login Button Missing in Production

## Le Problème

Le bouton de connexion Google ne s'affiche pas car votre service systemd ne définit pas les variables `NEXTAUTH_SECRET`, `GOOGLE_CLIENT_ID`, et `GOOGLE_CLIENT_SECRET`.

Votre service actuel a seulement :
```
Environment=NODE_ENV=production
Environment=PORT=3001
```

Il manque toutes les variables NextAuth et Google OAuth !

## La Solution en 4 Étapes

### Étape 1 : Éditez le fichier service

```bash
sudo nano /etc/systemd/system/echochat-frontend.service
```

**Remplacez TOUT le contenu par :**

```ini
[Unit]
Description=EchoChat Frontend (Next.js)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/echochat/frontend
ExecStart=/usr/bin/node /opt/echochat/frontend/.next/standalone/server.js
Restart=always
RestartSec=5

# Node Environment
Environment=NODE_ENV=production
Environment=PORT=3001

# API URL
Environment=NEXT_PUBLIC_API_URL=http://localhost:8001

# NextAuth Configuration
Environment=NEXTAUTH_SECRET=REMPLACEZ_PAR_VOTRE_SECRET
Environment=NEXTAUTH_URL=https://echochat.iafluence.cloud

# Google OAuth Configuration
Environment=GOOGLE_CLIENT_ID=REMPLACEZ_PAR_VOTRE_CLIENT_ID.apps.googleusercontent.com
Environment=GOOGLE_CLIENT_SECRET=REMPLACEZ_PAR_VOTRE_CLIENT_SECRET

# Admin Email Whitelist
Environment=ALLOWED_ADMIN_EMAILS=suan.tay.job@gmail.com,j.wallut.pro@gmail.com

[Install]
WantedBy=multi-user.target
```

**⚠️ IMPORTANT : Remplacez les valeurs suivantes avec vos vraies valeurs du fichier `/opt/echochat/frontend/.env.production` :**

- `NEXTAUTH_SECRET` : Votre secret NextAuth
- `GOOGLE_CLIENT_ID` : Votre client ID Google (se termine par `.apps.googleusercontent.com`)
- `GOOGLE_CLIENT_SECRET` : Votre secret Google OAuth

### Étape 2 : Vérifiez vos vraies valeurs

Pour copier les bonnes valeurs :

```bash
cat /opt/echochat/frontend/.env.production
```

Copiez les valeurs de `NEXTAUTH_SECRET`, `GOOGLE_CLIENT_ID`, et `GOOGLE_CLIENT_SECRET`.

### Étape 3 : Rebuild le frontend

**CRUCIAL** : Next.js a besoin de ces variables au moment du build !

```bash
cd /opt/echochat/frontend

# Définissez les variables temporairement pour le build
export NEXTAUTH_SECRET="votre-secret"
export NEXTAUTH_URL="https://echochat.iafluence.cloud"
export GOOGLE_CLIENT_ID="votre-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="votre-secret"
export NEXT_PUBLIC_API_URL="http://localhost:8001"

# Rebuild
npm run build
```

**OU** si vous préférez une seule commande :

```bash
cd /opt/echochat/frontend
source /opt/echochat/frontend/.env.production
npm run build
```

### Étape 4 : Redémarrez le service

```bash
# Recharger la configuration systemd
sudo systemctl daemon-reload

# Redémarrer le service frontend
sudo systemctl restart echochat-frontend

# Vérifier le statut
sudo systemctl status echochat-frontend
```

## ✅ Vérification

### 1. Testez l'API NextAuth

```bash
curl http://localhost:3001/api/auth/providers
```

**Résultat attendu** (vous devez voir le provider Google) :
```json
{
  "google": {
    "id": "google",
    "name": "Google",
    "type": "oauth",
    "signinUrl": "http://localhost:3001/api/auth/signin/google",
    "callbackUrl": "http://localhost:3001/api/auth/callback/google"
  }
}
```

**Résultat problématique** (objet vide = variables pas chargées) :
```json
{}
```

### 2. Testez dans le navigateur

Allez sur : `https://echochat.iafluence.cloud/auth/signin`

Vous devriez voir le bouton **"Continuer avec Google"** ! 🎉

## 🔧 Dépannage

### Le bouton n'apparaît toujours pas

1. **Vérifiez les logs** :
   ```bash
   sudo journalctl -u echochat-frontend -n 50
   ```

2. **Vérifiez que les variables sont chargées** :
   ```bash
   sudo systemctl show echochat-frontend | grep Environment
   ```

   Vous devez voir toutes les variables listées.

3. **Vérifiez qu'il n'y a pas d'erreurs au build** :
   ```bash
   cd /opt/echochat/frontend
   npm run build 2>&1 | grep -i error
   ```

### Erreur "redirect_uri_mismatch" après avoir cliqué sur Google

Vérifiez dans [Google Cloud Console](https://console.cloud.google.com/apis/credentials) que vous avez ajouté exactement cette URI :
```
https://echochat.iafluence.cloud/api/auth/callback/google
```

### Erreur "Access Denied" après connexion Google

Vérifiez que votre email est bien dans la liste `ALLOWED_ADMIN_EMAILS` du service.

## 📝 Note Importante

Les variables d'environnement doivent être disponibles à DEUX moments :

1. **Au moment du BUILD** (`npm run build`) : Next.js compile les pages
2. **Au moment du RUN** (service systemd) : Le serveur a besoin des variables

C'est pourquoi vous devez :
- Exporter les variables avant `npm run build`
- Les définir dans le service systemd

## 🎯 Résumé des commandes

```bash
# 1. Éditez le service avec vos vraies valeurs
sudo nano /etc/systemd/system/echochat-frontend.service

# 2. Rebuild avec les variables
cd /opt/echochat/frontend
export $(cat .env.production | xargs)
npm run build

# 3. Redémarrez
sudo systemctl daemon-reload
sudo systemctl restart echochat-frontend

# 4. Testez
curl http://localhost:3001/api/auth/providers
```

Vous devriez maintenant voir le bouton Google ! 🚀
