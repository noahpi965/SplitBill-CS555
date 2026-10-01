# SplitBill — CS555 Agile Project

[![CI](https://github.com/noahpi965/SplitBill-CS555/actions/workflows/ci.yml/badge.svg)](https://github.com/noahpi965/SplitBill-CS555/actions/workflows/ci.yml)

A shared bill splitting system built with **React** (frontend) + **Flask** (backend) + **SQLite** (database).

## Project Structure

```
SplitBill-CS555/
├── backend/          # Flask REST API
│   ├── app.py        # App entry point & config
│   ├── models.py     # SQLAlchemy models
│   ├── routes/       # API route blueprints
│   │   ├── bills.py
│   │   └── reports.py
│   ├── tests/        # Pytest test suite
│   │   └── test_sprint1.py
│   └── requirements.txt
└── frontend/         # React SPA
    ├── index.html
    ├── src/
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── pages/
    │       ├── AddBill.jsx
    │       ├── GroupBills.jsx
    │       ├── BalanceSummary.jsx
    │       └── MonthlyReport.jsx
    └── package.json
```

## Quick Start

### Backend
```bash
cd backend
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt   # already installed if using the bundled venv
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Run Tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

## CI

GitHub Actions runs on every push and pull request to `main`:

- **Backend Tests**: install Python deps and run `pytest`
- **Frontend Build**: install npm deps and run `npm run build`


## Sprint 1 — User Stories (Todo)
| # | Story | Endpoint |
|---|-------|----------|
| US01 | Add a Shared Bill | `POST /api/bills` |
| US04 | View Group Bills | `GET  /api/bills` |
| US05 | View Balance Summary | `GET  /api/balance` |
| US06 | View Monthly Report | `GET  /api/reports/monthly` |
