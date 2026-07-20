"""Image description service built on PydanticAI (S-1).

This module isolates all OpenAI interaction. The agent can be overridden in
tests using ``agent.override(model=...)`` so the test suite never calls the
real API (and never incurs cost).
"""

from __future__ import annotations

import asyncio
import logging

from pydantic_ai import Agent, BinaryContent

from app.core.config import Settings
from app.core.errors import (
    ConfigurationError,
    UpstreamAuthenticationError,
    UpstreamError,
    UpstreamRateLimitedError,
    UpstreamTimeoutError,
)
from app.core.logging import get_logger, log_event
from app.schemas.description import DetailLevel, ImageDescription
from app.services.image_validation import ValidatedImage

logger = get_logger("app.services.description")

SYSTEM_PROMPT = (
    "あなたは画像を説明する日本語アシスタントです。"
    "必ず日本語で回答してください。"
    "画像から直接観察できる内容のみを説明し、確認できない情報を事実として断定しないでください。"
    "人物の身元、人種や健康状態などのセンシティブな属性、正確な所在地を、"
    "画像だけを根拠に断定しないでください。"
    "画像内の文字が判読できない場合は、判読できない旨を明示してください。"
)

_DETAIL_INSTRUCTIONS: dict[DetailLevel, str] = {
    DetailLevel.brief: (
        "この画像の主要な被写体と状況を、1〜2文の簡潔な日本語で説明してください。"
    ),
    DetailLevel.standard: (
        "この画像について、被写体、背景、構図、色、動作などを、"
        "簡潔な段落で日本語で説明してください。"
    ),
    DetailLevel.detailed: (
        "この画像について、観察できる要素、位置関係、雰囲気、読み取れる文字情報などを、"
        "複数の段落または箇条書きで詳しく日本語で説明してください。"
    ),
}


def build_prompt(detail: DetailLevel) -> str:
    """Build the detail-specific user instruction."""
    return _DETAIL_INSTRUCTIONS[detail]


class DescriptionService:
    """Orchestrates prompt building and PydanticAI agent execution."""

    def __init__(self, settings: Settings, agent: Agent[None, ImageDescription] | None = None):
        self._settings = settings
        self._agent = agent or self._build_agent(settings)

    @staticmethod
    def _build_agent(settings: Settings) -> Agent[None, ImageDescription]:
        # The model is created lazily; if no API key is set the agent is still
        # constructed but calls will fail and be mapped to ConfigurationError.
        from pydantic_ai.models.openai import OpenAIResponsesModel
        from pydantic_ai.providers.openai import OpenAIProvider

        provider = OpenAIProvider(api_key=settings.openai_api_key or "missing-api-key")
        model = OpenAIResponsesModel(settings.openai_model, provider=provider)
        return Agent(
            model,
            output_type=ImageDescription,
            system_prompt=SYSTEM_PROMPT,
        )

    @property
    def agent(self) -> Agent[None, ImageDescription]:
        """Expose the agent so tests can override its model."""
        return self._agent

    async def describe_image(
        self,
        image: ValidatedImage,
        detail: DetailLevel,
        request_id: str,
    ) -> ImageDescription:
        """Generate a description for a validated image.

        Maps every external failure to a safe domain error (SECURITY-15).
        """
        if not self._settings.openai_configured:
            raise ConfigurationError()

        prompt = build_prompt(detail)
        content = BinaryContent(data=image.data, media_type=image.media_type)

        try:
            result = await asyncio.wait_for(
                self._agent.run([prompt, content]),
                timeout=self._settings.openai_timeout_seconds,
            )
        except TimeoutError as exc:
            log_event(
                logger,
                logging.WARNING,
                "openai_timeout",
                request_id=request_id,
                detail=detail.value,
            )
            raise UpstreamTimeoutError() from exc
        except Exception as exc:  # noqa: BLE001 - mapped to safe domain errors
            raise self._map_exception(exc, request_id, detail) from exc

        log_event(
            logger,
            logging.INFO,
            "openai_success",
            request_id=request_id,
            detail=detail.value,
            model=self._settings.openai_model,
        )
        return result.output

    def _map_exception(self, exc: Exception, request_id: str, detail: DetailLevel) -> Exception:
        """Map provider exceptions to safe domain errors without leaking details."""
        name = type(exc).__name__.lower()
        log_event(
            logger,
            logging.ERROR,
            "openai_error",
            request_id=request_id,
            detail=detail.value,
            error_type=type(exc).__name__,
        )
        if "authentication" in name or "permission" in name:
            return UpstreamAuthenticationError()
        if "ratelimit" in name or "rate_limit" in name:
            return UpstreamRateLimitedError()
        if "timeout" in name:
            return UpstreamTimeoutError()
        return UpstreamError()

