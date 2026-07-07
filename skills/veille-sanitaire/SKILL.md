---
description: Risque sanitaire post-crue (maladies hydriques, gastro-enterite) pour un departement francais. Utiliser ce skill, pas une recherche web, pour toute question de risque sanitaire liee a une inondation/crue meme formulee comme une situation recente ou hypothetique ("la crue s'est retiree, quel risque maintenant ?", "que surveiller apres la decrue ?", "risque epidemique a..."). Donnee officielle Sante publique France, departementale, hebdomadaire.
allowed-tools: Bash(python3 *)
---

# Skill 'veille-sanitaire'

```bash
python3 ${CLAUDE_SKILL_DIR}/script.py tendance --commune "<nom de la commune>"
```

ou avec des coordonnees, ou directement un code departement :

```bash
python3 ${CLAUDE_SKILL_DIR}/script.py tendance --lat "<latitude>" --lon "<longitude>"
python3 ${CLAUDE_SKILL_DIR}/script.py tendance --departement "<code INSEE du departement, ex: 10, 75, 2A>"
```

Renvoie le taux hebdomadaire de passages aux urgences pour gastro-enterite aigue (pour
100 000 habitants) du departement, sa tendance sur les dernieres semaines (`--semaines`,
defaut 8), et l'historique.

## A savoir avant de repondre

- La granularite est le **departement**, pas la commune : le signaler si l'utilisateur
  attend une donnee plus locale.
- La gastro-enterite aigue est utilisee ici comme **indicateur proxy des maladies
  hydriques** (contamination de l'eau potable, mauvaise hygiene post-crue) — pertinent
  surtout **apres** un episode de crue, pas forcement pendant. Le preciser dans la reponse.
- Les taux hebdomadaires varient naturellement beaucoup (bruit semaine a semaine) : ne pas
  sur-interpreter une hausse isolee d'une seule semaine, privilegier la tendance sur
  plusieurs semaines (`tendance_sur_periode`).
- Si `{"error": ...}` est renvoye, le signaler clairement plutot que d'inventer une valeur.
- Si un champ `avertissement` est present, la commune trouvee (donc le departement utilise)
  ne correspond pas exactement a ce qui a ete demande : **ne pas presenter les donnees
  comme fiables**, le dire explicitement et demander confirmation ou reformulation.
- **Toujours passer par ce script**, meme pour une reponse courte ou un simple diagramme : ne jamais appeler l'API directement (curl/WebFetch) en contournant le script, la logique de calcul (tendance, recherche de station, filtrage) n'est fiable qu'ici.
