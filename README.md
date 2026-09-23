# GH-200 team app

A one-page frontend your team deploys to its own URL on Google Cloud Run,
through a pipeline you build yourselves.

**Start with [LAB.md](LAB.md).**

| Path | What it is |
|---|---|
| `app/` | The page and its Dockerfile |
| `scripts/stamp.py` | Writes your team, commit and name into the page at build time |
| `.github/workflows/pipeline.yml` | Where you start: CI only |
| `reference/` | The finished pipeline and a rollback, for when you are stuck |
