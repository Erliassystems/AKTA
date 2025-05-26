"""
Proposal data model.
"""
from sqlalchemy import Column, String, Text, DateTime, ARRAY, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid

from ..database import Base


class Proposal(Base):
    """
    Proposal model representing a political proposal.
    """
    __tablename__ = "proposals"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic proposal information
    title = Column(String(500), nullable=False, index=True)
    proposal_number = Column(String(50), unique=True, index=True)
    proposal_type = Column(String(100), index=True)  # e.g., "Positionsantrag", "Satzungsänderung"
    
    # Content
    full_content_text = Column(Text, nullable=False)
    full_explanation_text = Column(Text)
    summary = Column(Text)
    
    # Authorship
    primary_author = Column(String(200))
    co_authors = Column(ARRAY(String))
    
    # Meeting/Decision information
    meeting_name = Column(String(200))
    meeting_date = Column(DateTime(timezone=True))
    submitted_date = Column(DateTime(timezone=True), index=True)
    decided_date = Column(DateTime(timezone=True))
    
    # Status and voting
    status = Column(String(50), index=True)  # e.g., "passed", "rejected", "withdrawn", "pending"
    votes_for = Column(Float)
    votes_against = Column(Float)
    votes_abstention = Column(Float)
    
    # Categorization and tagging
    tags = Column(ARRAY(String), default=[])
    category = Column(String(100), index=True)
    submitting_organization = Column(String(200), index=True)
    
    # Source document information
    source_document_path = Column(String(500))
    source_document_page = Column(Float)  # Page number in source document
    
    # Search and AI features
    embedding = Column(Vector(768))  # Vector for semantic search
    search_vector = Column(Text)  # Full-text search vector (tsvector in PostgreSQL)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Processing status
    processing_status = Column(String(50), default="pending")  # "pending", "processing", "completed", "failed"
    processing_error = Column(Text)
    
    def __repr__(self):
        return f"<Proposal(id={self.id}, title='{self.title[:50]}...', status='{self.status}')>"
    
    @property
    def display_title(self) -> str:
        """Get a display-friendly title."""
        return f"{self.proposal_number}: {self.title}" if self.proposal_number else self.title
    
    @property
    def author_list(self) -> list:
        """Get a combined list of all authors."""
        authors = []
        if self.primary_author:
            authors.append(self.primary_author)
        if self.co_authors:
            authors.extend(self.co_authors)
        return authors
    
    @property
    def total_votes(self) -> float:
        """Calculate total number of votes."""
        return sum(filter(None, [self.votes_for, self.votes_against, self.votes_abstention]))
    
    @property
    def vote_percentage_for(self) -> float:
        """Calculate percentage of votes in favor."""
        total = self.total_votes
        if total == 0 or not self.votes_for:
            return 0.0
        return (self.votes_for / total) * 100