# Image Description Backend

FastAPI + PydanticAI backend that generates Japanese descriptions of uploaded
images using the OpenAI API.

## Requirements

- Python 3.12.8 (uv can install it automatically)
- uv
- An OpenAI API key (only needed to generate real descriptions; the test
  suite never calls the API)

## Setup

```bash
cd backend
uv sync --extra dev
cp .env.example .env   # then edit .env and set OPENAI_API_KEY
```

On Windows PowerShell use `Copy-Item .env.example .env`.

## Run

```bash
uv run uvicorn app.main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Quality gates

```bash
uv run ruff check .
uv run mypy app
uv run pytest
```

## API

### POST /api/v1/descriptions

`multipart/form-data`:

- `image`: JPEG, PNG, or WebP, up to 10 MB
- `detail`: `brief` | `standard` | `detailed`

Returns JSON `{ description, detail, model, request_id }` or an error envelope
`{ error: { code, message, request_id } }`.

## Notes

- The OpenAI API key is read only from the environment and never logged.
- Images and generated descriptions are processed in memory and never persisted.
- The default model is `gpt-4.1-mini` (configurable via `OPENAI_MODEL`).
