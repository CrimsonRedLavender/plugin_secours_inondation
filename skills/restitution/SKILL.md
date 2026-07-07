---
description: Synthetise en une fiche de situation (et/ou un schema Mermaid) les informations deja recueillies dans la conversation (localisation, crue, meteo, population, equipements sensibles, risques). Trigger when user asks "fais-moi un resume de la situation", "genere un rapport", "fiche de situation pour...", "schema/diagramme de la situation", situation report, briefing, summary for the commander.
---

# Skill 'restitution'

Ce skill n'appelle aucune API : il structure ce qui a deja ete recueilli via les autres
skills (`localisation`, `crue`, `meteo`, `demographie-vulnerabilite`, `equipements-sensibles`,
`risques-industriels`, `veille-sanitaire`) dans cette conversation.

**Ne jamais inventer une donnee absente.** Si une information n'a pas ete recueillie,
omettre la section correspondante ou proposer d'appeler le skill manquant plutot que de
deviner une valeur.

## Fiche de situation (mode par defaut)

Structurer la reponse avec les sections suivantes, en n'incluant que celles pour
lesquelles des donnees ont reellement ete obtenues cette session :

1. **Zone concernee** — lieu, coordonnees, commune.
2. **Hydrologie / meteo** — niveau de crue et tendance, cumul de pluie prevu.
3. **Population & vulnerabilite** — habitants, part de personnes agees.
4. **Equipements sensibles** — hopitaux, EHPAD, ecoles, casernes a proximite.
5. **Risques industriels** — sites ICPE/SEVESO le cas echeant.
6. **Accessibilite** — routes, ponts, points d'eau.
7. **Recommandation** — 1 a 3 phrases actionnables, priorisant ce qui presente le plus
   grand risque humain (ex: EHPAD en zone inondable + crue en hausse rapide).

## Schema Mermaid (si demande explicitement, ou en complement de la fiche)

Utiliser un flowchart reliant la zone aux risques identifies et aux actions
recommandees. Exemple de structure a adapter aux donnees reellement disponibles :

```mermaid
flowchart TD
    Z["Zone : <nom du lieu>"]
    Z --> H["Crue : <niveau/tendance>"]
    Z --> M["Meteo : <cumul prevu>"]
    Z --> P["Population : <habitants>, <% agees>"]
    Z --> E["Equipements sensibles : <liste>"]
    H --> R["Recommandation"]
    P --> R
    E --> R
```

Ne pas inclure de noeud pour une categorie sans donnee reelle disponible.

## A savoir avant de repondre

- Si un lieu precis est nomme et qu'aucune donnee n'a encore ete recueillie, **ne pas
  demander confirmation avant d'agir** : lancer directement les skills pertinents
  (`localisation`, `crue`, `meteo`, `demographie-vulnerabilite`, `equipements-sensibles`,
  `risques-industriels`) puis produire la fiche. Le nom du lieu est deja un signal
  d'intention suffisant — l'objectif de ce plugin est la reactivite, pas la confirmation
  a chaque etape. Ne demander confirmation que si la demande est reellement ambigue
  (aucun lieu identifiable du tout).
- Rester concis : une fiche de situation sert a decider vite, pas a tout documenter.
