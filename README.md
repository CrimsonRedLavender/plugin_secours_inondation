# Secours Inondations

Plugin Claude Code pour aider les équipes de secours à **comprendre un territoire et
décider vite** en situation de crue : localiser une zone, la caractériser (population,
équipements sensibles, risques industriels), et connaître l'état d'alerte hydrologique,
météorologique et sanitaire.

## Installation

**Important : ce plugin doit être installé dans son ensemble, pas skill par skill.**

Les skills partagent du code via le dossier `common/` à la racine du plugin (géocodage,
appels HTTP, calculs de tendance...). Si vous copiez un seul dossier de `skills/` à part
(ex. `cp -r skills/crue ~/.claude/skills/`, méthode habituelle pour un skill autonome),
l'import de `common/` échouera (`ModuleNotFoundError`). Il faut charger le plugin complet.

Pour tester en local, depuis la racine du dépôt :

```bash
pip install -r requirements.txt
claude --plugin-dir .
```

(ou `claude --plugin-dir /chemin/vers/plugin_secours_inondation` depuis un autre
répertoire.)

Pour une installation permanente, suivre la documentation Claude Code sur les
[plugins](https://code.claude.com/docs/fr/plugins) (marketplace locale ou dépôt Git).

## Utilisation

Une fois le plugin chargé, il n'y a rien d'autre à faire que **parler naturellement** à
Claude Code : chaque skill se déclenche seul quand la question correspond à son rôle,
sans commande à retenir. Un skill peut aussi être invoqué explicitement avec
`/secours-inondations:<nom-du-skill>` si vous voulez forcer un skill précis (utile pour
tester, ou si le phrasé est trop ambigu pour l'auto-déclenchement).

### Cas d'usage typiques d'une équipe de secours

Le plugin est pensé pour des situations, pas pour des noms de skills — voici ce qu'une
équipe de secours est susceptible de taper dans chacune de ces situations.

| Situation opérationnelle                                                                            | Prompt typique                                                                                                                                     | Ce que Claude mobilise                                                                                                                                                 |
| --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Une alerte de montée des eaux tombe sur une commune, il faut décider avant d'envoyer une équipe     | « Il y a une alerte de montée des eaux à Nemours, aide-moi à évaluer la situation avant d'envoyer une équipe. »                                    | `localisation`, `crue`, `meteo`, `demographie-vulnerabilite`, `equipements-sensibles`, `risques-industriels`, puis `restitution` pour la synthèse et la recommandation |
| Préparer une évacuation ciblée sur une adresse précise, en priorisant les populations non-autonomes | « Il y a une alerte au 12 rue de la République à Troyes. Combien de personnes vivent dans le secteur, et y a-t-il un EHPAD ou hôpital pas loin ? » | `localisation`, `demographie-vulnerabilite`, `equipements-sensibles`                                                                                                   |
| Une rumeur ou un signalement remonte, il faut vérifier ce qui est confirmable avant de le relayer   | « J'ai entendu dire qu'il y a eu une fuite chimique près de Feyzin, tu peux vérifier ? »                                                           | `risques-industriels` (+ `localisation`) — et une réponse claire sur ce qui **n'est pas** vérifiable en temps réel avec ces sources                                    |
| Anticiper une dégradation avant qu'elle n'arrive                                                    | « Combien de pluie est prévue sur Marseille dans les 48 prochaines heures, et y a-t-il un pic à surveiller ? »                                     | `meteo`                                                                                                                                                                |
| Prioriser entre plusieurs communes quand les moyens sont limités                                    | « Compare le risque de crue entre Nemours et Nogent-sur-Seine, laquelle est la plus vulnérable ? »                                                 | `crue`, `demographie-vulnerabilite` (x2), synthèse comparative                                                                                                         |
| Briefer une équipe ou un commandement avec un support visuel                                        | « Vérifie le niveau de la Seine à Paris et la météo, fais-moi une fiche de situation complète avec un schéma Mermaid. »                            | `crue`, `meteo`, puis `restitution`                                                                                                                                    |
| Vérifier un risque combiné crue + industriel avant une intervention en zone à risque                | « Y a-t-il des sites Seveso dans un rayon de 8km autour de Gennevilliers ? Je m'inquiète d'un risque combiné avec une crue de la Seine. »          | `risques-industriels`, `crue`                                                                                                                                          |
| Réévaluer un risque sanitaire après le retrait des eaux, avant de lever une vigilance               | « La crue à Nogent-sur-Seine s'est retirée la semaine dernière, y a-t-il un risque sanitaire de maladies hydriques à surveiller maintenant ? »     | `veille-sanitaire`                                                                                                                                                     |

Ces exemples sont volontairement formulés comme le ferait un opérateur sous pression (avec
une commune ou une adresse, pas des coordonnées GPS) : c'est le cas d'usage réel visé par
ce plugin, et celui sur lequel chaque skill a été testé de bout en bout.

### Exemples déclenchant plusieurs skills

Claude enchaîne plusieurs skills seul quand la question l'exige — pas besoin de les
appeler un par un. Ces trois exemples ont été testés de bout en bout (les 8 skills se
déclenchent bien via l'outil `Skill`, pas en devinant leurs scripts) :

- « On nous signale une inondation à Besançon, tu peux me faire un rapport sur la
  situation ? »
- « La Loire menace de sortir de son lit à Orléans, prépare-moi un point de situation
  complet avant qu'on décide d'intervenir. » — Claude distingue correctement la Loire de
  **le Loiret** (rivière différente, dont la station la plus proche relève en fait), et
  s'appuie sur la vigilance Vigicrues officielle plutôt que de confondre les deux cours
  d'eau.
- « Le Rhône monte à Avignon, j'ai besoin d'un état complet de la situation pour le PC de
  crise. » — Claude a corrigé seul une erreur de géocodage initiale (une rue "Avignon" à
  Combourg, en Bretagne) en précisant le code postal, et a signalé une contradiction
  entre l'observation terrain rapportée et la donnée officielle (vigilance verte, niveau
  stable) plutôt que de trancher à sa place.

Dans les trois cas, une panne d'API réelle (Overpass ou Géorisques) a été rencontrée
pendant les tests et gérée correctement : la section concernée est marquée indisponible
plutôt que d'inventer une valeur.

### Exemples déclenchant un seul skill

Exemples de questions qui déclenchent chacune un seul skill :

| Question posée                                                            | Skill déclenché             |
| ------------------------------------------------------------------------- | --------------------------- |
| « quel est le niveau de la Seine à Paris et sa tendance ? »               | `crue`                      |
| « geocode le 10 rue de Rivoli à Paris, il y a un pont pas loin ? »        | `localisation`              |
| « combien de pluie est prévue sur Marseille dans les 48h ? »              | `meteo`                     |
| « combien d'habitants à Chamonix, et quelle part de personnes âgées ? »   | `demographie-vulnerabilite` |
| « y a-t-il un hôpital ou une école à moins de 2km du centre de Lyon ? »   | `equipements-sensibles`     |
| « quels sites Seveso sont proches de Feyzin ? »                           | `risques-industriels`       |
| « y a-t-il une hausse des gastro-entérites dans le Rhône actuellement ? » | `veille-sanitaire`          |

### Interpréter la réponse

Chaque skill renvoie un objet JSON brut (données + source + parfois un avertissement) que
Claude reformule en français avant de répondre — vous ne voyez jamais ce JSON tel quel en
usage normal. Deux réflexes à garder :

- Si Claude signale une donnée manquante, une erreur d'API ou un avertissement de
  correspondance approximative (nom de commune, station trop lointaine...), c'est un
  signal à vérifier, pas à ignorer — voir [Portée et limites connues](#portée-et-limites-connues)
  et le `SKILL.md` du skill concerné pour le détail.
- Ce plugin **aide à décider**, il ne décide pas : toute recommandation qu'il produit
  reste à valider par l'opérateur humain avant action sur le terrain.

## Skills disponibles

| Skill                       | Rôle                                                                                                                           | Source de données                                         |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------- |
| `localisation`              | Géocode une adresse ; routes, ponts, cours d'eau et densité de bâti autour d'un point                                          | BAN, OpenStreetMap/Overpass                               |
| `crue`                      | Niveau et tendance d'une rivière, station la plus proche d'un point, et niveau de vigilance officiel (vert/jaune/orange/rouge) | Hub'Eau (donnée Vigicrues fédérée), Vigicrues (vigilance) |
| `meteo`                     | Prévision de précipitations (cumuls 24h/48h/72h, pic horaire)                                                                  | Open-Meteo                                                |
| `demographie-vulnerabilite` | Population, densité, part de personnes âgées d'une commune                                                                     | geo.api.gouv.fr, INSEE (melodi)                           |
| `equipements-sensibles`     | Hôpitaux, EHPAD, écoles, casernes de pompiers autour d'un point                                                                | OpenStreetMap/Overpass                                    |
| `risques-industriels`       | Sites ICPE et Seveso (seuil bas/haut) autour d'un point                                                                        | Géorisques                                                |
| `veille-sanitaire`          | Tendance des passages aux urgences pour gastro-entérite aiguë (proxy maladies hydriques post-crue), par département            | Santé publique France (Odisse)                            |
| `restitution`               | Synthétise les données déjà récoltées dans la conversation en fiche de situation et/ou schéma Mermaid                          | aucune (skill pur Markdown, pas de script)                |

Chaque capacité a été retenue parce qu'elle répond à une décision concrète d'un
responsable de secours (localiser / caractériser une zone / connaître l'état d'alerte), et
non parce qu'une source de données existait — un « skill pour interroger des données » qui
ne se déclenche jamais seul n'a pas sa place ici.

Chaque skill a son propre `SKILL.md` documentant ses commandes, ses limites connues et la
façon d'interpréter sa sortie — à lire avant de modifier un skill.

## Architecture

```
plugin_secours_inondation/
  .claude-plugin/plugin.json   # manifeste du plugin
  common/                      # code partagé entre skills
    http.py                    # wrapper requests : User-Agent, retry/backoff sur 429/5xx
    geo.py                     # distance haversine
    ban.py, overpass.py, hydro.py, vigicrues.py, meteo.py, insee.py, georisques.py, geodes.py
  skills/
    <nom-du-skill>/
      SKILL.md                 # frontmatter (description, allowed-tools) + instructions
      script.py                # CLI Python testable seul (sauf restitution, sans script)
  requirements.txt
```

Chaque `script.py` peut être testé directement en ligne de commande, indépendamment de
Claude :

```bash
python3 skills/crue/script.py niveau --lat 48.8566 --lon 2.3522
```

Le code partagé est importé via un bootstrap `sys.path` dans chaque script (remonte du
dossier du skill jusqu'à la racine du plugin) : fonctionne quel que soit le répertoire de
travail au moment de l'exécution, à condition que le plugin soit installé en entier (voir
plus haut).

## Empreinte tokens

Mesuré via `/context` (Claude Code v2.1.197), les 8 skills chargés mais inactifs
consomment au total **~1110 tokens** (~140 tokens/skill en moyenne) :

| Skill                       | Tokens (idle) |
| --------------------------- | ------------- |
| `crue`                      | ~170          |
| `veille-sanitaire`          | ~160          |
| `restitution`               | ~150          |
| `demographie-vulnerabilite` | ~140          |
| `equipements-sensibles`     | ~140          |
| `localisation`              | ~140          |
| `risques-industriels`       | ~110          |
| `meteo`                     | ~100          |

Nous sommes au dessus de ~50 tokens car chaque description porte plusieurs variantes de
phrases déclenchantes (français + mots-clés métier). Cela rerésente un compromis délibéré : des
descriptions plus courtes ont été testées et ont produit des ratés de déclenchement
(`veille-sanitaire` en particulier, voir son `SKILL.md`), donc la fiabilité du routage a
été priorisée sur la compacité maximale. Le total reste très en dessous de l'équivalent
MCP : le support de cours chiffre un MCP géo à 5 outils à ~1500 tokens _rien qu'au démarrage
de session, en permanence_ ; nos 8 skills ne coûtent quelque chose qu'à l'usage (~500-2000
tokens chacun le temps d'une invocation), le reste du temps ils ne consomment que ce
~1110 tokens listés ci-dessus.

## Portée et limites connues

- **Scope France uniquement** : les sources de démographie (INSEE, geo.api.gouv.fr) et de
  veille sanitaire (Santé publique France) ne couvrent que le territoire français. Les
  skills basés sur OpenStreetMap (`localisation`, `equipements-sensibles`) fonctionnent
  n'importe où mais perdent leur intérêt hors de ce périmètre.
- **`localisation`** : les plans d'eau/lacs (`natural=water` sur OpenStreetMap) sont
  exclus par choix technique — polygones parfois énormes qui font échouer l'API Overpass
  publique (erreur 406). Seuls les cours d'eau linéaires (rivières/ruisseaux/canaux) sont
  couverts. Par ailleurs, le `score` de confiance du géocodage BAN ne suffit pas toujours
  à détecter une mauvaise correspondance : un nom de ville étrangère homonyme d'un petit
  lieu français (ex. "Berlin" → un hameau de l'Ariège) peut obtenir un score élevé malgré
  tout — voir `SKILL.md` pour la règle d'interprétation appliquée.
- **`crue`** : le niveau de vigilance officiel (Vigicrues) ne couvre qu'environ 340
  tronçons de cours d'eau surveillés par l'État en métropole, pas tous les cours d'eau —
  au-delà de 30km du tronçon le plus proche, aucune couleur de vigilance n'est renvoyée
  (absence de couverture, pas absence de risque).
- **`equipements-sensibles` / `risques-industriels`** : dépendent de la qualité des
  contributions OpenStreetMap / de la base Géorisques ; peuvent être incomplets en zone
  rurale ou très récente.
- **`veille-sanitaire`** : donnée au niveau département, pas commune ; peut masquer un
  foyer localisé.
- **`demographie-vulnerabilite` / `veille-sanitaire`** (recherche par nom de commune) :
  une recherche approximative peut retourner un `avertissement` si le nom ne correspond
  pas exactement à une commune française — à vérifier avant d'utiliser la donnée.

## Tester

Chaque skill peut être testé unitairement via son `script.py`. Pour tester le
déclenchement automatique et le comportement de bout en bout :

```bash
claude --plugin-dir . --allowedTools "Skill,Bash(python3 *)" -p "quel est le niveau de la Seine a Paris ?"
```

**Important** : `Skill` doit être inclus dans `--allowedTools`, pas seulement
`Bash(python3 *)` — sinon l'appel au skill est refusé silencieusement et Claude improvise
un contournement (appel direct à l'API), ce qui ressemble à un bug aléatoire mais n'en est
pas un.
