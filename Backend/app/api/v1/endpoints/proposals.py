"""
Proposal CRUD endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import logging
from uuid import UUID

from ...database import get_db
from ...models.proposal import Proposal
from ...schemas.proposal import (
    ProposalCreate,
    ProposalUpdate,
    ProposalResponse,
    ProposalSummary
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
async def create_proposal(
    proposal_data: ProposalCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new proposal.
    """
    try:
        # Create new proposal instance
        proposal = Proposal(
            title=proposal_data.title,
            proposal_number=proposal_data.proposal_number,
            proposal_type=proposal_data.proposal_type.value if proposal_data.proposal_type else None,
            full_content_text=proposal_data.full_content_text,
            full_explanation_text=proposal_data.full_explanation_text,
            summary=proposal_data.summary,
            primary_author=proposal_data.primary_author,
            co_authors=proposal_data.co_authors,
            meeting_name=proposal_data.meeting_name,
            meeting_date=proposal_data.meeting_date,
            submitted_date=proposal_data.submitted_date,
            decided_date=proposal_data.decided_date,
            status=proposal_data.status.value,
            votes_for=proposal_data.votes_for,
            votes_against=proposal_data.votes_against,
            votes_abstention=proposal_data.votes_abstention,
            tags=proposal_data.tags,
            category=proposal_data.category,
            submitting_organization=proposal_data.submitting_organization,
        )
        
        db.add(proposal)
        await db.commit()
        await db.refresh(proposal)
        
        logger.info(f"Created proposal: {proposal.id}")
        return proposal
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating proposal: {e}")
        raise HTTPException(status_code=500, detail="Failed to create proposal")


@router.get("", response_model=List[ProposalSummary])
async def list_proposals(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a list of all proposals (paginated).
    """
    try:
        query = select(Proposal).offset(skip).limit(limit).order_by(Proposal.created_at.desc())
        result = await db.execute(query)
        proposals = result.scalars().all()
        
        # Convert to summary format
        summaries = []
        for proposal in proposals:
            summary = ProposalSummary(
                id=proposal.id,
                title=proposal.title,
                proposal_number=proposal.proposal_number,
                summary=proposal.summary[:200] + "..." if proposal.summary and len(proposal.summary) > 200 else proposal.summary,
                submitted_date=proposal.submitted_date,
                status=proposal.status,
                tags=proposal.tags or [],
            )
            summaries.append(summary)
        
        return summaries
        
    except Exception as e:
        logger.error(f"Error listing proposals: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve proposals")


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific proposal by ID.
    """
    try:
        result = await db.execute(select(Proposal).where(Proposal.id == proposal_id))
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        return proposal
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving proposal {proposal_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve proposal")


@router.put("/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(
    proposal_id: UUID,
    proposal_update: ProposalUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing proposal.
    """
    try:
        result = await db.execute(select(Proposal).where(Proposal.id == proposal_id))
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # Update fields
        update_data = proposal_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "proposal_type" and value:
                setattr(proposal, field, value.value)
            elif field == "status" and value:
                setattr(proposal, field, value.value)
            else:
                setattr(proposal, field, value)
        
        await db.commit()
        await db.refresh(proposal)
        
        logger.info(f"Updated proposal: {proposal.id}")
        return proposal
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating proposal {proposal_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update proposal")


@router.delete("/{proposal_id}")
async def delete_proposal(
    proposal_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a proposal.
    """
    try:
        result = await db.execute(select(Proposal).where(Proposal.id == proposal_id))
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        await db.delete(proposal)
        await db.commit()
        
        logger.info(f"Deleted proposal: {proposal_id}")
        return {"message": "Proposal deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting proposal {proposal_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete proposal")


@router.get("/stats/overview")
async def get_proposals_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    Get overview statistics about proposals.
    """
    try:
        # Total count
        total_result = await db.execute(select(func.count(Proposal.id)))
        total_count = total_result.scalar()
        
        # Count by status
        status_result = await db.execute(
            select(Proposal.status, func.count(Proposal.id))
            .group_by(Proposal.status)
        )
        status_counts = dict(status_result.all())
        
        # Count by category
        category_result = await db.execute(
            select(Proposal.category, func.count(Proposal.id))
            .where(Proposal.category.isnot(None))
            .group_by(Proposal.category)
            .order_by(func.count(Proposal.id).desc())
            .limit(10)
        )
        category_counts = dict(category_result.all())
        
        return {
            "total_proposals": total_count,
            "by_status": status_counts,
            "by_category": category_counts,
        }
        
    except Exception as e:
        logger.error(f"Error getting proposal stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")