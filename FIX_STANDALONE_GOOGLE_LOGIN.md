# 🔧 Fix Google Login for Next.js Standalone Mode

## Le Problème

Votre application utilise Next.js en mode **standalone** (`.next/standalone/server.js`). Ce mode **ne charge PAS automatiquement** les fichiers `.env` !

Même si votre fichier `/opt/echochat/frontend/.env.production` contient toutes les bonnes variables, le serveur standalone les ignore complètement.

## La Solution

Systemd doit charger explicitement le fichier `.env.production` avec la directive `EnvironmentFile`.

### Étape 1 : Vérifiez que le fichier .env.production existe

```bash
ls -la /opt/echochat/frontend/.env.production
cat /opt/echochat/frontend/.env.production
```

Vous devez voir toutes vos variables (NEXTAUTH_SECRET, GOOGLE_CLIENT_ID, etc.)

### Étape 2 : Modifiez le service systemd

```bash
sudo nano /etc/systemd/system/echochat-frontend.service
```

**Remplacez par ce contenu :**

```ini
[Unit]
Description=EchoChat Frontend (Next.js)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/echochat/frontend
EnvironmentFile=/opt/echochat/frontend/.env.production
ExecStart=/usr/bin/node /opt/echochat/frontend/.next/standalone/server.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Ligne clé :** `EnvironmentFile=/opt/echochat/frontend/.env.production`

### Étape 3 : Vérifiez les permissions du fichier

Le service tourne en tant qu'utilisateur `ubuntu`, donc il doit pouvoir lire le fichier :

```bash
sudo chown ubuntu:ubuntu /opt/echochat/frontend/.env.production
sudo chmod 644 /opt/echochat/frontend/.env.production
```

### Étape 4 : Rebuild le frontend (IMPORTANT !)

Next.js a besoin des variables au moment du build, surtout `NEXT_PUBLIC_*` :

```bash
cd /opt/echochat/frontend

# Charger les variables pour le build
export $(cat .env.production | xargs)

# Rebuild avec le mode standalone
npm run build
```

Vérifiez qu'il n'y a pas d'erreurs pendant le build !

### Étape 5 : Redémarrer le service

```bash
# Recharger la configuration systemd
sudo systemctl daemon-reload

# Redémarrer le frontend
sudo systemctl restart echochat-frontend

# Vérifier le statut
sudo systemctl status echochat-frontend
```

Le service doit être **active (running)** avec aucune erreur.

### Étape 6 : Tester !

#### Test 1 : Vérifier que NextAuth voit les providers

```bash
curl http://localhost:3001/api/auth/providers
```

**Résultat attendu :**
```json
{
  "google": {
    "id": "google",
    "name": "Google",
    "type": "oauth",
    "signinUrl": "...",
    "callbackUrl": "..."
  }
}
```

**Si vous voyez `{}`** : Les variables ne sont pas chargées !

#### Test 2 : Vérifier dans le navigateur

Allez sur : `https://echochat.iafluence.cloud/auth/signin`

Le bouton **"Continuer avec Google"** doit apparaître ! ✅

## 🔧 Dépannage

### Problème 1 : Le service ne démarre pas

Vérifiez les logs :
```bash
sudo journalctl -u echochat-frontend -n 50
```

Erreur commune : `Permission denied` sur `.env.production`
→ Solution : `sudo chmod 644 /opt/echochat/frontend/.env.production`

### Problème 2 : `curl` retourne `{}`

Les variables ne sont pas chargées. Vérifiez que systemd voit le fichier :

```bash
sudo systemctl show echochat-frontend | grep EnvironmentFile
```

Vous devez voir : `EnvironmentFile=/opt/echochat/frontend/.env.production (ignore_errors=no)`

Si le fichier n'est pas trouvé, vérifiez le chemin :
```bash
sudo -u ubuntu cat /opt/echochat/frontend/.env.production
```

### Problème 3 : Variables pas chargées malgré EnvironmentFile

**Solution alternative : Définir les variables explicitement**

Éditez le service :
```bash
sudo nano /etc/systemd/system/echochat-frontend.service
```

Au lieu de `EnvironmentFile`, ajoutez toutes les variables :

```ini
[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/echochat/frontend
Environment=NODE_ENV=production
Environment=PORT=3001
Environment=NEXT_PUBLIC_API_URL=http://localhost:8001
Environment=NEXTAUTH_SECRET=votre-secret-ici
Environment=NEXTAUTH_URL=https://echochat.iafluence.cloud
Environment=GOOGLE_CLIENT_ID=votre-id.apps.googleusercontent.com
Environment=GOOGLE_CLIENT_SECRET=votre-secret-ici
Environment=ALLOWED_ADMIN_EMAILS=suan.tay.job@gmail.com,j.wallut.pro@gmail.com
ExecStart=/usr/bin/node /opt/echochat/frontend/.next/standalone/server.js
Restart=always
RestartSec=5
```

**⚠️ Remplacez les valeurs !** Copiez-les depuis votre `.env.production`.

Puis :
```bash
sudo systemctl daemon-reload
sudo systemctl restart echochat-frontend
```

### Problème 4 : Erreur "redirect_uri_mismatch"

Vérifiez dans [Google Cloud Console](https://console.cloud.google.com/apis/credentials) que l'URI de redirection est **exactement** :
```
https://echochat.iafluence.cloud/api/auth/callback/google
```

(Pas de `/` à la fin, pas de port)

### Problème 5 : "Access Denied" après connexion Google

Votre email n'est pas dans la liste `ALLOWED_ADMIN_EMAILS`. Vérifiez :

```bash
grep ALLOWED_ADMIN_EMAILS /opt/echochat/frontend/.env.production
```

Ajoutez votre email si nécessaire.

## 📊 Checklist Complète

- [ ] Fichier `.env.production` existe dans `/opt/echochat/frontend/`
- [ ] Fichier contient toutes les variables (NEXTAUTH_SECRET, GOOGLE_CLIENT_ID, etc.)
- [ ] Permissions du fichier sont correctes (`chmod 644`, owner `ubuntu`)
- [ ] Service systemd a la ligne `EnvironmentFile=/opt/echochat/frontend/.env.production`
- [ ] Frontend rebuilé avec `npm run build` (avec variables exportées)
- [ ] Service redémarré avec `systemctl restart echochat-frontend`
- [ ] `curl http://localhost:3001/api/auth/providers` retourne le provider Google
- [ ] Bouton Google visible sur `/auth/signin`
- [ ] Redirection URI configurée dans Google Cloud Console

## 🎯 Résumé en Une Commande

```bash
# Tout en une fois
cd /opt/echochat/frontend && \
export $(cat .env.production | xargs) && \
npm run build && \
sudo systemctl daemon-reload && \
sudo systemctl restart echochat-frontend && \
sleep 2 && \
curl http://localhost:3001/api/auth/providers
```

Si vous voyez le provider Google dans le JSON, c'est bon ! 🎉

## 💡 Pourquoi le Mode Standalone est Différent

| Mode Next.js | Commande | Charge .env ? |
|-------------|----------|---------------|
| Development | `npm run dev` | ✅ Oui (.env.local) |
| Production | `npm start` | ✅ Oui (.env.production) |
| **Standalone** | `node server.js` | ❌ **NON** |

Le mode standalone est conçu pour Docker/Kubernetes où les variables viennent de l'environnement externe (pas de fichiers). C'est pourquoi vous devez utiliser `EnvironmentFile` dans systemd.

## 🚀 Après le Fix

Une fois que ça fonctionne :

1. Testez la connexion Google complète
2. Vérifiez que vous êtes redirigé vers `/admin`
3. Gardez le service configuré tel quel
4. Pour les futures mises à jour, n'oubliez pas de rebuild avec les variables !

Bonne chance ! 🎉
