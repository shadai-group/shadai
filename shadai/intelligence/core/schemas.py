from enum import Enum
from typing import Optional

from pydantic import BaseModel


class SessionCreate(BaseModel):
    config_name: str
    llm_model: Optional[str] = None
    llm_temperature: Optional[float] = None
    llm_max_tokens: Optional[int] = None
    query_mode: Optional[str] = None
    language: Optional[str] = None


class SessionResponse(SessionCreate):
    session_id: str


class JobStatus(str, Enum):
    """Job status enumeration."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobType(str, Enum):
    INGESTION = "ingestion"
    DELETE = "delete"
    QUERY = "query"
    DELETE_SESSION = "delete_session"
    SUMMARY = "summary"
    ARTICLE = "article"
    LLM_CALL = "llm_call"


class JobResponse(BaseModel):
    """Typed job response container."""

    job_id: str
    user_id: str
    session_id: str
    job_type: JobType
    status: JobStatus
    result: Optional[str] = "in progress"
