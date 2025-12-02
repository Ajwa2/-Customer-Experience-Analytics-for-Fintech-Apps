# Customer Experience Analytics for Fintech Apps

This repository provides a starter scaffold for Python projects focused on customer experience analytics for fintech applications.

**Quick start**

- Create and activate a virtual environment:

  Windows (PowerShell):

  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

- Run tests:

  ```powershell
  pytest -q
  ```

**Key Performance Indicators (KPIs)**

- Dev Environment Setup: repository has venv instructions, `requirements.txt`, and `.vscode` settings.
- CI: GitHub Actions runs unit tests on push/PR.
- Tests passing: `pytest` runs successfully on local and CI.
- Demonstrated skill: small, test-covered example in `src/` and `tests/`.

**Suggested folder structure**

```
├── .vscode/
│   └── settings.json
├── .github/
│   └── workflows
│       └── unittests.yml
├── .gitignore
├── requirements.txt
├── README.md
├── src/
│   └── __init__.py
├── notebooks/
│   ├── __init__.py
│   └── README.md
├── tests/
│   └── __init__.py
└── scripts/
    ├── __init__.py
    └── README.md
```

**Next steps**

- Add your analysis modules under `src/`.
- Add real notebooks into `notebooks/` (use `requirements.txt` or separate `requirements-notebooks.txt`).
- Expand CI to include linting, type checks, and coverage thresholds.
