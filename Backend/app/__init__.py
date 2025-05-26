# Backend/app/__init__.py
"""AKTA Backend Application"""

# Backend/app/models/__init__.py
"""Data models for AKTA"""
from .proposal import Proposal

__all__ = ["Proposal"]

# Backend/app/schemas/__init__.py  
"""Pydantic schemas for AKTA API"""
from .proposal import (
    ProposalCreate,
    ProposalUpdate, 
    ProposalResponse,
    ProposalSummary,
    SearchRequest,
    SearchResponse
)

__all__ = [
    "ProposalCreate",
    "ProposalUpdate", 
    "ProposalResponse",
    "ProposalSummary",
    "SearchRequest", 
    "SearchResponse"
]

# Backend/app/api/__init__.py
"""API modules"""

# Backend/app/api/v1/__init__.py
"""API v1 modules"""

# Backend/app/api/v1/endpoints/__init__.py
"""API v1 endpoints"""

# Backend/app/core/__init__.py
"""Core modules"""