"""
Pydantic schemas for proposal API requests and responses.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class ProposalStatus(str, Enum):
    """Proposal status enumeration."""
    PENDING = "pending"
    PASSED = "passed"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    UNDER_REVIEW = "under_review"


class ProposalType(str, Enum):
    """Proposal type enumeration."""
    POSITIONSANTRAG = "Positionsantrag"
    SATZUNGSAENDERUNG = "Satzungsänderung"
    ARBEITSANTRAG = "Arbeitsantrag"
    OTHER = "Other"


class SearchType(str, Enum):
    """Search type enumeration."""
    SEMANTIC = "semantic"
    FULLTEXT = "fulltext"
    HYBRID = "hybrid"


# Base schemas
class ProposalBase(BaseModel):
    """Base proposal schema with common fields."""
    title: str = Field(..., min_length=1, max_length=500)
    proposal_number: Optional[str] = Field(None, max_length=50)
    proposal_type: Optional[ProposalType] = None
    full_content_text: str = Field(..., min_length=1)
    full_explanation_text: Optional[str] = None
    summary: Optional[str] = None
    primary_author: Optional[str] = Field(None, max_length=200)
    co_authors: List[str] = Field(default_factory=list)
    meeting_name: Optional[str] = Field(None, max_length=200)
    meeting_date: Optional[datetime] = None
    submitted_date: Optional[datetime] = None
    decided_date: Optional[datetime] = None
    status: ProposalStatus = ProposalStatus.PENDING
    votes_for: Optional[float] = Field(None, ge=0)
    votes_against: Optional[float] = Field(None, ge=0)
    votes_abstention: Optional[float] = Field(None, ge=0)
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = Field(None, max_length=100)
    submitting_organization: Optional[str] = Field(None, max_length=200)


# Create schemas
class ProposalCreate(ProposalBase):
    """Schema for creating a new proposal."""
    pass


class ProposalUpdate(BaseModel):
    """Schema for updating an existing proposal."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    proposal_number: Optional[str] = Field(None, max_length=50)
    proposal_type: Optional[ProposalType] = None
    full_content_text: Optional[str] = Field(None, min_length=1)
    full_explanation_text: Optional[str] = None
    summary: Optional[str] = None
    primary_author: Optional[str] = Field(None, max_length=200)
    co_authors: Optional[List[str]] = None
    meeting_name: Optional[str] = Field(None, max_length=200)
    meeting_date: Optional[datetime] = None
    submitted_date: Optional[datetime] = None
    decided_date: Optional[datetime] = None
    status: Optional[ProposalStatus] = None
    votes_for: Optional[float] = Field(None, ge=0)
    votes_against: Optional[float] = Field(None, ge=0)
    votes_abstention: Optional[float] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    category: Optional[str] = Field(None, max_length=100)
    submitting_organization: Optional[str] = Field(None, max_length=200)


# Response schemas
class ProposalResponse(ProposalBase):
    """Full proposal response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    processing_status: str
    processing_error: Optional[str] = None
    source_document_path: Optional[str] = None
    source_document_page: Optional[float] = None
    
    # Computed properties
    display_title: str
    author_list: List[str]
    total_votes: float
    vote_percentage_for: float


class ProposalSummary(BaseModel):
    """Summary proposal schema for search results."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    proposal_number: Optional[str] = None
    summary: Optional[str] = None
    submitted_date: Optional[datetime] = None
    status: ProposalStatus
    tags: List[str] = Field(default_factory=list)
    relevance_score: Optional[float] = None  # For search results


# Search schemas
class SearchRequest(BaseModel):
    """Search request schema."""
    q: str = Field(..., min_length=1, description="Search query")
    type: SearchType = Field(SearchType.HYBRID, description="Search type")
    limit: int = Field(20, ge=1, le=100, description="Maximum results")
    offset: int = Field(0, ge=0, description="Pagination offset")
    status: Optional[ProposalStatus] = Field(None, description="Filter by status")
    date_from: Optional[datetime] = Field(None, description="Filter by submission date from")
    date_to: Optional[datetime] = Field(None, description="Filter by submission date to")
    tags: List[str] = Field(default_factory=list, description="Filter by tags")
    category: Optional[str] = Field(None, description="Filter by category")
    submitting_organization: Optional[str] = Field(None, description="Filter by organization")


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str
    type: SearchType
    count: int = Field(..., description="Number of results returned")
    total: int = Field(..., description="Total number of matching results")
    results: List[ProposalSummary]
    took: float = Field(..., description="Search execution time in seconds")


# File upload schemas
class FileUploadResponse(BaseModel):
    """File upload response schema."""
    filename: str
    file_size: int
    upload_path: str
    processing_status: str
    message: str


# Health check schema
class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    database: bool
    redis: bool
    timestamp: datetime