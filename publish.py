#!/usr/bin/env python3
"""Publica no Instagram via Graph API o(s) post(s) devido(s) na fila.

Roda 1x por dia (via GitHub Actions). Pega o post mais antigo ainda nao
publicado cuja data ja chegou, cria o container de midia e publica.
Marca como publicado em fila.json (que e commitado de volta pelo workflow).

Variaveis de ambiente esperadas:
  IG_USER_ID    -> ID da conta Instagram (ou "me" no fluxo de login do Instagram)
  ACCESS_TOKEN  -> token de longa duracao com permissao de publicacao de conteudo
  IMG_BASE_URL  -> base publica das imagens (ex: https://raw.githubusercontent.com/<user>/<repo>/main/imagens)
  GRAPH_HOST    -> opcional. graph.instagram.com (login do Instagram) ou
                   graph.facebook.com (login do Facebook). Default graph.instagram.com
  GRAPH_VERSION -> opcional, default v21.0
  DRY_RUN       -> opcional, "1" so simula (nao publica)
"""
import json
import os
import sys
import time
from datetime import date
from pathlib import Path
from urllib import request, parse, error

AQUI = Path(__file__).parent
FILA = AQUI / "fila.json"

GRAPH = os.environ.get("GRAPH_VERSION", "v21.0")
GRAPH_HOST = os.environ.get("GRAPH_HOST", "graph.instagram.com")
IG_USER_ID = os.environ.get("IG_USER_ID", "me")
TOKEN = os.environ.get("ACCESS_TOKEN", "")
IMG_BASE = os.environ.get("IMG_BASE_URL", "").rstrip("/")
DRY_RUN = os.environ.get("DRY_RUN") == "1"
TZ = os.environ.get("TZ", "America/Sao_Paulo")


def hoje():
    # GitHub Actions roda em UTC; o workflow exporta TZ=America/Sao_Paulo
    return date.today()


def api_post(path, params):
    url = f"https://{GRAPH_HOST}/{GRAPH}/{path}"
    data = parse.urlencode(params).encode()
    req = request.Request(url, data=data, method="POST")
    try:
        with request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except error.HTTPError as e:
        corpo = e.read().decode()
        raise SystemExit(f"Erro Graph API ({e.code}) em {path}: {corpo}")


def publicar(item):
    image_url = f"{IMG_BASE}/{item['imagem']}"
    legenda = item["legenda"]
    print(f"  imagem: {image_url}")
    if DRY_RUN:
        print("  [DRY_RUN] criaria container e publicaria")
        return "dry-run-media-id"

    # 1) cria container de midia
    cont = api_post(f"{IG_USER_ID}/media", {
        "image_url": image_url,
        "caption": legenda,
        "access_token": TOKEN,
    })
    creation_id = cont["id"]
    print(f"  container criado: {creation_id}")

    # 2) publica (pequena espera ajuda o container ficar pronto)
    time.sleep(5)
    pub = api_post(f"{IG_USER_ID}/media_publish", {
        "creation_id": creation_id,
        "access_token": TOKEN,
    })
    media_id = pub["id"]
    print(f"  publicado: media_id={media_id}")
    return media_id


def main():
    if not DRY_RUN and not (IG_USER_ID and TOKEN and IMG_BASE):
        raise SystemExit("Faltam variaveis: IG_USER_ID, ACCESS_TOKEN, IMG_BASE_URL")

    fila = json.loads(FILA.read_text(encoding="utf-8"))
    hoje_iso = hoje().isoformat()

    # devidos = nao publicados com data <= hoje, em ordem
    devidos = [x for x in fila if not x["publicado"] and x["data"] <= hoje_iso]
    if not devidos:
        print(f"Nenhum post devido em {hoje_iso}. Nada a fazer.")
        return

    # publica apenas o mais antigo devido (1 por execucao)
    item = sorted(devidos, key=lambda x: x["data"])[0]
    print(f"Publicando post {item['post']} (agendado p/ {item['data']})...")
    media_id = publicar(item)

    item["publicado"] = True
    item["media_id"] = media_id
    item["publicado_em"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    FILA.write_text(json.dumps(fila, ensure_ascii=False, indent=2), encoding="utf-8")
    print("fila.json atualizado.")

    restantes = sum(1 for x in fila if not x["publicado"])
    print(f"Restam {restantes} posts na fila.")


if __name__ == "__main__":
    main()
