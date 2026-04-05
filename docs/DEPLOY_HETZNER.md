# Деплой на Hetzner з Caddy (`cvc.valtive.io`)

Короткий посібник узгоджений із планом інтеграції в `/opt/docker` (мережа Docker **`web`**, існуючий **Caddy**).

## 1. DNS (реєстратор `valtive.io`)

У панелі реєстратора додай **A-запис**:

| Тип | Ім’я | Значення   |
|-----|------|------------|
| A   | `cvc`| `89.167.79.114` (IPv4 VPS) |

Після поширення DNS перевір: `dig +short cvc.valtive.io`.

## 2. Сервер: ключі, клон, `.env`

Покрокові команди — у **`hetzner-server-bootstrap.local.md`** у корені репо (файл у `.gitignore`, не комітиться). Якщо файлу немає — віднови з бекапу або з інструкцій у плані.

**Важливо:** секрети додатку лише в:

- `/opt/docker/cvc/repo/backend/.env`
- `/opt/docker/cvc/repo/frontend/.env.production`

**Не** змінюй кореневий `/opt/docker/.env` (Riznica / WordPress), якщо не впевнений.

### Прод-змінні (орієнтир)

**Backend** — див. `backend/.env.example`:

- `ALLOWED_ORIGINS=https://cvc.valtive.io`
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- `AUTH0_DOMAIN`, `AUTH0_API_AUDIENCE`, `AUTH0_CLIENT_ID`
- `AI_PROVIDER`, `GEMINI_API_KEY` / `GEMINI_MODEL` (або Anthropic)
- За потреби `ADMIN_EMAILS`

**Frontend** — див. `frontend/.env.production.example`:

- `NUXT_SESSION_PASSWORD` (32+ символів)
- `NUXT_PUBLIC_API_URL=https://cvc.valtive.io`
- Поля Auth0 (`NUXT_OAUTH_AUTH0_*`)

**Auth0 Dashboard** (SPA + API): додай для прод-домену `https://cvc.valtive.io` у Allowed Callback URLs, Logout URLs і Web Origins (шляхи залежать від `nuxt-auth-utils`).

## 3. Docker Compose і Caddy на VPS

1. **Рекомендовано:** не дублювати YAML на сервері — файл [`docker-compose.hetzner.yml`](../docker-compose.hetzner.yml) лежить у клоні (`/opt/docker/cvc/repo/`). З `/opt/docker` збирай стек двома файлами:

   ```bash
   docker compose -f docker-compose.yml -f ./cvc/repo/docker-compose.hetzner.yml config
   ```

   Якщо `config` без помилок — ті самі `-f` використовують workflow і команди `build` / `up` нижче.

   **Альтернатива:** вставити вміст `docker-compose.hetzner.yml` у єдиний `/opt/docker/docker-compose.yml` після `blog-gapta` (тоді в workflow прибери другий `-f`).

2. У **`/opt/docker/caddy/Caddyfile`** додай блок для `cvc.valtive.io` — приклад у [`Caddyfile.example`](../Caddyfile.example).

3. Застосувати:

   ```bash
   cd /opt/docker
   docker compose -f docker-compose.yml -f ./cvc/repo/docker-compose.hetzner.yml build cvc-backend cvc-frontend
   docker compose -f docker-compose.yml -f ./cvc/repo/docker-compose.hetzner.yml up -d cvc-backend cvc-frontend
   docker exec caddy caddy reload --config /etc/caddy/Caddyfile
   ```

## 4. GitHub Actions

Workflow: [`.github/workflows/deploy-production.yml`](../.github/workflows/deploy-production.yml).

### Repository secrets

| Secret | Опис |
|--------|------|
| `SSH_PRIVATE_KEY` | Приватний ключ OpenSSH для доступу CI на VPS (окремо від deploy key для `git`). |
| `SSH_HOST` | IP або DNS сервера (напр. `89.167.79.114`). |
| `SSH_USER` | Користувач SSH (напр. `root`). |
| `SSH_KNOWN_HOSTS` | Публічний «відбиток» SSH-сервера (див. нижче). |

**Навіщо `SSH_KNOWN_HOSTS`:** коли GitHub Actions підключається до твого VPS по SSH, клієнт SSH **перевіряє ключ хоста** — так він переконується, що це саме твій сервер, а не підміна в мережі (MITM). На ранері немає інтерактивного «yes/no» як у тебе в терміналі, тому треба заздалегідь покласти очікуваний ключ у `known_hosts`. Його дає команда на **твоїй** машині (підстав свій IP):

```bash
ssh-keyscan -H 89.167.79.114
```

Скопіюй **увесь** вивід (1–3 рядки, часто починаються з `89.167.79.114` або `|1|…`) у значення secret **`SSH_KNOWN_HOSTS`**. Workflow записує це в `~/.ssh/known_hosts` на ранері перед `ssh-action`. Без цього деплой часто падає з помилкою на кшталт **Host key verification failed**.

Опційно (якщо хочеш оновлювати `.env` з GitHub): multiline secrets `CVC_BACKEND_ENV`, `CVC_FRONTEND_ENV` — тоді розшир workflow за потреби; за замовчуванням workflow лише `git pull` + `docker compose build/up`.

Публічну частину ключа CI додай у **`~/.ssh/authorized_keys`** на сервері.

### Перевірка

```bash
curl -fsS https://cvc.valtive.io/health
```

Очікуй `"status":"ok"`; `"db":"ok"` — якщо Supabase налаштований.
