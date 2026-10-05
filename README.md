# Builder Agent — LAB 3 (réseau d'agents autonomes)

Agent d'assemblage d'un réseau multi-agents. Il ne cherche pas l'information
lui-même : il **délègue des capacités** à un orchestrateur, récupère les
résultats et construit la page finale.

    agent_id     : builder-01
    nom          : Builder Agent
    rôle         : généraliste (imposé par l'orchestrateur)
    capacités    : web_development, application_development, frontend, backend
    endpoint     : http://127.0.0.1:8080

## Pipeline

    OBJECTIF
       │
       ├─► research            ──► Research Agent  ─┐
       ├─► security_analysis   ──► Cyber Agent      ├─► Builder ─► landing page
       └─► testing             ──► QA Agent        ─┘

Le Builder s'enregistre d'abord auprès de l'orchestrateur (il est un agent
comme les autres : identité, capacités, endpoint), puis demande une capacité
au **réseau** — jamais à un agent en direct. C'est l'orchestrateur qui choisit
l'agent capable de traiter la demande.

## Fichiers

| Fichier | Rôle |
|---|---|
| `builder.py` | L'agent : enregistrement, délégation, génération de la landing page. |
| `labkit.py` | Briques partagées : clés d'API, modèle `Agent`/`Task`, journal d'événements. |
| `docs/index.html` | Sortie réelle du Builder : page produite à partir des résultats délégués. |

## Utilisation

```bash
pip install -r requirements.txt

export LAB_ORCH=http://127.0.0.1:8000     # orchestrateur du lab
export LAB_MASTER_KEY='…'                 # clé opérateur (enregistrement, délégation)
export LAB_AGENT_KEY='…'                  # clé de l'agent

python builder.py --objective "Prépare une landing page sur les agents autonomes."
python builder.py --objective "Analyse de cybersécurité de cette application." --no-build
```

Options :

| Option | Effet |
|---|---|
| `--objective` | La demande, en langage naturel (obligatoire). |
| `--out` | Fichier HTML de sortie (défaut `landing.html`). |
| `--no-build` | Délègue et s'arrête : aucune page écrite. |

## Sécurité

- Les clés ne sont **jamais** en dur : elles viennent de l'environnement
  (`LAB_MASTER_KEY`, `LAB_AGENT_KEY`). Les valeurs par défaut du lab sont des
  placeholders publics.
- Les jetons d'enrôlement et d'agent restent hors du dépôt (`.gitignore`).
- L'orchestrateur répond `401 Unauthorized` si la clé est absente ou invalide.

## Résultat en ligne

La page produite par l'agent est publiée via GitHub Pages :
<https://aicmaxter.github.io/builder-agent/>

---

Lab 3 — comprendre API / HTTP / JSON / endpoint / agent / orchestrateur /
registry / capability / délégation / logs.
