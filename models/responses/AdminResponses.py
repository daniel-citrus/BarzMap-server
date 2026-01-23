"""
Response models for admin endpoints.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class ParkSubmissionItem(BaseModel):
    """Park submission item in the list view."""
    id: str
    title: str
    description: Optional[str] = None
    address: Optional[str] = None
    equipment: List[str] = []
    images: List[str] = []
    submittedAt: datetime
    submitter: Optional[str] = None
    moderationComment: Optional[str] = ""
    status: str

    model_config = ConfigDict(from_attributes=True)


class PaginationInfo(BaseModel):
    """Pagination metadata."""
    page: int
    pageSize: int
    totalPages: int
    totalItems: int


class ParkSubmissionsListResponse(BaseModel):
    """Response for park submissions list."""
    data: List[ParkSubmissionItem]
    pagination: PaginationInfo


class ParkSubmissionDetail(BaseModel):
    """Park submission detail view."""
    id: str
    title: Optional[str] = None
    parkName: Optional[str] = None
    description: Optional[str] = None
    parkDescription: Optional[str] = None
    address: Optional[str] = None
    parkAddress: Optional[str] = None
    equipment: List[str] = []
    images: List[str] = []
    submittedAt: Optional[datetime] = None
    date: Optional[datetime] = None
    submitter: Optional[str] = None
    user: Optional[str] = None
    moderationComment: Optional[str] = ""
    status: str

    model_config = ConfigDict(from_attributes=True)

