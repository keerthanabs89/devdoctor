from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from services.github_service import get_repo, get_pull_requests, get_user_or_org_repos
from services.analytics_service import *
from services.portfolio_service import analyze_portfolio

app = FastAPI(title="DevDoctor")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.get("/repo")
def repo_mode(request: Request, query: str):

    if "/" not in query:
        return templates.TemplateResponse("repo.html", {"request": request, "error": "Use format owner/repo"})

    owner, repo = query.split("/")
    meta = get_repo(owner, repo)

    if not meta:
        return templates.TemplateResponse("repo.html", {"request": request, "error": "Repository not found"})

    prs = process_prs(get_pull_requests(owner, repo))

    health = repo_health(prs)
    risk = risk_index(prs)
    opportunity = contribution_opportunity(prs)
    insight = ai_insight_summary(meta, prs, health, risk)

    return templates.TemplateResponse("repo.html", {
        "request": request,
        "meta": meta,
        "health": health,
        "risk": risk,
        "efficiency": merge_efficiency(prs),
        "complexity": pr_complexity(prs),
        "burnout": burnout_risk(prs),
        "governance": governance_score(prs),
        "bus": bus_factor(prs),
        "recommendation": recommendation(health, risk),
        "opportunity": opportunity,
        "insight": insight
    })


@app.get("/portfolio")
def portfolio_mode(request: Request, name: str):

    repos = get_user_or_org_repos(name)

    if not repos:
        return templates.TemplateResponse("portfolio.html", {"request": request, "error": "User or organization not found"})

    repo_data = []

    for repo in repos:
        prs = process_prs(get_pull_requests(repo["owner"]["login"], repo["name"]))
        repo_data.append({
            "name": repo["name"],
            "description": repo["description"],
            "stars": repo["stargazers_count"],
            "prs": prs
        })

    results, avg_health, risk_counts = analyze_portfolio(repo_data)

    return templates.TemplateResponse("portfolio.html", {
        "request": request,
        "results": results,
        "avg_health": avg_health,
        "risk_counts": risk_counts
    })