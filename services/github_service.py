import os
import requests
from dotenv import load_dotenv
from utils.cache import cached

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

BASE_URL = "https://api.github.com"

def get_repo(owner, repo):
    def fetch():
        r = requests.get(f"{BASE_URL}/repos/{owner}/{repo}", headers=headers)
        if r.status_code == 200:
            return r.json()
        return None
    return cached(f"repo:{owner}/{repo}", fetch)

def get_pull_requests(owner, repo):
    def fetch():
        r = requests.get(
            f"{BASE_URL}/repos/{owner}/{repo}/pulls?state=all&per_page=30",
            headers=headers
        )
        if r.status_code == 200:
            return r.json()
        return []
    return cached(f"prs:{owner}/{repo}", fetch)

def get_user_or_org_repos(name):
    def fetch():
        r = requests.get(f"{BASE_URL}/users/{name}/repos?per_page=8", headers=headers)
        if r.status_code == 200:
            return r.json()

        r = requests.get(f"{BASE_URL}/orgs/{name}/repos?per_page=8", headers=headers)
        if r.status_code == 200:
            return r.json()

        return []
    return cached(f"portfolio:{name}", fetch)