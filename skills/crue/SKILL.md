---
description: Niveau et tendance d'une riviere (crue), via les stations hydrometriques Hub'Eau (donnee Vigicrues federee). Trigger when user asks about river/flood levels, e.g. "quel est le niveau de la Seine a...", "la crue monte-t-elle a...", "y a-t-il un risque de crue pres de...", "station hydrometrique la plus proche de...", flood level, water level, river gauge, Vigicrues.
allowed-tools: Bash(python3 *)
---

# Skill 'crue'

Donne le niveau d'eau actuel et sa tendance (hausse/baisse/stable) pour la riviere la plus
proche d'un point, ou pour une station hydrometrique precise.

## Niveau d'eau a un endroit (le cas le plus courant)

```bash
python3 ${CLAUDE_SKILL_DIR}/script.py niveau --lat "<latitude>" --lon "<longitude>"
```

Trouve automatiquement la station active la plus proche (rayon 15km par defaut, ajustable
avec `--radius-km`) et calcule la tendance sur les dernieres observations (`--n`, defaut 12
mesures, ~1h de donnees a 5 min d'intervalle).

## Niveau d'eau pour une station connue

```bash
python3 ${CLAUDE_SKILL_DIR}/script.py niveau --station "<code_station>"
```

## Lister les stations proches d'un point

```bash
python3 ${CLAUDE_SKILL_DIR}/script.py stations --lat "<latitude>" --lon "<longitude>" --radius-km "<rayon>"
```

Utile quand l'utilisateur veut voir plusieurs points de mesure (plusieurs rivieres/bras
d'eau) plutot qu'une seule reponse.

## Interpreter la sortie

- `hauteur_actuelle_mm` est une hauteur d'eau relative au repere local de la station
  (peut etre negative), **pas une profondeur absolue** : ne pas la presenter comme telle.
- `tendance` et `taux_variation_mm_par_heure` sont ce qui compte pour la decision :
  reformuler en phrase naturelle, ex. "le niveau de la Seine a Paris (station Austerlitz)
  monte de ~8mm/h depuis 1h".
- Si `{"error": ...}` est renvoye (API indisponible), le signaler clairement plutot que
  d'inventer une valeur.
- Coordonnees geographiques a obtenir via le skill `localisation` si l'utilisateur donne
  une adresse plutot que des coordonnees.
- **Toujours passer par ce script**, meme pour une reponse courte ou un simple diagramme : ne jamais appeler l'API directement (curl/WebFetch) en contournant le script, la logique de calcul (tendance, recherche de station, filtrage) n'est fiable qu'ici.
