"""
Search endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from typing import List, Optional
import time
import logging

from ....database import get_db
from ....models.proposal import Proposal
from ....schemas.proposal import (
    SearchRequest,
    SearchResponse,
    ProposalSummary,
    SearchType,
    ProposalStatus
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=SearchResponse)
async def search_proposals(
    q: str = Query(..., min_length=1, description="Search query"),
    type: SearchType = Query(SearchType.HYBRID, description="Search type"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    status: Optional[ProposalStatus] = Query(None, description="Filter by status"),
    date_from: Optional[str] = Query(None, description="Filter by submission date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter by submission date to (YYYY-MM-DD)"),
    tags: List[str] = Query(default=[], description="Filter by tags"),
    category: Optional[str] = Query(None, description="Filter by category"),
    submitting_organization: Optional[str] = Query(None, description="Filter by organization"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search proposals using various methods.
    
    - **q**: Search query string
    - **type**: Search type (semantic, fulltext, hybrid)
    - **limit**: Maximum number of results (1-100)
    - **offset**: Pagination offset
    - **status**: Filter by proposal status
    - **date_from/date_to**: Filter by submission date range
    - **tags**: Filter by tags (can specify multiple)
    - **category**: Filter by category
    - **submitting_organization**: Filter by submitting organization
    """
    start_time = time.time()
    
    try:
        # Build base query
        query = select(Proposal)
        conditions = []
        
        # Add search conditions based on type
        if type == SearchType.FULLTEXT:
            # Full-text search using PostgreSQL's text search
            search_condition = func.to_tsvector('german', Proposal.full_content_text).match(q)
            conditions.append(search_condition)
        elif type == SearchType.SEMANTIC:
            # TODO: Implement semantic search using embeddings
            # For now, fall back to simple text matching
            logger.warning("Semantic search not yet implemented, falling back to text search")
            search_condition = or_(
                Proposal.title.ilike(f"%{q}%"),
                Proposal.full_content_text.ilike(f"%{q}%"),
                Proposal.summary.ilike(f"%{q}%")
            )
            conditions.append(search_condition)
        else:  # HYBRID
            # Combine full-text and simple text search
            search_condition = or_(
                func.to_tsvector('german', Proposal.full_content_text).match(q),
                Proposal.title.ilike(f"%{q}%"),
                Proposal.summary.ilike(f"%{q}%")
            )
            conditions.append(search_condition)
        
        # Add filters
        if status:
            conditions.append(Proposal.status == status.value)
        
        if date_from:
            conditions.append(Proposal.submitted_date >= date_from)
        
        if date_to:
            conditions.append(Proposal.submitted_date <= date_to)
        
        if tags:
            # Check if any of the provided tags match
            tag_conditions = [Proposal.tags.any(tag) for tag in tags]
            conditions.append(or_(*tag_conditions))
        
        if category:
            conditions.append(Proposal.category.ilike(f"%{category}%"))
        
        if submitting_organization:
            conditions.append(Proposal.submitting_organization.ilike(f"%{submitting_organization}%"))
        
        # Apply all conditions
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Proposal.created_at.desc()).offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        proposals = result.scalars().all()
        
        # Convert to response format
        proposal_summaries = []
        for proposal in proposals:
            summary = ProposalSummary(
                id=proposal.id,
                title=proposal.title,
                proposal_number=proposal.proposal_number,
                summary=proposal.summary[:200] + "..." if proposal.summary and len(proposal.summary) > 200 else proposal.summary,
                submitted_date=proposal.submitted_date,
                status=proposal.status,
                tags=proposal.tags or [],
                relevance_score=1.0  # TODO: Calculate actual relevance score
            )
            proposal_summaries.append(summary)
        
        execution_time = time.time() - start_time
        
        return SearchResponse(
            query=q,
            type=type,
            count=len(proposal_summaries),
            total=total,
            results=proposal_summaries,
            took=execution_time
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/similar/{proposal_id}")
async def find_similar_proposals(
    proposal_id: str,
    limit: int = Query(5, ge=1, le=20, description="Maximum similar proposals"),
    db: AsyncSession = Depends(get_db),
):
    """
    Find proposals similar to the given proposal.
    
    Currently uses basic text similarity. Will be enhanced with semantic similarity.
    """
    try:
        # Get the base proposal
        result = await db.execute(select(Proposal).where(Proposal.id == proposal_id))
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # TODO: Implement semantic similarity using embeddings
        # For now, use simple text-based similarity
        query = select(Proposal).where(
            and_(
                Proposal.id != proposal_id,
                or_(
                    Proposal.category == proposal.category,
                    Proposal.tags.overlap(proposal.tags or []),
                    func.similarity(Proposal.title, proposal.title) > 0.3
                )
            )
        ).limit(limit)
        
        result = await db.execute(query)
        similar_proposals = result.scalars().all()
        
        # Convert to response format
        similar_summaries = []
        for similar in similar_proposals:
            summary = ProposalSummary(
                id=similar.id,
                title=similar.title,
                proposal_number=similar.proposal_number,
                summary=similar.summary[:200] + "..." if similar.summary and len(similar.summary) > 200 else similar.summary,
                submitted_date=similar.submitted_date,
                status=similar.status,
                tags=similar.tags or [],
                relevance_score=0.8  # TODO: Calculate actual similarity score
            )
            similar_summaries.append(summary)
        
        return similar_summaries
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Similar search error: {e}")
        raise HTTPException(status_code=500, detail="Similar search failed")