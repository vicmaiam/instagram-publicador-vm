#!/usr/bin/env python3
"""Gera AGENDA.md (calendario legivel) a partir de fila.json."""
import json
from pathlib import Path

AQUI = Path(__file__).parent
fila = json.loads((AQUI / "fila.json").read_text(encoding="utf-8"))

linhas = [
    "# Agenda de publicacao",
    "",
    "Gerado automaticamente de `fila.json`. ✅ = ja publicado · ⏳ = agendado.",
    "",
    "| Data | Post | Status | Imagem | Inicio da legenda |",
    "|------|------|--------|--------|-------------------|",
]
for x in fila:
    status = "✅" if x["publicado"] else "⏳"
    primeira = next((l for l in x["legenda"].splitlines() if l.strip()), "")
    if len(primeira) > 70:
        primeira = primeira[:70] + "…"
    primeira = primeira.replace("|", "\\|")
    linhas.append(f"| {x['data']} | {x['post']} | {status} | {x['imagem']} | {primeira} |")

linhas += [
    "",
    "## Legendas completas",
    "",
]
for x in fila:
    status = "✅ publicado" if x["publicado"] else "⏳ agendado"
    linhas.append(f"### Post {x['post']} — {x['data']} ({status})")
    linhas.append(f"Imagem: `{x['imagem']}`")
    linhas.append("")
    linhas.append(x["legenda"])
    linhas.append("")
    linhas.append("---")
    linhas.append("")

(AQUI / "AGENDA.md").write_text("\n".join(linhas), encoding="utf-8")
print(f"AGENDA.md gerado ({len(fila)} posts).")
