"""Domain error hierarchy and safe error handling (SECURITY-15).

Every error surfaced to the client is mapped to a stable code and a generic,
user-safe message. Internal details are never exposed to the client.
"""

from __future__ import annotations


class AppError(Exception):
    """Base application error mapped to a safe client response."""

    code: str = "internal_error"
    http_status: int = 500
    default_message: str = "予期しないエラーが発生しました。時間をおいて再試行してください。"
    retryable: bool = False

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class InvalidImageTypeError(AppError):
    code = "invalid_image_type"
    http_status = 400
    default_message = "JPEG、PNG、WebP形式の画像を選択してください。"


class EmptyImageError(AppError):
    code = "empty_image"
    http_status = 400
    default_message = "空の画像ファイルはアップロードできません。"


class ImageTooLargeError(AppError):
    code = "image_too_large"
    http_status = 413
    default_message = "画像サイズが上限を超えています。10MB以下の画像を選択してください。"


class InvalidDetailError(AppError):
    code = "invalid_detail"
    http_status = 400
    default_message = "説明の詳しさは brief、standard、detailed のいずれかを指定してください。"


class ConfigurationError(AppError):
    code = "configuration_error"
    http_status = 503
    default_message = "サーバーの設定が不完全です。管理者に連絡してください。"


class UpstreamAuthenticationError(AppError):
    code = "authentication_error"
    http_status = 502
    default_message = "画像解析サービスの認証に失敗しました。管理者に連絡してください。"


class UpstreamRateLimitedError(AppError):
    code = "rate_limited"
    http_status = 429
    default_message = "画像解析サービスが混み合っています。時間をおいて再試行してください。"
    retryable = True


class UpstreamTimeoutError(AppError):
    code = "upstream_timeout"
    http_status = 504
    default_message = "画像解析がタイムアウトしました。時間をおいて再試行してください。"
    retryable = True


class UpstreamError(AppError):
    code = "upstream_error"
    http_status = 502
    default_message = "画像解析サービスでエラーが発生しました。時間をおいて再試行してください。"
    retryable = True


class LocalRateLimitedError(AppError):
    code = "rate_limited_local"
    http_status = 429
    default_message = "リクエストが多すぎます。少し待ってから再試行してください。"
    retryable = True
