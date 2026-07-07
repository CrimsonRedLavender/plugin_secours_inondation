---
description: Liste les sites industriels a risque (ICPE, sites Seveso seuil bas/haut) autour d'un point, via Georisques. Trigger when user asks "y a-t-il un site Seveso pres de...", "quels sites industriels a risque autour de...", "risque chimique/industriel a...", ICPE, Seveso site, industrial hazard nearby.
allowed-tools: Bash(python3 *)
---

# Skill 'risques-industriels'

```bash
python3 ${CLAUDE_SKILL_DIR}/script.py proches --lat "<latitude>" --lon "<longitude>" --radius-m "<rayon, defaut 5000, max 20000>"
```

Par defaut, ne renvoie que les sites **Seveso** (seuil bas ou haut) — les sites presentant
un risque d'accident majeur, pertinents en cas de crue (rupture de confinement, produits
dangereux). Pour voir toutes les installations classees (ICPE) sans filtre, y compris les
sites sans enjeu majeur (garages, pressings, etc.), ajouter `--tous`.

## A savoir avant de repondre

- **Seveso seuil haut** > **Seveso seuil bas** en gravite potentielle : le signaler
  explicitement si des deux types sont presents.
- Un site industriel inonde peut aggraver la situation au-dela de l'eau elle-meme
  (pollution, produits dangereux) : le mentionner si un site Seveso est proche d'un cours
  d'eau identifie par le skill `crue` ou `localisation`.
- L'API n'autorise pas un rayon au-dela de 20km (erreur serveur au-dela) : le rayon est
  automatiquement plafonne.
- Si `troncature: true` est renvoye, la recherche n'a pas pu parcourir tous les
  etablissements de la zone (tres forte densite d'ICPE) : le signaler plutot que de
  presenter la liste comme exhaustive.
- Si `{"error": ...}` est renvoye, le signaler clairement plutot que d'inventer une reponse.
- **Toujours passer par ce script**, meme pour une reponse courte ou un simple diagramme : ne jamais appeler l'API directement (curl/WebFetch) en contournant le script, la logique de calcul (tendance, recherche de station, filtrage) n'est fiable qu'ici.
