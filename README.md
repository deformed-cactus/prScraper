# GitHub Pull Request Scraper

This Python script fetches closed pull requests from a specified GitHub repository (even private ones, if you provide the appropriate access token), filters them by a given cutoff date, and prints their titles to the console. Additionally, it categorizes the PR titles into two lists—one for titles containing the keyword **Improvement** and one for titles containing **New Feature**.

## Features

- **Cutoff Date Filtering:** Only processes pull requests closed on or after a user-specified date.
- **Keyword Categorization:** Creates two lists based on whether a PR title contains the keywords `Improvement` or `New Feature` (case-insensitive).
- **Private Repository Support:** If the target repository is private, the script accepts a GitHub Personal Access Token for authentication.
- **Pagination Handling:** Retrieves all pages of results from the GitHub API.

## Prerequisites

- Python 3.6 or later.
- The `requests` library. If not already installed, you can install it via pip:

  ```bash
  pip install requests
