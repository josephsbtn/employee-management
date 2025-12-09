# Employee Management

![CI](https://github.com/josephsbtn/employee-management/actions/workflows/ci.yml/badge.svg) ![tests](https://img.shields.io/badge/tests-55%20passed-brightgreen) ![version](https://img.shields.io/badge/version-0.1.0-blue) ![license](https://img.shields.io/badge/license-See_LICENSE-lightgrey)

A lightweight Flask-based Employee Management system providing attendance tracking, leave/annual request handling, employee profiles, history logs, and basic store/shift management. The project is organized with clear separation between routes, services, and repository layers and uses MongoDB as its data store.

**Key features**

- Attendance recording and history
- Annual/leave request submission and attachment handling
- Employee profile management and authentication
- Shift and branch management scaffolding
- Service/repository separation to improve testability

**Tech stack & dependencies**

- Python (3.8+ recommended)
- Flask
- MongoDB (pymongo)
- JWT auth via `Flask-JWT-Extended`
- See `requirements.txt` for full dependency list

**Repository layout (important parts)**

- `main.py` — application entrypoint and Flask app
- `routes/` — Flask Blueprints that define HTTP endpoints
- `service/` — business logic layer
- `repo/` — data access repositories for MongoDB
- `templates/`, `static/` — UI templates and static assets
- `utils/` — configuration and MongoDB connection helpers
- `tests/` — unit and functional tests

**Why this project is useful**

- Provides a starting point for building HR/attendance tooling
- Demonstrates clear project layering (routes → services → repos)
- Includes examples of form validation, file uploads, and JWT auth

--

**Getting started**

Prerequisites

- Python 3.8+ installed
- MongoDB accessible (cloud or local)

1. Clone the repository

```powershell
git clone <repo-url>
cd employee-management
```

2. Create and activate a virtual environment (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4. Configuration

- The project reads configuration from `utils/config.py`. For development, create a `.env` (or override `utils/config.Config`) — see `.env.example` for recommended variables. Example values:

```text
MONGO_URI=mongodb://localhost:27017
DATABASE=aventra_db
JWT_SECRET_KEY=some_very_secret_key
```

Note: `utils/config.py` currently contains default values. Do not commit secrets to source control; prefer using environment variables or a `.env` file in real deployments.

5. Run the app (development)

```powershell
python main.py
# App runs with Flask builtin server at http://127.0.0.1:5000
```

6. Production (example using gunicorn)

```powershell
# Use gunicorn with eventlet worker for production (example)
gunicorn main:app -w 4 -k eventlet --bind 0.0.0.0:8000
```

**Endpoints and usage**

- Web pages are under `templates/` and served by `routes/pageRoutes.py`.
- API endpoints are prefixed in `main.py` when Blueprints are registered, e.g.:
  - `/api/employees` — employee operations
  - `/api/attendance` — attendance endpoints
  - `/api/annualRequest` — annual/leave request endpoints
  - `/auth` — authentication endpoints

For quick exploration, inspect the `routes/` directory to see available routes and example request/response payloads.

**Testing**

- Unit and service tests live in `tests/`. To run tests locally:

```powershell
pytest -q
```

- Test results (local run on Dec 9, 2025): **Service functional tests — 55 passed, 0 failed**.

There are also functional/integration tests and non-functional load scripts under `non-functional/`.

**Development notes**

- Database connection is handled by `utils/mongoConnect.py` and reads `Config.MONGO_URI` and `Config.DATABASE` from `utils/config.py`.
- Input validation uses `marshmallow` schemas located in `validation/`.
- Keep business logic in `service/` so controllers remain thin and testable.

**Where to get help**

- Open an issue in this repository for bug reports or feature requests.
- Inspect `tests/` and `htmlcov/` for test examples and current coverage reports.

**Contributing**

- Thanks for considering contributing! Please follow standard GitHub workflows.
- See `CONTRIBUTING.md` for contribution guidelines.

**Maintainers**

- Repository owner: `josephsbtn` (see repository metadata)

**Next steps / Suggestions**

- Add a `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` for contributor guidance.
- Replace placeholder badges with CI badges when CI is configured.
- Move secrets out of `utils/config.py` into environment variables or a secure secrets manager.

---

If you'd like, I can also:

- add a `CONTRIBUTING.md` scaffold
- create a `.env.example` file with recommended env variables
- add a GitHub Actions workflow badge and basic CI workflow

Feel free to tell me which of the above I should do next.
