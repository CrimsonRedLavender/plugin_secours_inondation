---
description: Geocode une adresse, ou caracterise l'accessibilite d'un point (routes, ponts, cours d'eau proches, densite de batiments), via BAN et OpenStreetMap/Overpass. Trigger when user asks "ou se trouve...", "quelles routes/ponts autour de...", "comment acceder a...", "quels cours d'eau pres de...", geocode an address, find nearby roads/bridges/water access, building density.
allowed-tools: Bash(python3 *)
---

# Skill 'localisation'

## Convertir une adresse en coordonnees

```bash
python3 ${CLAUDE_SKILL_DIR}/script.py geocode --address "<adresse en texte libre>"
```

## Convertir des coordonnees en adresse

```bash
python3 ${CLAUDE_SKILL_DIR}/script.py reverse --lat "<latitude>" --lon "<longitude>"
```

## Caracteriser l'accessibilite autour d'un point

```bash
python3 ${CLAUDE_SKILL_DIR}/script.py acces --lat "<latitude>" --lon "<longitude>" --radius-m "<rayon en metres, defaut 800>"
```

Renvoie, pour le rayon donne : les routes nommees, les ponts (utiles pour reperer les
points de passage potentiellement coupes par une crue), les cours d'eau proches
(rivieres/ruisseaux/canaux, pas les lacs — voir note technique), et une estimation de la
densite de batiments (nombre de batiments dans le rayon, pas une liste individuelle).

## A savoir avant de repondre

- Si l'utilisateur donne une adresse plutot que des coordonnees, commencer par `geocode`
  puis reutiliser `lat`/`lon` pour `acces`.
- `points_eau` ne couvre que les cours d'eau lineaires (waterway=river/stream/canal), pas
  les plans d'eau/lacs (natural=water) : cette derniere categorie est deliberement exclue
  car elle correspond a des polygones OSM parfois enormes que l'API publique Overpass
  rejette (erreur 406). A signaler si l'utilisateur cherche specifiquement un lac/plan
  d'eau — la reponse peut etre incomplete dans ce cas precis.
- Si `{"error": ...}` est renvoye, le signaler clairement plutot que d'inventer une reponse.
- Pour le niveau/la tendance d'un cours d'eau identifie ici, utiliser le skill `crue`.
- **Toujours passer par ce script**, meme pour une reponse courte ou un simple diagramme : ne jamais appeler l'API directement (curl/WebFetch) en contournant le script, la logique de calcul (tendance, recherche de station, filtrage) n'est fiable qu'ici.
