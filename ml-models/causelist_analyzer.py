"""
Cause List Analyzer - Pattern detection and anomaly analysis for cause lists.
"""

import logging
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, date, timedelta, timezone
from collections import Counter, defaultdict

import numpy as np  # type: ignore[import-not-found]
import pandas as pd  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)


class CauseListAnalyzer:
    """Detect patterns, anomalies, and trends in cause lists."""

    def __init__(self):
        self.history: List[Dict] = []  # Historical cause list data

    def load_history(self, cause_lists: List[Dict]):
        """Load historical cause list data for analysis."""
        self.history = cause_lists
        logger.info(f"Loaded {len(cause_lists)} cause list records for analysis")

    def analyze_volume_trends(self, court_name: Optional[str] = None) -> Dict:
        """Analyze cause list volume trends over time."""
        filtered = self.history
        if court_name:
            filtered = [cl for cl in filtered if cl.get("court_name") == court_name]

        if not filtered:
            return {"error": "No data available"}

        # Group by date
        daily_volumes: Dict[str, int] = defaultdict(int)
        for cl in filtered:
            cl_date = cl.get("date", "")
            entries = cl.get("entries", [])
            daily_volumes[cl_date] += len(entries)  # type: ignore[index]

        dates = sorted(daily_volumes.keys())
        volumes = [daily_volumes[d] for d in dates]

        # Calculate statistics
        vol_array = np.array(volumes) if volumes else np.array([0])
        avg_volume = float(np.mean(vol_array))
        std_volume = float(np.std(vol_array))
        max_volume = float(np.max(vol_array))
        min_volume = float(np.min(vol_array))

        # Trend detection (simple linear regression)
        trend = "stable"
        if len(volumes) >= 5:
            x = np.arange(len(volumes))
            coeffs = np.polyfit(x, volumes, 1)
            slope = coeffs[0]
            if slope > 0.5:
                trend = "increasing"
            elif slope < -0.5:
                trend = "decreasing"

        # Day of week analysis
        dow_volumes: Dict[str, List[int]] = defaultdict(list)
        for d, v in daily_volumes.items():
            try:
                parsed = datetime.fromisoformat(d).date()
                dow = parsed.strftime("%A")
                dow_volumes[dow].append(v)
            except (ValueError, TypeError):
                pass

        busiest_days = {
            day: round(float(np.mean(vols)), 1)  # type: ignore[call-overload]
            for day, vols in sorted(dow_volumes.items(), key=lambda x: -float(np.mean(x[1])))
        }

        return {
            "court": court_name or "All Courts",
            "total_days": len(dates),
            "average_daily_cases": round(float(avg_volume), 1),  # type: ignore[call-overload]
            "std_deviation": round(float(std_volume), 1),  # type: ignore[call-overload]
            "max_daily_cases": int(max_volume),
            "min_daily_cases": int(min_volume),
            "trend": trend,
            "busiest_days": busiest_days,
            "date_range": {"from": dates[0] if dates else None, "to": dates[-1] if dates else None},
        }

    def detect_anomalies(self, court_name: Optional[str] = None, threshold: float = 2.0) -> List[Dict]:
        """Detect unusual cause list patterns (anomaly detection)."""
        filtered = self.history
        if court_name:
            filtered = [cl for cl in filtered if cl.get("court_name") == court_name]

        # Daily volumes
        daily_volumes: Dict[str, int] = defaultdict(int)
        for cl in filtered:
            daily_volumes[cl.get("date", "")] += len(cl.get("entries", []))  # type: ignore[index]

        if not daily_volumes:
            return []

        volumes = list(daily_volumes.values())
        mean_vol = np.mean(volumes)
        std_vol = np.std(volumes)

        if std_vol == 0:
            return []

        anomalies = []
        for d, vol in daily_volumes.items():
            z_score = (vol - mean_vol) / std_vol
            if abs(z_score) > threshold:
                anomalies.append({
                    "date": d,
                    "volume": vol,
                    "z_score": round(float(z_score), 2),  # type: ignore[call-overload]
                    "type": "high" if float(z_score) > 0 else "low",
                    "deviation": f"{abs(round(float(z_score), 1))}x standard deviation",  # type: ignore[call-overload]
                })

        return sorted(anomalies, key=lambda x: abs(x["z_score"]), reverse=True)

    def analyze_case_type_distribution(self, court_name: Optional[str] = None) -> Dict:
        """Analyze distribution of case types in cause lists."""
        filtered = self.history
        if court_name:
            filtered = [cl for cl in filtered if cl.get("court_name") == court_name]

        case_types = Counter()
        for cl in filtered:
            for entry in cl.get("entries", []):
                ct = entry.get("case_type", "unknown")
                case_types[ct] += 1

        total = sum(case_types.values()) or 1

        return {
            "court": court_name or "All Courts",
            "total_entries": total,
            "distribution": [
                {
                    "case_type": ct,
                    "count": count,
                    "percentage": round(float(count / total * 100), 1),  # type: ignore[call-overload]
                }
                for ct, count in case_types.most_common()
            ],
        }

    def analyze_judge_workload(self, court_name: Optional[str] = None) -> Dict:
        """Analyze workload distribution across judges/benches."""
        filtered = self.history
        if court_name:
            filtered = [cl for cl in filtered if cl.get("court_name") == court_name]

        judge_cases: Dict[str, int] = defaultdict(int)
        judge_dates: Dict[str, Set[str]] = defaultdict(set)

        for cl in filtered:
            bench = cl.get("bench") or cl.get("judge_name") or "Unknown"
            cl_date = cl.get("date", "")
            entries = cl.get("entries", [])
            judge_cases[bench] += len(entries)  # type: ignore[index]
            judge_dates[bench].add(cl_date)

        if not judge_cases:
            return {"error": "No judge data available"}

        judges = []
        for judge, total in sorted(judge_cases.items(), key=lambda x: -x[1]):
            days = len(judge_dates[judge])
            judges.append({
                "judge": judge,
                "total_cases": total,
                "days_active": days,
                "avg_daily_cases": round(float(total / max(days, 1)), 1),  # type: ignore[call-overload]
            })

        return {
            "court": court_name or "All Courts",
            "total_judges": len(judges),
            "judges": judges,
        }

    def find_repeat_adjournments(self, court_name: Optional[str] = None) -> List[Dict]:
        """Find cases that appear repeatedly in cause lists (frequent adjournments)."""
        filtered = self.history
        if court_name:
            filtered = [cl for cl in filtered if cl.get("court_name") == court_name]

        case_appearances: Dict[str, List[str]] = defaultdict(list)
        for cl in filtered:
            cl_date = cl.get("date", "")
            for entry in cl.get("entries", []):
                cn = entry.get("case_number", "")
                if cn:
                    case_appearances[cn].append(cl_date)  # type: ignore[misc]

        # Cases appearing 3+ times are likely being repeatedly adjourned
        repeat_cases = []
        for case_number, dates in case_appearances.items():
            if len(dates) >= 3:
                sorted_dates = sorted(dates)
                repeat_cases.append({
                    "case_number": case_number,
                    "appearances": len(dates),
                    "first_seen": sorted_dates[0],
                    "last_seen": sorted_dates[-1],
                    "dates": sorted_dates,
                })

        return sorted(repeat_cases, key=lambda x: -x["appearances"])

    def court_efficiency_score(self, court_name: str) -> Dict:
        """Calculate court efficiency metrics."""
        filtered = [cl for cl in self.history if cl.get("court_name") == court_name]

        if not filtered:
            return {"error": "No data for this court"}

        # Total entries scheduled
        total_scheduled = sum(len(cl.get("entries", [])) for cl in filtered)
        total_days = len(set(cl.get("date", "") for cl in filtered))

        # Repeat appearances indicate inefficiency
        repeat_cases = self.find_repeat_adjournments(court_name)
        repeat_count = sum(c["appearances"] for c in repeat_cases)

        # Efficiency: fewer repeat adjournments = more efficient
        if total_scheduled > 0:
            adjournment_rate = repeat_count / total_scheduled
            efficiency = max(0, round(float((1 - adjournment_rate) * 100), 1))  # type: ignore[call-overload]
        else:
            efficiency = 0

        return {
            "court": court_name,
            "efficiency_score": efficiency,
            "total_days_analyzed": total_days,
            "total_cases_listed": total_scheduled,
            "repeat_adjournment_count": len(repeat_cases),
            "avg_daily_load": round(float(total_scheduled / max(total_days, 1)), 1),  # type: ignore[call-overload]
        }

    def generate_report(self, court_name: Optional[str] = None) -> Dict:
        """Generate a comprehensive analysis report."""
        return {
            "volume_trends": self.analyze_volume_trends(court_name),
            "anomalies": self.detect_anomalies(court_name),
            "case_distribution": self.analyze_case_type_distribution(court_name),
            "judge_workload": self.analyze_judge_workload(court_name),
            "repeat_adjournments": list(self.find_repeat_adjournments(court_name))[:20],  # type: ignore[index]
            "efficiency": self.court_efficiency_score(court_name) if court_name else {},
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
