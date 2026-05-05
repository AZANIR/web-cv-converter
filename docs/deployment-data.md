# CVC на сервері Valtive — контекст для AI-агентів у Cursor

> **Призначення цього файлу.** Це довідник для агентів, які працюють із кодом CVC (Web CV Converter) у Cursor. Тут описано, **як саме сервіс задеплоєно на продакшн-сервері Valtive (Hetzner)**, де лежить код, як ходять HTTP-запити, де брати логи і які команди використовувати при діагностиці. Це **не** інструкція по самому коду — лише інфраструктурний контекст.

---

## 1. TL;DR — що треба знати в першу чергу

- Прод крутиться на **Hetzner Cloud, IP `77.42.20.229`** (hostname `ubuntu-4gb-valtive`), Ubuntu 24.04.
- Домен — **`cvc.valtive.io`**, SSL автоматично через Caddy + Let's Encrypt.
- Сервіс складається з **двох контейнерів**: `cvc-frontend` (Next.js, порт `3000`) і `cvc-backend` (FastAPI/uvicorn, порт `8000`).
- Все живе у `/opt/docker/cvc/`. Репозиторій клонується в `/opt/docker/cvc/repo/` (GitHub: `AZANIR/web-cv-converter`, гілка `master`).
- Ззовні **порти 3000 і 8000 НЕ відкриті** — їх бачить тільки Caddy через внутрішню Docker-мережу `web`.
- Деплой — через **GitHub Actions** (push у `master` → CI пушить у `ghcr.io` → SSH на сервер → `git pull` + `docker compose build` + `docker compose up -d`).

---

## 2. Доступ до сервера

| Параметр | Значення |
|---|---|
| Хостер | Hetzner Cloud |
| IP | `77.42.20.229` |
| Hostname | `ubuntu-4gb-valtive` |
| ОС | Ubuntu 24.04.4 LTS (4 GB RAM, ~38 GB диск) |
| SSH | `ssh root@77.42.20.229` (тільки за ключем, парольний вхід вимкнено) |
| GUI (опційно) | XFCE через XRDP по SSH-тунелю, користувач `desktopuser` (порт 3389 слухає тільки `127.0.0.1`) |

> **Агент не виконує SSH сам.** Якщо потрібно щось перевірити на сервері — формулюй конкретну команду і проси користувача її виконати, або давай повний блок команд, який можна скопіювати в SSH-сесію.

---

## 3. Загальний стек на сервері

- **Docker + Docker Compose** — кожен сервіс у власній папці у `/opt/docker/`, свій `docker-compose.yml`.
- **Caddy 2 (Alpine) у контейнері** — єдиний reverse proxy для всіх доменів сервера, авто-SSL.
- **Зовнішня Docker-мережа `web`** — створюється стеком Caddy, до неї підключаються всі сервіси (зокрема обидва контейнери CVC).

Окрім CVC, на цьому ж сервері крутиться: `wiki.valtive.io` (Wiki.js + Postgres), `riznica.com.ua` (WordPress + WooCommerce + MariaDB), `coolify-sentinel`. **Не чіпати їх при роботі з CVC.**

---

## 4. Структура каталогів CVC

```
/opt/docker/cvc/
├── docker-compose.yml         ← оркеструє два контейнери (frontend + backend)
└── repo/                      ← git clone https://github.com/AZANIR/web-cv-converter (гілка master)
    ├── Dockerfile             ← (або окремі Dockerfile-и під фронт/бек)
    ├── docker-compose.hetzner.yml  ← можливий override для прод (історично використовувався)
    ├── frontend/              ← Next.js
    ├── backend/               ← FastAPI (Python, uvicorn)
    └── ...
```

> Точна структура `repo/` визначається самим репозиторієм — агент має дивитися безпосередньо в нього. Тут описана лише обгортка на сервері.

---

## 5. Контейнери CVC (поточний стан з `docker ps`)

| Container name | Image | Команда | Внутрішній порт |
|---|---|---|---|
| `cvc-frontend` | `cvc-cvc-frontend` (build з repo) | `docker-entrypoint.sh` (Next.js) | `3000` |
| `cvc-backend` | `cvc-cvc-backend` (build з repo) | `uvicorn main:app --...` | `8000` |

Обидва підключені до зовнішньої мережі `web`. **Жодних `ports:` на 0.0.0.0 у compose немає** — це принцип сервера: 80/443 робить тільки Caddy.

Compose: `/opt/docker/cvc/docker-compose.yml`. Реєстр у `docker compose ls`:
```
cvc                 running(2)          /opt/docker/cvc/docker-compose.yml
```

---

## 6. Caddy routing — як HTTP-запит до `cvc.valtive.io` потрапляє в контейнер

Файл: `/opt/docker/caddy/Caddyfile`

```caddy
cvc.valtive.io {
    handle /api/auth/*   { reverse_proxy cvc-frontend:3000 }
    handle /api/_auth/*  { reverse_proxy cvc-frontend:3000 }
    handle /api/*        { reverse_proxy cvc-backend:8000 }
    handle /health       { reverse_proxy cvc-backend:8000 }
    handle /health/*     { reverse_proxy cvc-backend:8000 }
    handle               { reverse_proxy cvc-frontend:3000 }
}
```

**Логіка маршрутизації — важливо для розуміння помилок:**

| URL | Куди йде | Чому |
|---|---|---|
| `/api/auth/...` | **frontend** (3000) | NextAuth-роут, обробляється Next.js |
| `/api/_auth/...` | **frontend** (3000) | Внутрішня логіка NextAuth |
| `/api/*` (інші) | **backend** (8000) | Бізнес-API на FastAPI |
| `/health`, `/health/*` | **backend** (8000) | Healthcheck бекенду |
| Усе інше (`/`, статика, сторінки) | **frontend** (3000) | Next.js рендерить UI |

> **Якщо агент бачить помилку на запиті — спочатку треба зрозуміти, який контейнер її повернув**, виходячи з URL. Наприклад, 500 на `/api/users` — це backend, а 500 на `/api/auth/session` — це frontend.

Caddy працює як `reverse_proxy` за іменем контейнера в Docker DNS — `cvc-frontend` і `cvc-backend` резолвляться в IP контейнера всередині мережі `web`.

---

## 7. Логи — основний інструмент діагностики

Усі команди виконувати на сервері від `root`.

### 7.1. Швидкий огляд

```bash
# Усе, що крутиться, з image і статусом
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

# Конкретно CVC + Caddy
docker ps --filter "name=cvc" --filter "name=caddy" \
  --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### 7.2. Логи frontend (Next.js)

```bash
# Останні 200 рядків
docker logs cvc-frontend --tail 200

# Стрім у реальному часі (Ctrl+C для виходу)
docker logs cvc-frontend -f

# З timestamp
docker logs cvc-frontend --tail 200 --timestamps

# За останні 30 хвилин
docker logs cvc-frontend --since 30m
```

### 7.3. Логи backend (FastAPI/uvicorn)

```bash
docker logs cvc-backend --tail 200
docker logs cvc-backend -f
docker logs cvc-backend --since 30m --timestamps
```

### 7.4. Логи Caddy (404, 502, проблеми SSL, неправильний роутинг)

```bash
docker logs caddy --tail 100
docker logs caddy -f | grep cvc.valtive.io
```

> Якщо frontend або backend повертає помилку — у логах Caddy буде статус (502 = контейнер не відповідає, 504 = таймаут, 404 = не знайдено маршруту).

### 7.5. Грепи за конкретним запитом

```bash
# Шукаємо стектрейси у backend
docker logs cvc-backend --tail 500 2>&1 | grep -A 20 "Traceback"

# Шукаємо помилки Next.js
docker logs cvc-frontend --tail 500 2>&1 | grep -iE "error|warn"

# Усі 5xx у Caddy за конкретним доменом
docker logs caddy --tail 1000 2>&1 | grep cvc.valtive.io | grep -E '"status":5'
```

### 7.6. Файлові логи FastAPI (генерація CV з вакансії)

Бекенд пише в **stderr** (це і є `docker logs cvc-backend`) і, якщо вдалося створити файл, у **`/app/logs/backend.log`** (змінна `LOG_FILE_PATH` у `backend/.env`, типово `/app/logs/backend.log`).

У `docker-compose.hetzner.yml` рекомендовано змонтувати `./cvc/repo/backend/logs:/app/logs`, щоб ротація логів не губилася при пересозданні контейнера. Якщо том не змонтовано або каталог незаписний, бекенд усе одно логуватиме лише в stderr — див. `docker logs cvc-backend`.

Помилки пайплайну «вакансія → CV» шукати так:

```bash
docker logs cvc-backend --tail 500 2>&1 | grep -E "Generation pipeline failed|ERROR \[services.generation_runner\]"
```

Переконайся, що в `.env` бекенду не виставлено занадто високий рівень, наприклад `LOG_LEVEL=ERROR` — тоді `INFO` не видно; для діагностики зазвичай достатньо `INFO`.

### 7.7. Зайти всередину контейнера (для дебагу)

```bash
# Frontend
docker exec -it cvc-frontend sh

# Backend (Python образи зазвичай мають bash)
docker exec -it cvc-backend bash
# або
docker exec -it cvc-backend sh
```

Усередині можна, наприклад, перевірити змінні оточення (`env`), доступ до бази/зовнішніх сервісів (`curl`, `wget`, якщо встановлені), глянути конфіги.

---

## 8. Перезапуск і перебудова

Перейти в папку проєкту:
```bash
cd /opt/docker/cvc
```

### 8.1. М'який рестарт (без перезбірки)
```bash
docker compose restart
# або тільки один контейнер:
docker compose restart cvc-frontend
docker compose restart cvc-backend
```

### 8.2. Підняти (якщо щось упало)
```bash
docker compose up -d
```

### 8.3. Перебудувати образи з поточного стану `repo/` (підтягти зміни з git і пересобрати)
```bash
cd /opt/docker/cvc/repo
git status
git pull origin master
cd /opt/docker/cvc
docker compose build
docker compose up -d
```

### 8.4. Перезавантажити Caddy після правок Caddyfile (без рестарту контейнера)
```bash
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```

> CI зазвичай робить кроки 8.3 автоматично — ручний запуск потрібен лише якщо CI впав або агент тестує локальну зміну на сервері.

---

## 9. CI/CD — як зміни потрапляють на прод

- Репозиторій: **`AZANIR/web-cv-converter`**, гілка **`master`**.
- На push у `master` запускається **GitHub Actions**:
  1. Білдить образи й пушить у `ghcr.io`.
  2. По SSH ходить на `77.42.20.229`, у папку `/opt/docker/cvc/`.
  3. Робить `git pull` у `repo/` + `docker compose build` + `docker compose up -d`.
- Workflow очікує саме структуру `/opt/docker/cvc/` — **не міняти шлях без оновлення workflow**.

> Якщо агент пропонує зміни в `Dockerfile` або `docker-compose.yml` — пам'ятати, що вони підхопляться тільки після наступного push у `master` і прогону CI (або ручного rebuild на сервері).

---

## 10. Швидкий чек-ліст при «щось зламалося на cvc.valtive.io»

Виконувати по порядку, поки не знайдеться причина:

```bash
# 1. Чи живі контейнери взагалі?
docker ps --filter "name=cvc"
# Очікуємо два рядки зі статусом "Up". Якщо хтось "Restarting" або відсутній — джамп до п.4.

# 2. Чи відповідає сервіс ззовні?
curl -I https://cvc.valtive.io
curl -I https://cvc.valtive.io/health

# 3. Свіжі логи обох контейнерів (помилки, стектрейси)
docker logs cvc-frontend --tail 100 --timestamps
docker logs cvc-backend  --tail 100 --timestamps

# 4. Якщо контейнер падає — дивимося чому
docker logs cvc-frontend --tail 300
docker logs cvc-backend  --tail 300
# Часто бачимо: відсутні env, помилка міграції БД, не зміг прочитати файл

# 5. Caddy: чи бачить він контейнери, чи нема 502
docker logs caddy --tail 50 | grep cvc.valtive.io

# 6. Мережа: чи в одній мережі `web` усі троє
docker network inspect web | grep -E "cvc-|caddy"

# 7. Ресурси сервера (диск часто 70%+ — може бути причиною)
df -h /
free -h

# 8. Якщо потрібен повний рестарт сервісу
cd /opt/docker/cvc && docker compose restart

# 9. Якщо потрібна перебудова з останнім кодом
cd /opt/docker/cvc/repo && git pull
cd /opt/docker/cvc && docker compose build && docker compose up -d
```

---

## 11. Типові симптоми → де шукати

| Симптом | Найімовірніша причина | Куди дивитися |
|---|---|---|
| `502 Bad Gateway` на будь-якій сторінці | Контейнер frontend упав / не стартував | `docker ps`, `docker logs cvc-frontend` |
| `502` тільки на `/api/*` (не auth) | Контейнер backend упав / висить | `docker logs cvc-backend` |
| `500` на сторінці, але контейнер живий | Помилка в коді Next.js (SSR) | `docker logs cvc-frontend --tail 200` — шукати stack trace |
| `500` на `/api/...` (не auth) | Виняток у FastAPI | `docker logs cvc-backend` — шукати `Traceback` |
| Логін не працює, `/api/auth/...` дає 500 | Проблема NextAuth (env, секрети, redirect URL) | `docker logs cvc-frontend`, перевірити env у `docker-compose.yml` |
| SSL-помилка / неправильний сертифікат | Caddy не зміг отримати/продовжити Let's Encrypt | `docker logs caddy --tail 200` |
| Дані «зникли» / БД не відповідає | Volume не змонтовано / БД-контейнер не стартував | `docker volume ls`, `docker logs <db-container>` (якщо він є для CVC) |
| `no space left on device` у логах | Диск переповнений (на Valtive ~38 GB, легко забити) | `df -h /`, `docker system df`, чистка `docker system prune -a` (з обережністю) |

---

## 12. Чого **НЕ** робити (правила сервера)

- ❌ **Не пробрасувати** порти 3000/8000 на 0.0.0.0 у compose. Тільки внутрішня мережа `web`. Якщо треба локально для дебагу — `127.0.0.1:3000`, не публічно.
- ❌ **Не редагувати** Caddyfile через `cat >>` — легко зламати конфіг. Тільки `nano` + `docker exec caddy caddy validate --config /etc/caddy/Caddyfile` перед reload.
- ❌ **Не видаляти** volumes без явного бекапу.
- ❌ **Не повертати** монолітний `/opt/docker/docker-compose.yml` — кожен сервіс у своїй папці.
- ❌ **Не забувати** `restart: unless-stopped` у compose — інакше після ребуту сервер підніметься без сервісу.
- ❌ **Не міняти** `container_name` у compose — Caddy проксить саме за цим іменем (`cvc-frontend`, `cvc-backend`). Зміна імені = `502` поки не оновити Caddyfile.
- ❌ **Не чіпати** інші сервіси на сервері (`wiki`, `blog-valtive`, `db-valtive`, `caddy`) при роботі з CVC.

---

## 13. Корисні посилання й артефакти на сервері

- Compose CVC: `/opt/docker/cvc/docker-compose.yml`
- Код CVC: `/opt/docker/cvc/repo/` (гілка `master` з `github.com/AZANIR/web-cv-converter`)
- Caddyfile: `/opt/docker/caddy/Caddyfile`
- Compose Caddy: `/opt/docker/caddy/docker-compose.yml`
- Логи всіх контейнерів: `docker logs <name>` (зберігаються Docker-ом, не файлами на ФС)
- Загальна документація сервера: `Структура_сервера_Valtive.md` (у тому ж проєкті)

---

## 14. Що дати агенту разом з цим файлом

Щоб агент у Cursor міг ефективно діагностувати помилку, корисно одразу прикласти:

1. **Цей файл** — як інфраструктурний контекст.
2. **Конкретний URL/запит**, на якому ламається (щоб агент зрозумів, frontend це чи backend — див. п.6).
3. **Свіжі логи** відповідного контейнера (мінімум 100 останніх рядків з `--timestamps`).
4. **Скріншот або текст помилки** з браузера / DevTools (status code + response body).
5. **Вивід `docker ps`** — щоб бачити, що контейнери живі і скільки часу.
