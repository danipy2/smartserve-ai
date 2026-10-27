"""
SmartServe AI — Analytics API Routes
Endpoints for dashboard analytics and monitoring.
"""

from fastapi import APIRouter

from api.models import AnalyticsResponse
from database.db import get_analytics

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/", response_model=AnalyticsResponse)
async def get_analytics_data():
    """
    Get analytics data for the admin dashboard.
    
    Returns conversation counts, average confidence scores,
    escalation rates, daily message trends, and low-confidence queries.
    """
    analytics = get_analytics()
    return AnalyticsResponse(**analytics)
