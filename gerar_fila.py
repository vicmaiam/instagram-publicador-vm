#!/usr/bin/env python3
"""Gera fila.json a partir do arquivo de legendas e das imagens 51-100.

Pareia Post N -> N.png, atribui uma data por dia a partir de DATA_INICIO
e grava tudo em fila.json. Rode novamente sempre que mudar as legendas.
"""
import json
import re
from datetime import date, timedelta
from pathlib import Path

AQUI = Path(__file__).parent
LEGENDAS = AQUI.parent / "posts-prev-51-100" / "legendas-instagram-51-100.md"
SAIDA = AQUI / "fila.json"

DATA_INICIO = date(2026, 6, 4)   # post 51 publica neste dia
PRIMEIRO, ULTIMO = 51, 100       # intervalo de posts

texto = LEGENDAS.read_text(encoding="utf-8")

# Quebra em blocos por "Legenda Post N"
partes = re.split(r"(?m)^Legenda Post\s+(\d+)\s*$", texto)
# partes = ['', '51', '<conteudo>', '52', '<conteudo>', ...]
legendas = {}
for i in range(1, len(partes), 2):
    n = int(partes[i])
    conteudo = partes[i + 1]
    # remove separadores "---" e espacos das bordas
    conteudo = re.sub(r"(?m)^\s*-{3,}\s*$", "", conteudo).strip()
    legendas[n] = conteudo

fila = []
dia = DATA_INICIO
for n in range(PRIMEIRO, ULTIMO + 1):
    if n not in legendas:
        raise SystemExit(f"Legenda do post {n} nao encontrada")
    fila.append({
        "post": n,
        "data": dia.isoformat(),
        "imagem": f"{n}.png",
        "legenda": legendas[n],
        "publicado": False,
        "media_id": None,
        "publicado_em": None,
    })
    dia += timedelta(days=1)

SAIDA.write_text(json.dumps(fila, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"fila.json gerado com {len(fila)} posts ({fila[0]['data']} a {fila[-1]['data']})")
