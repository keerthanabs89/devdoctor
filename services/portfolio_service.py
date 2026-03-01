from services.analytics_service import repo_health, risk_index

def analyze_portfolio(repo_data):
    results = []
    risk_counts = {"Critical":0,"Moderate":0,"Low":0}
    health_values = []

    for repo in repo_data:
        health = repo_health(repo["prs"])
        risk = risk_index(repo["prs"])
        risk_counts[risk] += 1
        health_values.append(health)

        results.append({
            "name": repo["name"],
            "description": repo["description"],
            "stars": repo["stars"],
            "health": health,
            "risk": risk
        })

    avg_health = round(sum(health_values)/len(health_values),2) if health_values else 0
    return results, avg_health, risk_counts