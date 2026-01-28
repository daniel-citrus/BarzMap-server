"""
API routes for Events.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.Database import get_db

router = APIRouter()
