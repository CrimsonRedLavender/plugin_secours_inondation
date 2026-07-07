---
description: Prevision de precipitations pour un point (cumuls 24h/48h/72h, pic horaire), via Open-Meteo. Trigger when user asks "va-t-il pleuvoir a...", "combien de pluie est prevue sur...", "prevision meteo pour...", "risque de fortes pluies a...", rainfall forecast, precipitation forecast.
allowed-tools: Bash(python3 *)
---

# Skill 'meteo'

```bash
python3 ${CLAUDE_SKILL_DIR}/script.py prevision --lat "<latitude>" --lon "<longitude>" --heures "<horizon en heures, defaut 72>"
```

Renvoie la precipitation actuelle, les cumuls prevus a 24h/48h/72h, et le pic horaire attendu
avec son horaire — pense pour repondre a "combien va-t-il tomber, et quand est-ce que ca
empire".

## A savoir avant de repondre

- Reformuler les cumuls en langage naturel plutot que de balancer les mm bruts : ex. "59mm
  attendus dans les prochaines 24h, avec un pic a 12,6mm/h prevu vers 22h le 4 juillet —
  cumul qui grimpe a plus de 300mm sur 72h, ce qui est un volume significatif".
- Ce skill donne une prevision meteo, pas un niveau de riviere : pour savoir si ca se
  traduit en crue, combiner avec le skill `crue` sur le meme point.
- Si `{"error": ...}` est renvoye, le signaler clairement plutot que d'inventer une valeur.
- Coordonnees a obtenir via le skill `localisation` si l'utilisateur donne une adresse.
- **Toujours passer par ce script**, meme pour une reponse courte ou un simple diagramme : ne jamais appeler l'API directement (curl/WebFetch) en contournant le script, la logique de calcul (tendance, recherche de station, filtrage) n'est fiable qu'ici.
