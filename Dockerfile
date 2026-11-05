FROM ghcr.io/astral-sh/uv:0.13.7-python3.14-trixie-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-cache
COPY alembic.ini ./
COPY alembic/ alembic/
COPY app/ app/

FROM python:3.14.10-slim-trixie AS runtime
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY --from=builder /app /app
RUN useradd --no-create-home appuser && chown -R appuser /app
USER appuser
EXPOSE 8000
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
