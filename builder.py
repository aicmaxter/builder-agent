"""
builder.py — BUILDER AGENT du LAB 3.

Rôle : produire l'application finale. Il ne fait PAS la recherche lui-même :
il demande la capacité « research » à l'orchestrateur, reçoit le résultat,
puis enchaîne avec security_analysis et testing avant d'écrire la landing page.

Il s'enregistre aussi auprès de l'orchestrateur : c'est un agent comme les autres,
il a donc une identité, des capacités et un endpoint.

Usage :
    python builder.py --objective "Prépare une landing page sur les agents autonomes."
    python builder.py --objective "Fais une analyse de cybersécurité de cette application." --no-build
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from labkit import AGENT_KEY, MASTER_KEY  # noqa: E402

ORCH = os.environ.get("LAB_ORCH", "http://127.0.0.1:8000")
AGENT_ID = "builder-01"
CAPABILITIES = ["web_development", "application_development", "frontend", "backend"]
HEADERS = {"X-API-Key": MASTER_KEY}

C = {
    "b": "\033[1m", "dim": "\033[2m", "y": "\033[33m", "g": "\033[32m",
    "r": "\033[31m", "c": "\033[36m", "x": "\033[0m",
}


def say(step: str, msg: str) -> None:
    print(f"{C['dim']}[{time.strftime('%H:%M:%S')}]{C['x']} {C['b']}{step:<14}{C['x']}{msg}")


def delegate(client: httpx.Client, capability: str, task: str) -> dict:
    """Demande une capacité au réseau — jamais à un agent en direct."""
    say("DELEGATE", f"capability={C['c']}{capability}{C['x']} → orchestrateur")
    resp = client.post(f"{ORCH}/delegate", json={"capability": capability, "task": task}, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") == "completed":
        say("RESULT", f"{C['g']}{data['agent_id']}{C['x']} a répondu ({len(data.get('result') or '')} car.)")
    else:
        say("REFUSÉ", f"{C['r']}{data.get('error')}{C['x']}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--objective", required=True)
    parser.add_argument("--out", default="landing.html")
    parser.add_argument("--no-build", action="store_true", help="ne pas écrire la landing page")
    args = parser.parse_args()

    with httpx.Client(timeout=180) as client:
        # 1) Le Builder se présente au réseau.
        client.post(
            f"{ORCH}/register",
            json={
                "agent_id": AGENT_ID,
                "name": "Builder Agent",
                "endpoint": "http://127.0.0.1:8080",
                "capabilities": CAPABILITIES,
                "api_key": AGENT_KEY,
            },
            headers=HEADERS,
        )
        say("REGISTER", f"{AGENT_ID} présenté au réseau")

        # 2) Analyser la demande : de quoi ai-je besoin ?
        needs = ["research"]
        lowered = args.objective.lower()
        if any(w in lowered for w in ("landing", "application", "site", "app")):
            needs += ["security_analysis", "testing"]
        say("ANALYSE", f"besoins identifiés : {', '.join(needs)}")

        results: dict[str, str] = {}
        for capability in needs:
            data = delegate(client, capability, args.objective)
            if data.get("status") == "completed":
                results[capability] = data["result"]
            else:
                say("ARRÊT", f"sans « {capability} », je ne peux pas continuer")
                print(f"\n{C['r']}{data.get('error')}{C['x']}")
                return 2

        if args.no_build:
            return 0

        # 3) Construire avec ce qui est revenu du réseau.
        research = results.get("research", "")
        security = results.get("security_analysis", "")
        qa = results.get("testing", "")
        title = "Agents autonomes"
        html = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NovaLab — {title}</title>
<style>
 :root{{--bg:#0b0d16;--fg:#e9eaf2;--accent:#7c5cff;--muted:#9aa0b4}}
 *{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);
 font:16px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
 .wrap{{max-width:900px;margin:0 auto;padding:64px 24px}}
 h1{{font-size:clamp(2rem,5vw,3rem);line-height:1.1;margin:0 0 8px}}
 .tag{{display:inline-block;padding:4px 10px;border:1px solid #ffffff22;border-radius:999px;
 font-size:12px;color:var(--muted);margin-bottom:20px}}
 .grid{{display:grid;gap:16px;grid-template-columns:1fr 1fr;margin-top:32px}}
 .card{{background:#ffffff08;border:1px solid #ffffff14;border-radius:16px;padding:20px}}
 pre{{white-space:pre-wrap;font-size:13px;color:var(--muted);margin:0}}
 .accent{{color:var(--accent)}}
 footer{{margin-top:48px;font-size:13px;color:var(--muted);border-top:1px solid #ffffff14;padding-top:16px}}
</style></head><body><div class="wrap">
<span class="tag">Construit par builder-01 · via orchestrateur</span>
<h1>Comprendre les <span class="accent">agents autonomes</span></h1>
<p>Cette page n'a pas été écrite à la main : elle a été assemblée par le Builder
Agent à partir d'une recherche déléguée au Research Agent, puis contrôlée par
les agents Cyber et QA.</p>
<div class="grid">
 <div class="card"><h3>Recherche</h3><pre>{research[:1500]}</pre></div>
 <div class="card"><h3>Sécurité</h3><pre>{security[:1200]}</pre></div>
</div>
<div class="card" style="margin-top:16px"><h3>QA</h3><pre>{qa[:1200]}</pre></div>
<footer>Objectif : {args.objective} — généré {time.strftime('%Y-%m-%d %H:%M')}</footer>
</div></body></html>"""

        Path(args.out).write_text(html, encoding="utf-8")
        say("BUILD", f"landing page écrite : {C['g']}{args.out}{C['x']} ({len(html)} octets)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
