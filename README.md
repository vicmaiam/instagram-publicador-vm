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

### 1. Conta e app na Meta

1. `@vmadvogados.prev` precisa ser conta **Profissional (Business)** e estar
   vinculada a uma **Página do Facebook**.
2. Em [developers.facebook.com](https://developers.facebook.com) crie um app do
   tipo **Business**.
3. Adicione o produto **Instagram Graph API** (ou "Instagram" / "Facebook Login").
4. No **Graph API Explorer**, gere um token com as permissões:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
   - `business_management`
5. Descubra o **Instagram Business Account ID** (o `IG_USER_ID`):
   - `GET /me/accounts` → pega o `id` da Página
   - `GET /{page-id}?fields=instagram_business_account` → retorna o `IG_USER_ID`
6. Troque o token curto por um **token de longa duração** (~60 dias):
   ```
   GET https://graph.facebook.com/v21.0/oauth/access_token
       ?grant_type=fb_exchange_token
       &client_id={APP_ID}
       &client_secret={APP_SECRET}
       &fb_exchange_token={TOKEN_CURTO}
   ```

> O token de longa duração dura ~60 dias e cobre toda a campanha (50 dias). Antes
> de vencer, gere outro e atualize o secret `ACCESS_TOKEN`.

### 2. Repositório no GitHub

1. Crie um repositório **público** (a Meta precisa baixar as imagens por URL
   pública; o token NUNCA fica no repo, vai como secret criptografado).
2. Suba este conteúdo (veja comandos abaixo).
3. Em **Settings → Secrets and variables → Actions → New repository secret**, crie:
   - `IG_USER_ID` = o ID do passo 1.5
   - `ACCESS_TOKEN` = o token de longa duração do passo 1.6

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
- Stories e Reels **não** são suportados por este fluxo (só foto única e carrossel).
- Se o token vencer, o workflow falha com erro 190 — basta gerar novo token e
  atualizar o secret `ACCESS_TOKEN`.
