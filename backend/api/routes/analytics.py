"""
Analytics API routes - endpoints for case analytics and insights.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date, timedelta

from utils.cache import cache_get, cache_set
from utils.database import aggregate, count_documents, find_many

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    user_id: Optional[str] = Query(None, description="User ID for personalized stats"),
):
    """Get dashboard overview statistics."""
    cache_key = f"analytics:dashboard:{user_id or 'global'}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    try:
        # Total cases in system
        total_cases = await count_documents("cases", {})
        pending_cases = await count_documents("cases", {"status": "pending"})
        disposed_cases = await count_documents("cases", {"status": "disposed"})

        # Today's cause list entries
        today = date.today().isoformat()
        today_causelists = await count_documents("causelists", {"date": today})

        # Upcoming hearings (next 7 days)
        next_week = (date.today() + timedelta(days=7)).isoformat()
        upcoming = await count_documents("cases", {
            "next_hearing_date": {"$gte": today, "$lte": next_week}
        })

        # User-specific stats
        user_stats = {}
        if user_id:
            tracked = await count_documents("tracked_cases", {"user_id": user_id, "is_active": True})
            monitors = await count_documents("monitored_cases", {"user_id": user_id, "is_active": True})
            user_stats = {"tracked_cases": tracked, "monitored_cases": monitors}

        result = {
            "success": True,
            "data": {
                "total_cases": total_cases,
                "pending_cases": pending_cases,
                "disposed_cases": disposed_cases,
                "today_causelists": today_causelists,
                "upcoming_hearings": upcoming,
                "active_rate": round(pending_cases / max(total_cases, 1) * 100, 1),
                **user_stats,
            },
        }

        await cache_set(cache_key, result, ttl=300)  # Cache 5 min
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard stats failed: {str(e)}")


@router.get("/trends")
async def get_case_trends(
    court_name: Optional[str] = Query(None),
    period: str = Query("monthly", pattern="^(daily|weekly|monthly)$"),
    months: int = Query(6, ge=1, le=24),
):
    """Get case filing and disposal trends."""
    cache_key = f"analytics:trends:{court_name}:{period}:{months}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    try:
        # Aggregation based on period
        if period == "daily":
            date_format = "%Y-%m-%d"
            group_key = {"$dateToString": {"format": date_format, "date": "$filing_date"}}
        elif period == "weekly":
            group_key = {"$isoWeek": "$filing_date"}
        else:
            date_format = "%Y-%m"
            group_key = {"$dateToString": {"format": date_format, "date": "$filing_date"}}

        match_stage = {}
        if court_name:
            match_stage["court_name"] = court_name

        pipeline = [
            {"$match": match_stage} if match_stage else {"$match": {}},
            {
                "$group": {
                    "_id": group_key,
                    "filed": {"$sum": 1},
                    "disposed": {
                        "$sum": {"$cond": [{"$eq": ["$status", "disposed"]}, 1, 0]}
                    },
                    "pending": {
                        "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                    },
                }
            },
            {"$sort": {"_id": 1}},
            {"$limit": 50},
        ]

        trends = await aggregate("cases", pipeline)

        result = {
            "success": True,
            "period": period,
            "court": court_name or "All Courts",
            "data": [
                {
                    "period": t["_id"],
                    "filed": t["filed"],
                    "disposed": t["disposed"],
                    "pending": t["pending"],
                }
                for t in trends
            ],
        }

        await cache_set(cache_key, result, ttl=1800)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trends query failed: {str(e)}")


@router.get("/court-performance")
async def get_court_performance(
    court_name: Optional[str] = Query(None),
):
    """Get court performance metrics (disposal rates, avg time, etc.)."""
    cache_key = f"analytics:performance:{court_name or 'all'}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    try:
        match_stage = {"court_name": court_name} if court_name else {}

        pipeline = [
            {"$match": match_stage} if match_stage else {"$match": {}},
            {
                "$group": {
                    "_id": "$court_name",
                    "total_cases": {"$sum": 1},
                    "disposed": {
                        "$sum": {"$cond": [{"$eq": ["$status", "disposed"]}, 1, 0]}
                    },
                    "pending": {
                        "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                    },
                    "adjourned": {
                        "$sum": {"$cond": [{"$eq": ["$status", "adjourned"]}, 1, 0]}
                    },
                }
            },
            {"$sort": {"total_cases": -1}},
        ]

        performance = await aggregate("cases", pipeline)

        result = {
            "success": True,
            "data": [
                {
                    "court": p["_id"],
                    "total_cases": p["total_cases"],
                    "disposed": p["disposed"],
                    "pending": p["pending"],
                    "adjourned": p["adjourned"],
                    "disposal_rate": round(p["disposed"] / max(p["total_cases"], 1) * 100, 1),
                    "pendency_rate": round(p["pending"] / max(p["total_cases"], 1) * 100, 1),
                }
                for p in performance
            ],
        }

        await cache_set(cache_key, result, ttl=3600)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/case-types")
async def get_case_type_distribution(
    court_name: Optional[str] = Query(None),
):
    """Get distribution of case types."""
    try:
        match_stage = {"court_name": court_name} if court_name else {}
        pipeline = [
            {"$match": match_stage} if match_stage else {"$match": {}},
            {
                "$group": {
                    "_id": "$case_type",
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"count": -1}},
        ]

        distribution = await aggregate("cases", pipeline)

        total = sum(d["count"] for d in distribution) if distribution else 0
        return {
            "success": True,
            "court": court_name or "All Courts",
            "total": total,
            "data": [
                {
                    "case_type": d["_id"],
                    "count": d["count"],
                    "percentage": round(d["count"] / max(total, 1) * 100, 1),
                }
                for d in distribution
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions")
async def get_case_predictions(
    case_number: Optional[str] = Query(None, description="Specific case to predict"),
    court_name: Optional[str] = Query(None),
):
    """Get AI-powered predictions for case outcomes."""
    try:
        from api.services.ai_service import AIService
        ai = AIService()

        if case_number:
            from utils.database import find_one
            case = await find_one("cases", {"case_number": case_number})
            if not case:
                raise HTTPException(status_code=404, detail="Case not found")

            prediction = await ai.predict_outcome(case)
            return {"success": True, "case_number": case_number, "prediction": prediction}
        else:
            # General predictions for a court
            predictions = await ai.get_court_insights(court_name or "All Courts")
            return {"success": True, "court": court_name or "All Courts", "insights": predictions}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hearings-heatmap")
async def get_hearings_heatmap(
    court_name: str = Query(..., description="Court name"),
    months: int = Query(3, ge=1, le=12),
):
    """Get a heatmap of hearing frequency by day of week and time."""
    try:
        pipeline = [
            {"$match": {"court_name": court_name}},
            {"$unwind": "$hearings"},
            {
                "$group": {
                    "_id": {"$dayOfWeek": "$hearings.date"},
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        heatmap_data = await aggregate("cases", pipeline)
        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        return {
            "success": True,
            "court": court_name,
            "data": [
                {
                    "day": day_names[d["_id"] - 1] if d["_id"] <= 7 else "Unknown",
                    "day_number": d["_id"],
                    "hearings": d["count"],
                }
                for d in heatmap_data
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
