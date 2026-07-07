# Secours Inondations

Plugin Claude Code pour aider les équipes de secours à **comprendre un territoire et
décider vite** en situation de crue : localiser une zone, la caractériser (population,
équipements sensibles, risques industriels), et connaître l'état d'alerte hydrologique,
météorologique et sanitaire.

Projet réalisé dans le cadre du cours *Un plugin Claude Code pour les situations d'urgence*
(IUT NFC – UMLP, C. Guyeux — voir `ProjetsSkills.pdf`). Le périmètre couvert ici est le
volet « crue de surface » ; la spécialisation « crue souterraine / spéléologie » fait
l'objet d'un skill séparé, développé par un autre membre du groupe.

## Pourquoi des skills, et pas des MCP servers

Un agent d'urgence doit rester **réactif** : ne pas consommer une partie de son contexte à
se présenter lui-même avant qu'on lui ait rien demandé. Un serveur MCP reste chargé en
mémoire en permanence (nom, outils, signatures, docstrings) — de l'ordre de 1 000 à 2 000
tokens par serveur, dès le démarrage de la session. Un skill, lui, ne coûte que ~50 tokens
tant qu'il n'est pas utilisé : Claude ne charge son contenu complet (`SKILL.md`, scripts)
qu'au moment où la description matche la requête. Sur une trentaine de sources « utiles en
urgence », l'écart passe du simple au décuple. Voir [Empreinte tokens](#empreinte-tokens)
pour la mesure réelle sur ce plugin.

## Installer

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

Puis, dans la session Claude Code, poser une question naturelle, par exemple :

- « quel est le niveau de la Seine à Paris et sa tendance ? »
- « il pleut fort sur Nîmes depuis ce matin, quel risque dans les prochaines 48h ? »
- « quels hôpitaux et EHPAD sont exposés autour de Saint-Martin-Vésubie ? »
- « fais-moi une fiche de situation pour la zone qu'on vient de regarder »

ou invoquer explicitement un skill (`/secours-inondations:crue`).

Pour une installation permanente, suivre la documentation Claude Code sur les
[plugins](https://code.claude.com/docs/fr/plugins) (marketplace locale ou dépôt Git).

## Skills disponibles

| Skill | Rôle | Source de données |
|---|---|---|
| `localisation` | Géocode une adresse ; routes, ponts, cours d'eau et densité de bâti autour d'un point | BAN, OpenStreetMap/Overpass |
| `crue` | Niveau et tendance d'une rivière, station la plus proche d'un point | Hub'Eau (donnée Vigicrues fédérée) |
| `meteo` | Prévision de précipitations (cumuls 24h/48h/72h, pic horaire) | Open-Meteo |
| `demographie-vulnerabilite` | Population, densité, part de personnes âgées d'une commune | geo.api.gouv.fr, INSEE (melodi) |
| `equipements-sensibles` | Hôpitaux, EHPAD, écoles, casernes de pompiers autour d'un point | OpenStreetMap/Overpass |
| `risques-industriels` | Sites ICPE et Seveso (seuil bas/haut) autour d'un point | Géorisques |
| `veille-sanitaire` | Tendance des passages aux urgences pour gastro-entérite aiguë (proxy maladies hydriques post-crue), par département | Santé publique France (Odisse) |
| `restitution` | Synthétise les données déjà récoltées dans la conversation en fiche de situation et/ou schéma Mermaid | aucune (skill pur Markdown, pas de script) |

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
    ban.py, overpass.py, hydro.py, meteo.py, insee.py, georisques.py, geodes.py
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
consomment au total **~1060 tokens** (~130 tokens/skill en moyenne, contre les ~50
tokens/skill pris comme référence dans le support de cours) :

| Skill | Tokens (idle) |
|---|---|
| `veille-sanitaire` | ~160 |
| `demographie-vulnerabilite` | ~140 |
| `equipements-sensibles` | ~140 |
| `localisation` | ~140 |
| `restitution` | ~140 |
| `crue` | ~130 |
| `risques-industriels` | ~110 |
| `meteo` | ~100 |

Au-dessus des ~50 tokens de référence car chaque description porte plusieurs variantes de
phrases déclenchantes (français + mots-clés métier) — un compromis délibéré : des
descriptions plus courtes ont été testées et ont produit des ratés de déclenchement
(`veille-sanitaire` en particulier, voir son `SKILL.md`), donc la fiabilité du routage a
été priorisée sur la compacité maximale. Le total reste très en dessous de l'équivalent
MCP : le support de cours chiffre un MCP géo à 5 outils à ~1500 tokens *rien qu'au démarrage
de session, en permanence* ; nos 8 skills ne coûtent quelque chose qu'à l'usage (~500-2000
tokens chacun le temps d'une invocation), le reste du temps ils ne consomment que ce
~1060 tokens listés ci-dessus.

## Portée et limites connues

- **Scope France uniquement** : les sources de démographie (INSEE, geo.api.gouv.fr) et de
  veille sanitaire (Santé publique France) ne couvrent que le territoire français. Les
  skills basés sur OpenStreetMap (`localisation`, `equipements-sensibles`) fonctionnent
  n'importe où mais perdent leur intérêt hors de ce périmètre.
- **Crue souterraine / spéléologie** : hors périmètre de ce plugin par choix — une
  spécialisation séparée est prévue par un autre membre de l'équipe, réutilisant
  `common/hydro.py` et `common/geo.py`.
- **`localisation`** : les plans d'eau/lacs (`natural=water` sur OpenStreetMap) sont
  exclus par choix technique — polygones parfois énormes qui font échouer l'API Overpass
  publique (erreur 406). Seuls les cours d'eau linéaires (rivières/ruisseaux/canaux) sont
  couverts.
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
