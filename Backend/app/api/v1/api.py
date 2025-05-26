"""
API v1 router.
"""
from fastapi import APIRouter

from .endpoints import proposals, search

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    proposals.router,
    prefix="/proposals",
    tags=["proposals"]
)

api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
)