# Аналіз репозиторію CV Converter — план рефакторингу

> Дата аналізу: квітень 2026  
> Стек: FastAPI (Python 3.11) + Nuxt 3 (Vue 3 / TypeScript) + Supabase + Auth0

---

## 1. Архітектурний огляд

Проєкт складається з двох сервісів:
- **Backend** — FastAPI, 6 роутерів, 9 сервісів, Supabase як БД + Storage
- **Frontend** — Nuxt 3, nuxt-auth-utils (Auth0), Nuxt UI / Tailwind

Загальна структура чиста, розподіл відповідальностей дотримано. Нижче — конкретні проблеми та пропозиції.

---

## 2. Backend

### 2.1 Rate limiting — in-memory, не персистентний

**Файл:** `backend/services/rate_limit.py`

```python
_window: dict[str, list[float]] = defaultdict(list)
```

Стан зберігається в пам'яті процесу. При рестарті контейнера ліміти скидаються — користувач може перевищити ліміт одразу після рестарту.

**Рішення (без Redis, використовуємо Supabase яка вже є):**

Таблиця `conversions` вже існує і містить `user_id` + `created_at`. Просто рахуємо записи за останню годину замість in-memory словника:

```python
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from core.config import get_settings
from core.supabase import get_supabase

def check_and_record_conversion(user_id: str) -> None:
    s = get_settings()
    sb = get_supabase()
    since = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

    res = sb.table("conversions") \
        .select("id", count="exact") \
        .eq("user_id", user_id) \
        .gte("created_at", since) \
        .execute()

    if (res.count or 0) >= s.conversions_per_hour:
        raise HTTPException(status_code=429, detail="Conversion rate limit exceeded")
    # запис в таблицю відбувається далі в роутері — нічого додаткового не потрібно
```

- нульова інфраструктура — Redis не потрібен
- виживає після рестарту сервера
- один додатковий запит до БД на конверсію — несуттєво для простої машини

---

### 2.2 `schedule_conversion` / `schedule_generation` — небезпечний `asyncio.create_task`

**Файли:** `backend/services/conversion_runner.py`, `backend/services/generation_runner.py`

```python
def schedule_conversion(conversion_id: str) -> None:
    asyncio.create_task(run_conversion_pipeline(conversion_id))
```

Проблеми:
- Task не прив'язаний до жодного event loop reference — при завершенні запиту може бути зібраний GC.
- Немає черги, немає retry-логіки, немає обмеження паралельних задач.
- При рестарті сервера всі `pending` конверсії залишаються "завислими" назавжди.

**Реалізовано (мінімальний підхід без Redis/Celery):**
- Модуль-рівнева множина `_running_tasks: set[asyncio.Task]` в обох runner-файлах — task зберігається до завершення, `done_callback` очищає.
- `recover_pending_conversions()` / `recover_pending_generations()` — при старті сервера шукають записи зі `status IN ('pending','processing'/'generating')` і перезапускають їх через `schedule_*`.
- `lifespan` у `main.py` викликає обидві функції відновлення перед стартом застосунку.

---

### 2.3 Дублювання логіки AI-провайдера

**Файли:** `backend/services/ai_service.py`, `backend/services/generation_runner.py`, `backend/services/vacancy_parser.py`

Логіка вибору провайдера (Gemini / Anthropic) та виклику API дублюється в трьох місцях:

```python
provider = (s.ai_provider or "gemini").strip().lower()
if provider == "gemini":
    ...
if provider == "anthropic":
    ...
```

**Пропозиція:**
- Виділити єдиний `AIClient` (або `AIProvider` protocol/ABC) у `core/ai_client.py`.
- Реалізувати `GeminiClient` і `AnthropicClient`, які реалізують спільний інтерфейс.
- Усі сервіси отримують клієнт через DI або фабрику `get_ai_client()`.

---

### 2.4 `_jwks_json` кешується назавжди через `lru_cache`

**Файл:** `backend/core/auth.py`

```python
@lru_cache(maxsize=1)
def _jwks_json(domain: str) -> dict:
```

JWKS ротується Auth0 при зміні ключів. Якщо ключ змінився — сервіс почне відхиляти всі токени до рестарту.

**Пропозиція:**
- Замінити `lru_cache` на кеш з TTL (наприклад, `cachetools.TTLCache` з TTL 1 година).
- Або зберігати `jwks` у змінній з `last_fetched` timestamp і рефетчити при помилці верифікації.

---

### 2.5 `get_supabase()` викликається всередині функцій, а не через DI

**Файли:** усі роутери та сервіси

```python
sb = get_supabase()  # викликається напряму всередині функції
```

Це ускладнює тестування (потрібно патчити `get_supabase` у кожному модулі окремо) і не дозволяє FastAPI керувати lifecycle клієнта.

**Пропозиція:**
- Зробити `get_supabase` FastAPI dependency (`Depends(get_supabase)`) у роутерах.
- Сервіси приймають `sb` як параметр, а не викликають `get_supabase()` самостійно.

---

### 2.6 `health` endpoint — синхронний блокуючий виклик до БД

**Файл:** `backend/main.py`

```python
@app.get("/health")
def health():
    sb = get_supabase()
    sb.table("profiles").select("id").limit(1).execute()
```

Синхронний запит у async-контексті блокує event loop.

**Пропозиція:**
- Зробити endpoint `async` і обернути виклик у `asyncio.to_thread(...)`.
- Або використати легший ping без запиту до таблиці.

---

### 2.7 `vacancy_parser.extract_text_from_url` — async функція, але викликається через `asyncio.to_thread`

**Файл:** `backend/routers/generate.py` + `backend/services/vacancy_parser.py`

`extract_text_from_url` є `async def`, але в `generation_runner.py` URL-обробка відбувається синхронно через `raw_input = vacancy_url.strip()` без реального fetch. Fetch відбувається пізніше в pipeline, але не через `to_thread`. Потрібна перевірка узгодженості async/sync меж.

**Пропозиція:**
- Аудит усіх `asyncio.to_thread` викликів — переконатись, що передаються лише синхронні функції.
- `extract_text_from_url` має викликатись напряму `await`, а не через `to_thread`.

---

### 2.8 Відсутній `updated_at` тригер у схемі БД

**Файл:** `backend/supabase/schema.sql`

Поле `updated_at` є у таблицях, але немає тригера для автоматичного оновлення.

**Пропозиція:**
```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at BEFORE UPDATE ON conversions
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
-- аналогічно для vacancies, generated_cvs
```

---

### 2.9 `error_message` обрізається до 2000 символів без логування повного тексту

**Файли:** `conversion_runner.py`, `generation_runner.py`

```python
"error_message": str(e)[:2000],
```

Повний стектрейс логується через `logger.exception`, але в БД зберігається лише початок. Це нормально, але варто переконатись, що логи централізовані.

**Пропозиція:**
- Додати structured logging (наприклад, `structlog`) для кращого пошуку по `conversion_id`.
- Розглянути інтеграцію з Sentry для трекінгу помилок у продакшені.

---

### 2.10 `prompt_service` — глобальний in-memory кеш без thread-safety

**Файл:** `backend/services/prompt_service.py`

```python
_cache: dict[str, tuple[str, float]] = {}
```

При конкурентних запитах можливі race conditions при записі в словник (хоча CPython GIL частково захищає, це не гарантія).

**Пропозиція:**
- Використати `threading.Lock` або `asyncio.Lock` для захисту кешу.
- Або замінити на `cachetools.TTLCache` з thread-safe реалізацією.

---

### 2.11 Відсутня пагінація в history endpoints

**Файли:** `backend/routers/history.py`, `backend/routers/admin.py`

```python
sb.table("conversions").select(...).eq("user_id", ...).order(...).execute()
```

Немає `limit`/`offset` або cursor-based пагінації. При великій кількості записів — повне завантаження.

**Пропозиція:**
- Додати query params `?page=1&per_page=20` або `?cursor=<id>`.
- Повертати `{ items, total, next_cursor }` у відповіді.

---

### 2.12 `admin.py` — N+1 запит вирішено, але немає захисту від великих вибірок

**Файл:** `backend/routers/admin.py`

N+1 вирішено через `in_()` запит для профілів — добре. Але немає ліміту на кількість конверсій, що повертаються адміну.

**Пропозиція:**
- Додати пагінацію аналогічно п. 2.11.
- Додати фільтри за датою, статусом, user_id.

---

## 3. Frontend

### 3.1 Дублювання логіки авторизаційних заголовків

**Файли:** `frontend/composables/useApi.ts`, `frontend/components/ConversionCard.vue`

`ConversionCard.vue` реалізує власну функцію `apiHeaders()` замість використання `useApiRequest()`:

```typescript
// ConversionCard.vue — дублікат логіки
function apiHeaders(): Record<string, string> {
  const token = session.value?.accessToken as string | undefined
  ...
}
```

**Пропозиція:**
- Використовувати `useApiRequest()` скрізь, включно з `ConversionCard.vue`.
- Видалити локальну `apiHeaders()` функцію з компонента.

---

### 3.2 Polling через `setInterval` без exponential backoff

**Файл:** `frontend/pages/history.vue`

```typescript
timers[id] = setInterval(async () => { ... }, POLL_INTERVAL_MS)
```

Фіксований інтервал polling — при довгих операціях генерує зайві запити. Немає обмеження кількості спроб.

**Пропозиція:**
- Реалізувати exponential backoff: 2s → 4s → 8s → 16s → max 30s.
- Додати максимальну кількість спроб (наприклад, 30) після якої встановлювати статус `failed`.
- Розглянути WebSocket або SSE для real-time оновлень замість polling.

---

### 3.3 `generate-history.vue` — помилки ігноруються мовчки

**Файл:** `frontend/pages/generate-history.vue`

```typescript
catch { /* ignore */ }
```

Помилки завантаження та видалення ковтаються без жодного повідомлення користувачу.

**Пропозиція:**
- Додати `error` ref і відображати повідомлення про помилку в UI.
- Використати `useToast()` з Nuxt UI для нотифікацій.

---

### 3.4 `statusLabel` / `statusClasses` дублюються між сторінками

**Файли:** `frontend/pages/generate-history.vue`, `frontend/components/StatusBadge.vue`

Логіка маппінгу статусів реалізована в кількох місцях.

**Пропозиція:**
- Винести в окремий composable `useStatusDisplay()` або розширити `StatusBadge.vue` для підтримки всіх статусів обох flow (conversion + generation).

---

### 3.5 Відсутні frontend тести для сторінок і composables

**Директорія:** `frontend/tests/`

Структура тестів є (`tests/components/`, `tests/pages/`, `tests/composables/`), але наповнення невідоме / мінімальне.

**Пропозиція:**
- Покрити `useApiRequest` composable unit-тестами.
- Додати тести для `history.vue` polling логіки.
- Додати тести для `middleware/auth.global.ts`.

---

### 3.6 Hardcoded CSS змінні замість Tailwind токенів

**Файли:** більшість `.vue` компонентів

```html
class="text-[var(--cv-primary-dark)] bg-[var(--cv-teal-accent)]"
```

CSS змінні використовуються напряму в Tailwind arbitrary values. Це ускладнює рефакторинг теми.

**Пропозиція:**
- Зареєструвати CSS змінні як Tailwind токени в `tailwind.config`:
  ```js
  colors: { 'cv-primary': 'var(--cv-primary-dark)', ... }
  ```
- Використовувати `text-cv-primary` замість `text-[var(--cv-primary-dark)]`.

---

### 3.7 `confirm()` для підтвердження видалення

**Файл:** `frontend/components/ConversionCard.vue`

```typescript
if (!confirm(`Remove "${props.filename}" from your history?...`)) return
```

Нативний `confirm()` блокує UI, не стилізується, не підтримується в деяких середовищах (SSR).

**Пропозиція:**
- Замінити на модальне вікно підтвердження через `UModal` з Nuxt UI.

---

## 4. DevOps / Інфраструктура

### 4.1 `docker-compose.yml` — `NUXT_PUBLIC_API_URL` hardcoded як `localhost`

**Файл:** `docker-compose.yml`

```yaml
args:
  NUXT_PUBLIC_API_URL: http://localhost:8000
```

Build arg вшивається в образ під час збірки. У продакшені потрібен інший URL.

**Пропозиція:**
- Не передавати публічний API URL як build arg — передавати через runtime env.
- Або використовувати відносні URL на фронтенді (`/api/...`) і проксувати через Caddy/Nginx.

---

### 4.2 `.dockerignore` — неповний перелік виключень

**Файл:** `backend/.dockerignore`

Файл існує і містить `__pycache__`, `*.pyc`, `.env`, `venv`, `.git`. Але відсутні тести та кеш-директорії — вони потрапляють у Docker образ.

**Пропозиція:**
- Додати до `backend/.dockerignore`:
  ```
  tests/
  .pytest_cache/
  .hypothesis/
  .coverage
  ```

---

### 4.3 Відсутній health check у `docker-compose.yml`

**Файл:** `docker-compose.yml`

`depends_on: backend` не гарантує, що backend готовий приймати запити.

**Пропозиція:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 10s
  timeout: 5s
  retries: 5
```
І `depends_on: backend: condition: service_healthy` для frontend.

---

## 5. Тести

### 5.1 `conftest.py` — `_ChainableMock` дублюється в деяких тест-файлах

**Файл:** `backend/tests/conftest.py`

`make_supabase_mock()` є в `conftest.py`, але деякі тести (`test_conversion_runner.py`) визначають власний локальний mock замість використання фікстури.

**Пропозиція:**
- Уніфікувати: всі тести використовують `mock_supabase` фікстуру з `conftest.py`.
- Видалити локальні дублікати mock-налаштувань.

---

### 5.2 Відсутні інтеграційні тести для generation pipeline

**Файл:** `backend/tests/services/test_generation_runner.py`

Тести покривають happy path і failure, але не тестують часткові збої (наприклад, embedding fails але pipeline продовжується).

**Пропозиція:**
- Додати тест: `embedding_service.store_embedding` кидає виняток → pipeline все одно завершується (або коректно фейлиться).
- Додати тест для URL-input flow у `generate.py` роутері.

---

### 5.3 Відсутні тести для `admin.py` роутера

**Директорія:** `backend/tests/routers/`

Немає тестів для адмін-ендпоінтів.

**Пропозиція:**
- Додати тести: доступ без admin role → 403, додавання/видалення email, перегляд конверсій.

---

## 6. Додаткові знахідки (виявлені при верифікації)

### 6.1 Широкі `except Exception` без логування у роутерах

**Файли:** `backend/routers/generate.py`, `backend/routers/convert.py`, `backend/routers/history.py`

5 місць з `except Exception` що ковтають помилки:

```python
# generate.py:137, convert.py:78 — download_url тихо стає None
except Exception:
    out["download_url"] = None

# generate.py:155, :212 — повне ігнорування помилок
except Exception:
    pass  # non-critical

# history.py:25 — логується, але не пробрасовується
except Exception:
    logger.exception("Storage remove failed for %s objects", len(batch))
```

Для `download_url` fallback до `None` прийнятний, але відсутнє логування приховує реальні проблеми (наприклад, протермінований signed URL ключ).

**Пропозиція:**
- Для `download_url`: додати `logger.warning(...)` перед fallback, щоб мати видимість.
- Для `generate.py:155` (`pass`): embedding update провалюється тихо — додати `logger.exception(...)` щоб знати про збої.
- Для `generate.py:212` (delete storage): аналогічно — логувати, навіть якщо не фейлити запит.

---

### 6.2 Відсутні `frontend/.dockerignore`

**Директорія:** `frontend/`

У frontend директорії немає `.dockerignore`. Це означає, що `node_modules/`, `.nuxt/`, тести та інші артефакти потрапляють у Docker build context.

**Пропозиція:**
- Створити `frontend/.dockerignore`:
  ```
  node_modules/
  .nuxt/
  .output/
  tests/
  .env
  .env.*
  ```

---

## 7. Пріоритизований план впровадження

| Пріоритет | Задача | Складність | Статус |
|-----------|--------|------------|--------|
| 🔴 Критично | 2.2 — Замінити `asyncio.create_task` на чергу задач (ARQ/Celery) | Висока | ✅ Виконано |
| 🔴 Критично | 2.1 — Персистентний rate limiting (Supabase, без Redis) | Низька | ✅ Виконано |
| 🟠 Важливо | 2.3 — Уніфікований AIClient | Середня | ✅ Виконано |
| 🟠 Важливо | 2.4 — TTL-кеш для JWKS | Низька | ✅ Виконано |
| 🟠 Важливо | 3.1 — Прибрати дублювання auth headers у ConversionCard | Низька | ✅ Виконано |
| 🟠 Важливо | 3.3 — Обробка помилок у generate-history.vue | Низька | ✅ Виконано |
| 🟠 Важливо | 6.1 — Логування в `except Exception` блоках роутерів | Низька | ✅ Виконано |
| 🟡 Бажано | 2.5 — Supabase через FastAPI Depends | Середня | ✅ Виконано |
| 🟡 Бажано | 2.11 — Пагінація в history endpoints | Середня | ✅ Виконано |
| 🟡 Бажано | 3.2 — Exponential backoff для polling | Низька | ✅ Виконано |
| 🟡 Бажано | 4.3 — Health check у docker-compose | Низька | ✅ Виконано |
| 🟡 Бажано | 2.8 — `updated_at` тригери в БД | Низька | ✅ Виконано |
| 🟡 Бажано | 6.2 — Створити `frontend/.dockerignore` | Низька | ✅ Виконано |
| 🔵 Покращення | 3.6 — Tailwind токени замість CSS змінних | Середня | ✅ Виконано |
| 🔵 Покращення | 3.7 — UModal замість `confirm()` | Низька | ✅ Виконано |
| 🔵 Покращення | 5.1–5.3 — Розширення тестового покриття | Середня | ✅ Виконано |
| 🔵 Покращення | 2.9 — Structured logging / Sentry | Середня | ⏭ Відкладено |
