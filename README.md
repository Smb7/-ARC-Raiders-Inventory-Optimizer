# ARC Raiders Inventory Optimizer

Read-only companion web app that scans a player's stash via community APIs and produces a Keep / Sell / Recycle checklist.

## Stack

- Frontend: Angular 19 (standalone), RxJS, Tailwind CSS
- Backend: FastAPI (Python 3.12)
- Database: PostgreSQL 16
- Deploy: Docker Compose

## Local development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

Unit tests:

```bash
npm run test:ci
```

### Docker

```bash
docker compose up --build
```

- App: http://localhost
- API: http://localhost:8000/health

## CI

GitHub Actions runs backend pytest, Angular unit tests, and a Docker Compose smoke test on push and pull request.
