"""Round-trip property tests for API schemas (PBT-02)."""

from __future__ import annotations

import json

from hypothesis import given
from hypothesis import strategies as st

from app.schemas.description import DescriptionResponse, DetailLevel
from app.schemas.error import ErrorBody, ErrorResponse


@given(
    description=st.text(min_size=0, max_size=500),
    detail=st.sampled_from(list(DetailLevel)),
    model=st.text(min_size=1, max_size=40),
    request_id=st.uuids().map(str),
)
def test_description_response_round_trip(
    description: str, detail: DetailLevel, model: str, request_id: str
) -> None:
    original = DescriptionResponse(
        description=description, detail=detail, model=model, request_id=request_id
    )
    restored = DescriptionResponse.model_validate(json.loads(original.model_dump_json()))
    assert restored == original


@given(
    code=st.text(min_size=1, max_size=40),
    message=st.text(min_size=1, max_size=200),
    request_id=st.uuids().map(str),
)
def test_error_response_round_trip(code: str, message: str, request_id: str) -> None:
    original = ErrorResponse(error=ErrorBody(code=code, message=message, request_id=request_id))
    restored = ErrorResponse.model_validate(json.loads(original.model_dump_json()))
    assert restored == original
