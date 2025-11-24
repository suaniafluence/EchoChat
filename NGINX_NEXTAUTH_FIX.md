# 🔧 Fix Nginx Routing for NextAuth

## Le Problème

Nginx envoie **toutes** les requêtes `/api/*` au backend FastAPI (port 8001), y compris les routes NextAuth (`/api/auth/*`) qui doivent aller au frontend Next.js (port 3001).

Résultat : `/api/auth/providers` retourne **404 Not Found** ❌

## Pourquoi ?

NextAuth (utilisé dans Next.js) expose ses routes d'authentification sous :
- `/api/auth/signin`
- `/api/auth/callback/google`
- `/api/auth/providers`
- etc.

Votre configuration Nginx actuelle :
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8001;  # Backend FastAPI
}
```

Cette règle capture **toutes** les requêtes `/api/*`, donc NextAuth ne reçoit jamais ses propres requêtes !

## La Solution

Ajouter une règle **AVANT** la règle générale `/api/` pour capturer spécifiquement les routes NextAuth.

**L'ordre est crucial !** Nginx utilise la première correspondance.

### Configuration Corrigée

```nginx
server {
    server_name echochat.iafluence.cloud;

    # 1. NextAuth routes - Frontend Next.js (DOIT être AVANT /api/)
    location /api/auth/ {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
    }

    # 2. Backend API - FastAPI
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 3. Frontend - Next.js
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/echochat.iafluence.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/echochat.iafluence.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = echochat.iafluence.cloud) {
        return 301 https://$host$request_uri;
    }
    listen 80;
    server_name echochat.iafluence.cloud;
    return 404;
}
```

## 📋 Étapes pour Appliquer le Fix

### 1. Sauvegardez la config actuelle

```bash
sudo cp /etc/nginx/sites-enabled/echochat /etc/nginx/sites-enabled/echochat.backup
```

### 2. Éditez le fichier Nginx

```bash
sudo nano /etc/nginx/sites-enabled/echochat
```

### 3. Ajoutez la section NextAuth

**AVANT** la section `location /api/`, ajoutez :

```nginx
    # NextAuth API - Frontend Next.js (port 3001)
    location /api/auth/ {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
    }
```

**Important** : Cette section doit être **AU-DESSUS** de `location /api/` !

### 4. Vérifiez l'ordre des sections

Votre fichier doit avoir cet ordre :

```
server {
    1. location /api/auth/ { ... }     ← NextAuth (port 3001)
    2. location /api/ { ... }          ← Backend (port 8001)
    3. location / { ... }              ← Frontend (port 3001)
    ...
}
```

### 5. Testez la syntaxe Nginx

```bash
sudo nginx -t
```

Vous devez voir :
```
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 6. Rechargez Nginx

```bash
sudo systemctl reload nginx
```

## ✅ Vérification

### Test 1 : API NextAuth

```bash
curl https://echochat.iafluence.cloud/api/auth/providers
```

**Résultat attendu :**
```json
{
  "google": {
    "id": "google",
    "name": "Google",
    "type": "oauth",
    "signinUrl": "https://echochat.iafluence.cloud/api/auth/signin/google",
    "callbackUrl": "https://echochat.iafluence.cloud/api/auth/callback/google"
  }
}
```

Si vous voyez ce JSON, NextAuth fonctionne ! ✅

### Test 2 : Bouton Google dans le navigateur

Allez sur : `https://echochat.iafluence.cloud/auth/signin`

Le bouton **"Continuer avec Google"** doit maintenant s'afficher ! 🎉

### Test 3 : Backend API (optionnel)

Si vous avez des routes backend, testez qu'elles fonctionnent toujours :

```bash
curl https://echochat.iafluence.cloud/api/health
# ou toute autre route de votre backend FastAPI
```

## 🔍 Dépannage

### Problème : Toujours 404 après le changement

1. **Vérifiez que les deux services tournent :**
   ```bash
   sudo systemctl status echochat-frontend
   sudo systemctl status echochat-backend

   sudo ss -tlnp | grep -E "3001|8001"
   ```

2. **Vérifiez l'ordre des sections dans Nginx :**
   ```bash
   sudo cat /etc/nginx/sites-enabled/echochat | grep -A 1 "location"
   ```

   Vous devez voir `/api/auth/` **avant** `/api/`.

3. **Vérifiez les logs Nginx :**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

### Problème : "Unable to connect"

Le frontend ne tourne pas :
```bash
sudo systemctl restart echochat-frontend
sudo journalctl -u echochat-frontend -n 50
```

### Problème : Backend retourne des erreurs

Vérifiez que le backend écoute sur le bon port :
```bash
sudo ss -tlnp | grep 8001
```

## 📊 Résumé du Routage

| Route | Destination | Port | Service |
|-------|-------------|------|---------|
| `/api/auth/*` | Frontend Next.js | 3001 | NextAuth |
| `/api/*` | Backend FastAPI | 8001 | EchoChat API |
| `/*` | Frontend Next.js | 3001 | Pages React |

## 🎯 Points Clés

1. **Ordre des `location` est crucial** : Plus spécifique d'abord
2. `/api/auth/` doit être **avant** `/api/`
3. NextAuth est partie du **frontend** (Next.js)
4. Les deux services (frontend 3001 + backend 8001) doivent tourner
5. Après chaque changement Nginx : `sudo nginx -t` puis `sudo systemctl reload nginx`

## 🚀 Après le Fix

Une fois que `/api/auth/providers` retourne le JSON Google :

1. ✅ Le bouton Google s'affichera sur la page de connexion
2. ✅ La connexion Google fonctionnera
3. ✅ Vous serez redirigé vers `/admin` après connexion
4. ✅ Votre backend API continuera de fonctionner normalement

C'est tout ! Le problème était uniquement dans le routage Nginx, pas dans votre code ou configuration Next.js. 🎉
