---
description: Population, densite et part de personnes agees (vulnerabilite face a une evacuation) d'une commune, via geo.api.gouv.fr et INSEE. Trigger when user asks "combien d'habitants a...", "quelle est la population de...", "y a-t-il beaucoup de personnes agees a...", "qui est vulnerable dans cette commune", population density, elderly population, demographic vulnerability.
allowed-tools: Bash(python3 *)
---

# Skill 'demographie-vulnerabilite'

```bash
python3 ${CLAUDE_SKILL_DIR}/script.py profil --lat "<latitude>" --lon "<longitude>"
```

ou, si l'utilisateur donne un nom de commune plutot que des coordonnees :

```bash
python3 ${CLAUDE_SKILL_DIR}/script.py profil --commune "<nom de la commune>"
```

Renvoie population, superficie, densite (hab/km2), et la structure par age : part et
effectif des 65 ans et plus, 80 ans et plus, et moins de 15 ans (annee 2023 par defaut,
ajustable avec `--annee` si une comparaison historique est demandee).

## A savoir avant de repondre

- Le niveau geographique est la **commune**, pas un rayon libre autour d'un point : pour
  une adresse precise, ce skill donne le profil de toute la commune qui la contient,
  pas seulement du quartier immediat. Le signaler si l'utilisateur cherche une echelle
  plus fine (quartier/IRIS).
- La part de personnes de 65+/80+ est le proxy de vulnerabilite le plus direct pour une
  evacuation : la mentionner explicitement plutot que de juste citer la population totale.
- Une forte densite (hab/km2) signifie plus de monde a evacuer dans un meme perimetre,
  mais aussi potentiellement plus de ressources locales (transports, personnel) ; le
  nuancer plutot que de le presenter comme un simple facteur de risque.
- Si `{"error": ...}` est renvoye, le signaler clairement plutot que d'inventer une valeur.
- Si un champ `avertissement` est present, la commune trouvee ne correspond pas exactement
  a ce qui a ete demande (recherche par nom approximative) : **ne pas presenter les
  donnees comme fiables**, le dire explicitement et demander confirmation ou reformulation.
- Pour les batiments/etablissements sensibles (EHPAD, hopitaux, ecoles) qui accueillent
  specifiquement ces populations vulnerables, combiner avec le skill `equipements-sensibles`.
- **Toujours passer par ce script**, meme pour une reponse courte ou un simple diagramme : ne jamais appeler l'API directement (curl/WebFetch) en contournant le script, la logique de calcul (tendance, recherche de station, filtrage) n'est fiable qu'ici.
