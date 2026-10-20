# ShopFlow

ShopFlow is a small e-commerce order-management API used as a realistic
pull-request analysys test repository. It uses FastAPI, SQLAlchemy, and SQLite.
All payment behavior is simulated; do not send real payment or customer data.

## Windows PowerShell setup

```powershell
cd "E:\Major Project\test1\ShopFlow"
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the API documentation. The API creates
its local SQLite database on startup.

Run tests with `python -m pytest`. The seeded admin is `admin@shopflow.test`
with password `admin-demo-password`; this is development-only seed data.
Register a normal user through `POST /auth/register`, sign in with
`POST /auth/login`, then send its bearer token to authenticated endpoints.
Set `SHOPFLOW_ADMIN_PASSWORD` before startup to change the local seeded admin
password. Never expose this demo configuration publicly.

## Repository scenarios

This repository includes twelve independent scenario branches and fixtures.
See [evaluation/README.md](evaluation/README.md). Useful commands:

```powershell
.\scripts\list-scenarios.ps1
.\scripts\checkout-scenario.ps1 PR-05
.\scripts\export-scenario.ps1 PR-05
.\scripts\reset-baseline.ps1
python scripts\validate_fixtures.py
```

Reset is deliberately limited to checking out the local `baseline` branch;
it does not delete files or affect another repository. Scenario scripts only
operate after verifying that their own directory is the ShopFlow Git root.
