from datetime import datetime
from collections import Counter
import math

def process_prs(prs):
    processed = []
    for pr in prs:
        created = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        merged_at = pr["merged_at"]

        merge_days = None
        if merged_at:
            merged = datetime.strptime(merged_at, "%Y-%m-%dT%H:%M:%SZ")
            merge_days = (merged - created).days

        processed.append({
            "author": pr["user"]["login"],
            "merged": merged_at is not None,
            "merge_days": merge_days
        })
    return processed


def merge_efficiency(prs):
    merged = [p for p in prs if p["merge_days"] is not None]
    if not merged:
        return 0
    avg = sum(p["merge_days"] for p in merged) / len(merged)
    return round(max(0, 100 - avg * 2.5), 2)


def risk_index(prs):
    open_prs = len([p for p in prs if not p["merged"]])
    if open_prs > 20:
        return "Critical"
    if open_prs > 10:
        return "Moderate"
    return "Low"


def bus_factor(prs):
    counts = Counter([p["author"] for p in prs])
    if not counts:
        return "Unknown"
    total = sum(counts.values())
    top = max(counts.values())
    ratio = top / total

    if ratio > 0.7:
        return "High Dependency"
    elif ratio > 0.4:
        return "Moderate Dependency"
    return "Distributed"


def pr_complexity(prs):
    merged = [p["merge_days"] for p in prs if p["merge_days"] is not None]
    if not merged:
        return 0
    avg = sum(merged) / len(merged)
    variance = sum((x - avg)**2 for x in merged) / len(merged)
    return round(min(100, math.sqrt(variance) * 5), 2)


def burnout_risk(prs):
    counts = Counter([p["author"] for p in prs])
    total = sum(counts.values())
    if total == 0:
        return 0
    dominance = max(counts.values()) / total
    open_prs = len([p for p in prs if not p["merged"]])
    return round(min(100, dominance*60 + open_prs*1.5), 2)


def governance_score(prs):
    return round(
        max(
            0,
            merge_efficiency(prs)
            - pr_complexity(prs)*0.3
            - burnout_risk(prs)*0.2
        ),
        2
    )


def repo_health(prs):
    if not prs:
        return 0
    merged_ratio = len([p for p in prs if p["merged"]]) / len(prs)
    return round(
        (merged_ratio*40)
        + (merge_efficiency(prs)*0.4)
        + ((100-burnout_risk(prs))*0.2),
        2
    )


def recommendation(health, risk):
    if health > 75 and risk == "Low":
        return "Safe to Contribute"
    if health > 50:
        return "Moderate Stability"
    return "High Risk – Caution"


# 🔥 NEW FEATURE 1
def contribution_opportunity(prs):
    total = len(prs)
    if total == 0:
        return "Low Data"

    open_prs = len([p for p in prs if not p["merged"]])
    merge_score = merge_efficiency(prs)
    burnout = burnout_risk(prs)

    openness = open_prs / total

    score = (openness * 40) + ((100 - burnout) * 0.3) + (merge_score * 0.3)

    if score > 70:
        return "🟢 Great for First-Time Contributors"
    elif score > 45:
        return "🟡 Contribute with Caution"
    else:
        return "🔴 Maintainer Overloaded"


# 🔥 NEW FEATURE 2
def ai_insight_summary(meta, prs, health, risk):
    if not prs:
        return "Not enough pull request data to generate insights."

    burnout = burnout_risk(prs)
    efficiency = merge_efficiency(prs)
    bus = bus_factor(prs)

    insight = []

    if efficiency > 70:
        insight.append("The repository demonstrates strong merge efficiency.")
    else:
        insight.append("Merge delays suggest potential review bottlenecks.")

    if burnout > 60:
        insight.append("Burnout indicators show high contributor dependency.")
    else:
        insight.append("Contributor workload appears distributed.")

    if bus == "High Dependency":
        insight.append("High bus factor risk detected.")
    else:
        insight.append("Contribution ownership is relatively distributed.")

    if risk == "Critical":
        insight.append("Open PR accumulation signals governance stress.")

    return " ".join(insight)