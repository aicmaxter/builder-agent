"""
labkit.py — briques partagées du LAB 3 (réseau local d'agents).

Contient tout ce qui serait sinon dupliqué dans chaque agent :
- clés d'API et vérification d'authentification ;
- journal d'événements horodaté ;
- identité d'agent (ce que l'orchestrateur a besoin de savoir, et rien de plus).
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Clés partagées (à surcharger par variables d'environnement)
# ---------------------------------------------------------------------------
# Clé « opérateur » : autorise les actions sensibles sur l'orchestrateur
# (enregistrer un agent, déléguer une tâche).
MASTER_KEY = os.environ.get("LAB_MASTER_KEY", "LAB-MASTER-SECRET")
# Clé par défaut des agents du lab (chaque agent peut la surcharger).
AGENT_KEY = os.environ.get("LAB_AGENT_KEY", "LAB-AGENT-SECRET")


def now() -> str:
    """Heure locale au format utilisé dans les logs du sujet : [17:32:01]."""
    return time.strftime("%H:%M:%S")


class Unauthorized(Exception):
    """Levée quand la clé d'API est absente ou invalide (→ HTTP 401)."""


def check_key(provided: str | None, expected: str) -> None:
    """Vérifie une clé d'API. Lève Unauthorized si elle ne correspond pas."""
    if not provided or provided != expected:
        raise Unauthorized("Unauthorized: X-API-Key manquante ou invalide")


# ---------------------------------------------------------------------------
# Modèles de données
# ---------------------------------------------------------------------------
@dataclass
class Agent:
    """Un agent tel que l'orchestrateur le connaît : identité + capacités + adresse."""

    agent_id: str
    name: str
    endpoint: str
    capabilities: list[str]
    api_key: str = AGENT_KEY
    status: str = "unknown"  # online | offline | unknown
    last_seen: float = field(default_factory=time.time)
    registered_at: float = field(default_factory=time.time)
    tasks_done: int = 0

    def public(self) -> dict[str, Any]:
        """Vue publique : jamais de clé d'API dans une réponse HTTP."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "endpoint": self.endpoint,
            "capabilities": self.capabilities,
            "status": self.status,
            "last_seen": self.last_seen,
            "tasks_done": self.tasks_done,
        }


@dataclass
class Task:
    """Une tâche déléguée, avec son cycle de vie complet."""

    task_id: str
    capability: str
    prompt: str
    status: str = "created"  # created | routed | running | completed | failed
    agent_id: str | None = None
    result: str | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def public(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "capability": self.capability,
            "prompt": self.prompt,
            "status": self.status,
            "agent_id": self.agent_id,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class EventLog:
    """Journal d'événements : c'est lui que les étudiants lisent pour comprendre."""

    def __init__(self, limit: int = 500) -> None:
        self.limit = limit
        self.events: list[dict[str, Any]] = []

    def add(self, kind: str, message: str, **data: Any) -> dict[str, Any]:
        event = {"at": now(), "ts": time.time(), "kind": kind, "message": message, **data}
        self.events.append(event)
        if len(self.events) > self.limit:
            self.events = self.events[-self.limit :]
        print(f"[{event['at']}] {message}", flush=True)
        return event

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.events[-limit:][::-1]
