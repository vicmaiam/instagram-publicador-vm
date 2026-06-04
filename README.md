# Publicador Instagram VM Advogados (Graph API)

Publica automaticamente **1 post por dia** no Instagram `@vmadvogados.prev`, via
Graph API oficial da Meta, agendado por um GitHub Actions que roda na nuvem todo
dia às **09:00 (horário de Brasília)**.

Campanha atual: posts **51 a 100** (50 dias, de 04/06/2026 a 23/07/2026).

## Como funciona

- `imagens/` — as 50 artes (`51.png` … `100.png`)
- `fila.json` — a fila: para cada post, a data, a imagem e a legenda
- `publish.py` — pega o post devido do dia e publica via Graph API
- `gerar_fila.py` — regenera `fila.json` a partir das legendas (datas e pareamento)
- `.github/workflows/publicar.yml` — agendador diário (GitHub Actions)

A cada execução o script publica **o post mais antigo ainda não publicado cuja
data já chegou** e marca como publicado em `fila.json` (commitado de volta). Se um
dia falhar, no dia seguinte ele pega o atrasado primeiro (sem furar a ordem).

---

## Setup (uma vez)

### 1. Conta e app na Meta (fluxo "login do Instagram")

1. `@vmadvogados.prev` precisa ser conta **Profissional (Business)** e estar
   vinculada a uma **Página do Facebook**.
2. Em [developers.facebook.com](https://developers.facebook.com) crie um app com o
   caso de uso **"Gerenciar mensagens e conteúdo no Instagram"** (API do Instagram
   com login do Instagram).
3. Em **Permissões e recursos**, adicione:
   - `instagram_business_basic`
   - `instagram_business_content_publish`
4. Em **Funções do app → Funções**, adicione `vmadvogados.prev` como
   **Testador do Instagram** e **aceite o convite** dentro do app do Instagram
   (Configurações → Apps e sites → Convites de testador). Sem isso, o token dá erro
   "Função de desenvolvedor é insuficiente".
5. Em **Configuração da API com login do Instagram**, conecte a conta e clique em
   **Gerar token de acesso**. Esse token de longa duração (~60 dias) é o `ACCESS_TOKEN`.

> O `IG_USER_ID` não é necessário: neste fluxo o script publica via `me` usando
> `GRAPH_HOST=graph.instagram.com` (já configurado no workflow).
> O token dura ~60 dias e cobre a campanha (50 dias). Antes de vencer, gere outro
> e atualize o secret `ACCESS_TOKEN`.

### 2. Repositório no GitHub

1. Crie um repositório **público** (a Meta precisa baixar as imagens por URL
   pública; o token NUNCA fica no repo, vai como secret criptografado).
2. Suba este conteúdo (veja comandos abaixo).
3. Em **Settings → Secrets and variables → Actions → New repository secret**, crie:
   - `ACCESS_TOKEN` = o token gerado no passo 1.5
4. Se o Actions acusar **"account is locked due to a billing issue"**, cadastre um
   método de pagamento em [github.com/settings/billing](https://github.com/settings/billing).
   Em repositório público o Actions é gratuito e ilimitado; o cartão é só para
   desbloquear (não há cobrança).

### 3. Subir os arquivos

```bash
cd instagram-graph-publisher
git init
git add .
git commit -m "Campanha Instagram posts 51-100"
git branch -M main
git remote add origin https://github.com/<SEU_USUARIO>/<SEU_REPO>.git
git push -u origin main
```

### 4. Testar antes de valer

Na aba **Actions** do repo → workflow **Publicar Instagram** → **Run workflow**:
- coloque `dry_run = 1` para simular (não publica nada, só mostra o que faria).
- depois rode com `dry_run = 0` para publicar o post do dia de verdade.

Como a campanha começa em **04/06**, o primeiro `Run workflow` (com `dry_run=0`)
já publica o post 51. Os próximos saem sozinhos todo dia às 09:00.

---

## Mudar horário ou datas

- **Horário:** edite o `cron` em `.github/workflows/publicar.yml` (está em UTC;
  09:00 BRT = `0 12 * * *`).
- **Datas / nova campanha:** ajuste `DATA_INICIO`, `PRIMEIRO`, `ULTIMO` em
  `gerar_fila.py`, troque as imagens em `imagens/`, rode `python3 gerar_fila.py`
  e dê push.

## Limites e cuidados

- Limite da Meta: 100 publicações por API a cada 24h (folga enorme para 1/dia).
- A API publica foto, carrossel, vídeo/Reels e Stories. O `publish.py` atual faz **foto única**;
  os outros tipos precisam estender o script. Imagens: doc pede JPEG, mas PNG funcionou na prática.
- Se o token vencer, o workflow falha com erro 190 — basta gerar novo token e
  atualizar o secret `ACCESS_TOKEN`.
