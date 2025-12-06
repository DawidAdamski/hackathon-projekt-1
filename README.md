# 🚀 Hacknation Job Orchestrator

## 🧩 Stack technologiczny

- **FastAPI** – backend + prosty frontend (Jinja2)
- **PostgreSQL** – baza jobów
- **Celery** – system tasków (fast / slow / fail)
- **RabbitMQ** – broker komunikacji
- **Celery Beat** – periodyczne taski
- **Alembic** – migracje bazy
- **pgAdmin4** – GUI do zarządzania SQL
- **Docker Compose** – cały system odpalany jednym poleceniem
- **pytest** – testy jednostkowe / API

## 🏗️ Struktura projektu

```

backend/
app/
routes/
models/
schemas/
services/
tasks/
templates/
core/
db/
main.py
entrypoints/
api.sh
worker.sh
beat.sh
alembic/
versions/
docker-compose.yml
.env.example
Makefile

```

---

## 🔧 Instalacja i uruchomienie

### 1. Utwórz plik `.env`:

```bash
cp .env.example .env
```

Możesz tam zmienić hasła, porty oraz dane logowania do pgAdmin.

### 2. Uruchom system:

```bash
docker compose up -d --build
```

### 3. Uruchom migracje:

```bash
make migrate
```

---

## 🌐 Dostępne usługi

| Usługa        | Adres                                                    | Opis               |
| ------------- | -------------------------------------------------------- | ------------------ |
| FastAPI       | [http://localhost:8000](http://localhost:8000)           | Panel + API        |
| Swagger       | [http://localhost:8000/docs](http://localhost:8000/docs) | API docs           |
| pgAdmin       | [http://localhost:5050](http://localhost:5050)           | GUI do Postgresa   |
| RabbitMQ Mgmt | [http://localhost:15672](http://localhost:15672)         | Monitoring kolejki |

---

## 🎛️ Panel WWW

Prosty interfejs HTML pod `/`:

- Uruchamianie tasków:
  - **Fast** – natychmiastowy
  - **Slow** – 10 sekund
  - **Fail** – zawsze error

- Lista jobów + statusy aktualizowane przez worker

---

## 🔁 Celery Workers & Beat

W systemie działają:

### Worker

Obsługuje kolejki:

```
fast, slow, fail, celery
```

### Beat

Generuje zadania periodyczne, np. co X sekund:

- tworzy rekord Job w bazie
- odpala właściwy Celery task

Solidne do testowania plug&play tasków na hackathon.

---

## 🐘 pgAdmin

Login domyślny z `.env.example`:

- email: `admin@admin.com`
- hasło: `admin`

Po zalogowaniu dodaj nowy serwer:

- Host: `db`
- Port: `5432`
- User: `${POSTGRES_USER}`
- Password: `${POSTGRES_PASSWORD}`

---

## 🔨 Migracje Alembica

Wykonanie migracji:

```bash
make migrate
```

Utworzenie nowej migracji:

```bash
make makemigration m="twoj opis"
```

Reset bazy (DEV):

```bash
make reset-db
```

---

## 🧪 Testy

Testy używają **SQLite in-memory**, więc są szybkie i nie wymagają Dockera.

Uruchom testy:

```bash
cd backend
pytest -q
```

Fixtures (`conftest.py`) zapewniają:

- izolowaną testową bazę
- override FastAPI `get_db`
- testowego klienta HTTP

---

## 🛠️ Implementacja tasków

Taski znajdują się w:

```
backend/app/tasks/
```

Dostępne:

- `fast_task.py`
- `slow_task.py`
- `fail_task.py`
- `periodic_tasks.py` (dla Celery Beat)

Twój zespół może łatwo dopisywać własne taski modułami.

---

## 🧹 Dodatkowe narzędzia

- **Makefile** – skróty do zarządzania projektem
- **.gitignore** – gotowy pod Pythona + Dockera + pgAdmin + testy
