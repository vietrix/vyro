# Déploiement

## Liste de contrôle

1. Définissez `VYRO_ENV=production`
2. Configurez un `VYRO_SECRET_KEY` fort
3. Définir le nombre de travailleurs à partir du profil CPU
4. Activer l'observabilité et les sondes de santé
5. Validez le contrat API avant le déploiement

## Kubernetes

Générez des manifestes :

```bash
vyro k8s --name vyro-api --image ghcr.io/vietrix/vyro:latest --out k8s.yaml
```
