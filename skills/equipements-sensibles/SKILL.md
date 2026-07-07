---
description: Liste les equipements sensibles (hopitaux, EHPAD/maisons de retraite, ecoles, casernes de pompiers) autour d'un point, via OpenStreetMap/Overpass. Trigger when user asks "y a-t-il un hopital/EHPAD/ecole/caserne pres de...", "quels equipements sensibles autour de...", "qui est vulnerable a...", sensitive facilities, nursing homes, hospitals nearby, schools nearby, fire stations nearby.
allowed-tools: Bash(python3 *)
---

# Skill 'equipements-sensibles'

```bash
python3 ${CLAUDE_SKILL_DIR}/script.py proches --lat "<latitude>" --lon "<longitude>" --radius-m "<rayon, defaut 1500>" --categorie "<hopitaux|ehpad|ecoles|casernes_pompiers|tous, defaut tous>"
```

Renvoie, triees par distance, les installations trouvees dans le rayon donne : nom,
coordonnees, distance au point, telephone si disponible.

## Quand restreindre la categorie

- Question ciblee ("y a-t-il un EHPAD pres de...") -> `--categorie ehpad`.
- Question generale de caracterisation de zone -> laisser `tous` (defaut), qui interroge
  les 4 categories en une seule commande.

## A savoir avant de repondre

- Les EHPAD marquent la population la moins capable d'auto-evacuer : les signaler en
  priorite s'il y en a dans la zone.
- Les casernes de pompiers proches ne sont pas juste informatives : ce sont des points de
  coordination possibles pour l'intervention elle-meme.
- Cette liste vient d'OpenStreetMap (contributions communautaires) : la couverture peut
  etre incomplete pour de petites structures recentes ou rurales. Le signaler si peu ou
  aucun resultat n'apparait dans une zone qui devrait raisonnablement en avoir.
- Si `{"error": ...}` est renvoye, le signaler clairement plutot que d'inventer une reponse.
- Pour la population/vulnerabilite demographique (pas les batiments), utiliser le skill
  `demographie-vulnerabilite`. Pour les sites industriels a risque (ICPE/SEVESO), utiliser
  `risques-industriels`.
- **Toujours passer par ce script**, meme pour une reponse courte ou un simple diagramme : ne jamais appeler l'API directement (curl/WebFetch) en contournant le script, la logique de calcul (tendance, recherche de station, filtrage) n'est fiable qu'ici.
