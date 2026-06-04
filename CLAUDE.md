# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All tasks run via `mise run <task>`. The toolchain (Python 3.14, uv) is pinned in `mise.toml`.

| Task | Command |
|---|---|
| Install dependencies | `mise run install` |
| Dev server | `mise run dev` |
| Production server | `mise run serve` |
| Format | `mise run fmt` |
| Lint | `mise run lint` |
| Type check | `mise run typecheck` |
| Vulnerability audit | `mise run vuln` |
| Run tests | `mise run test` |
| Upgrade dependencies | `mise run deps` |

## Architecture

`app/main.py` owns the FastAPI application. Routes are registered under `/documents` via `app/routers/documents.py`.

- `app/config.py` — pydantic-settings config, loaded from `.env`
- `app/database.py` — SQLAlchemy engine and session factory
- `app/models.py` — ORM models (`Document`, `DocumentChunk` with pgvector embedding)
- `app/crud.py` — database query helpers
- `app/ingest.py` — PDF and DOCX text extraction
- `app/llm.py` — Ollama-backed summarisation and Q&A via LangChain

Database migrations live in `alembic/`. Run `alembic upgrade head` after standing up the PostgreSQL container (`docker compose up -d db`).

Tests live in `tests/`. `tests/conftest.py` sets environment variables before any app imports so the module-level settings load succeeds without a real database or Ollama instance. The `get_db` dependency is overridden with a `MagicMock` session in each test.
