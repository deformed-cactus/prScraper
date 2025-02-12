#!/usr/bin/env python3
import os
import argparse
import requests
from datetime import datetime

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
# Hard-code your repository here in the format "owner/repository".
# For example: REPO = "octocat/Hello-World"
REPO = "username/repository"  # <-- Replace with your repository

# -------------------------------------------------------------------
# Argument Parsing
# -------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Scrape closed pull requests from a GitHub repository "
            "that were closed on or after a specified cutoff date."
        )
    )
    parser.add_argument(
        "--cutoff",
        required=True,
        help="Cutoff date in YYYY-MM-DD format. Only PRs closed on or after this date will be processed.",
    )
    parser.add_argument(
        "--token",
        help=(
            "GitHub Personal Access Token. If not provided, the script will look for "
            "the GITHUB_TOKEN environment variable."
        ),
    )
    return parser.parse_args()

# -------------------------------------------------------------------
# Fetch PRs from GitHub (handling pagination)
# -------------------------------------------------------------------
def fetch_closed_pull_requests(repo, token):
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    # GitHub API endpoint for pull requests
    url = f"https://api.github.com/repos/{repo}/pulls"
    params = {
        "state": "closed",
        "per_page": 100,
        # Although you can sort, note that the API’s sorting may not match closed_at strictly.
        # So we process all pages.
    }
    prs = []
    page = 1
    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch pull requests: {response.status_code}\n{response.text}"
            )
        data = response.json()
        if not data:
            break  # no more pages
        prs.extend(data)
        page += 1
    return prs

# -------------------------------------------------------------------
# Filter PRs by cutoff date and categorize by keywords
# -------------------------------------------------------------------
def filter_and_categorize_prs(prs, cutoff_date):
    all_pr_titles = []
    improvements = []
    new_features = []

    for pr in prs:
        closed_at = pr.get("closed_at")
        if not closed_at:
            continue  # skip if there is no close date (should not happen for closed PRs)
        # GitHub returns closed_at in ISO8601 format, e.g., "2021-03-11T14:25:30Z"
        try:
            pr_closed_date = datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            # If date format is unexpected, skip this PR
            continue

        if pr_closed_date < cutoff_date:
            # Skip PRs closed before the cutoff date
            continue

        title = pr.get("title", "").strip()
        all_pr_titles.append(title)

        lower_title = title.lower()
        if "improvement" in lower_title:
            improvements.append(title)
        if "new feature" in lower_title:
            new_features.append(title)

    return all_pr_titles, improvements, new_features

# -------------------------------------------------------------------
# Main function
# -------------------------------------------------------------------
def main():
    args = parse_args()

    # Parse cutoff date
    try:
        cutoff_date = datetime.strptime(args.cutoff, "%Y-%m-%d")
    except ValueError:
        print("Error: cutoff date must be in YYYY-MM-DD format.")
        return

    # Retrieve token: first from command-line, then environment variable
    token = args.token or os.getenv("GITHUB_TOKEN")
    if token is None:
        print("Warning: No GitHub token provided. If the repository is private, please supply a token via --token or the GITHUB_TOKEN environment variable.")

    print(f"Fetching closed pull requests for repository: {REPO}")
    try:
        prs = fetch_closed_pull_requests(REPO, token)
    except Exception as e:
        print(f"Error fetching PRs: {e}")
        return

    all_titles, improvements, new_features = filter_and_categorize_prs(prs, cutoff_date)

    # Output results
    print("\n=== All Closed PR Titles (on/after cutoff date) ===")
    if all_titles:
        for title in all_titles:
            print(f"- {title}")
    else:
        print("No pull requests found after the specified cutoff date.")

    print("\n=== Pull Requests containing 'Improvement' ===")
    if improvements:
        for title in improvements:
            print(f"- {title}")
    else:
        print("No pull requests with 'Improvement' found.")

    print("\n=== Pull Requests containing 'New Feature' ===")
    if new_features:
        for title in new_features:
            print(f"- {title}")
    else:
        print("No pull requests with 'New Feature' found.")

if __name__ == "__main__":
    main()
