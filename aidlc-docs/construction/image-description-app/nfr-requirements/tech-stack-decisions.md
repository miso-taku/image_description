# 技術スタック決定（サマリー）

- Backend: Python 3.12.8, uv, FastAPI, Pydantic v2, Pydantic Settings, PydanticAI, OpenAI。
- Testing: pytest, pytest-asyncio, httpx, Hypothesis（部分PBT）。
- Frontend: Next.js, React, TypeScript, Vitest, Testing Library。
- Quality: Ruff, mypy, ESLint, tsc。
- 既定モデル: gpt-4.1-mini（`OPENAI_MODEL` で変更可能）。
