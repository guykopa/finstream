from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class TokenRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PipelineRunRequest(BaseModel):
    business_date: date
    source: str = Field(default="fake", pattern="^(fake|csv|live)$")
    file_path: str | None = Field(default=None)
    chunk_size: int = Field(default=10_000, ge=100, le=100_000)
    quality_gate_threshold: float = Field(default=80.0, ge=0.0, le=100.0)


class PipelineRunResponse(BaseModel):
    run_id: str
    status: str
    total_records: int
    clean_records: int
    quality_score: float
    duration_seconds: float
    chunk_count: int
    started_at: datetime


class QualityReportResponse(BaseModel):
    run_id: str
    rule_name: str
    passed: bool
    failed_count: int
    error_samples: list[str]
    checked_at: datetime


class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"
    checks: dict[str, str]
