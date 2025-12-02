#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import re
import sys
import argparse
import os
import time

# I love ai slop vibe coded shit lol
def get_repos(user):
    repos = []
    page = 1
    
    print(f"Fetching repositories for user: {user}")
    
    while True:
        url = f"https://api.github.com/users/{user}/repos?page={page}&per_page=100"
        try:
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"Failed to fetch repos. Status code: {response.status_code}")
                break
                
            data = response.json()
            
            if not data:
                break
            
            for repo in data:
                repos.append(repo["html_url"])
            
            page += 1
            
            # Be nice to GitHub API
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching repositories: {e}")
            break
    
    print(f"Found {len(repos)} repositories for user {user}")
    return repos

def get_commits(repo_url):
    repo_name = repo_url.rstrip('/').split('/')[-2:]
    if len(repo_name) < 2:
        print(f"Invalid repository URL: {repo_url}")
        return []
    
    user, repo = repo_name[0], repo_name[1]
    commits_url = f'https://api.github.com/repos/{user}/{repo}/commits'
    
    print(f"Fetching commits from: {commits_url}")
    
    try:
        response = requests.get(commits_url)
        if response.status_code == 200:
            commits = response.json()
            print(f"Found {len(commits)} commits")
            return [commit['sha'] for commit in commits]
        else:
            print(f"Failed to retrieve commits for {repo_url}. Status code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching commits: {e}")
        return []

def get_emails_from_patch(commit_sha, repo_url):
    patch_url = f"{repo_url}/commit/{commit_sha}.patch"
    
    try:
        response = requests.get(patch_url)
        if response.status_code == 200:
            patch_data = response.text

            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, patch_data)
            
            return set(emails)  # return unique emails
        else:
            print(f"Failed to fetch patch for commit {commit_sha}. Status code: {response.status_code}")
            return set()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching patch for commit {commit_sha}: {e}")
        return set()

def fetch_emails_from_repo(repo_url, max_commits=None):
    print(f"\nFetching emails from repository: {repo_url}")
    
    if not repo_url.startswith('https://github.com/'):
        print("Error: Please provide a valid GitHub repository URL")
        return set()
    
    commits = get_commits(repo_url)
    
    if not commits:
        print("No commits found or failed to fetch commits")
        return set()
    
    if max_commits and max_commits > 0:
        commits = commits[:max_commits]
        print(f"Limiting to {max_commits} commits")
    
    all_emails = set()
    total_commits = len(commits)

    for i, commit_sha in enumerate(commits, 1):
        print(f"Processing commit {i}/{total_commits}: {commit_sha[:8]}...")
        emails = get_emails_from_patch(commit_sha, repo_url)
        all_emails.update(emails)
        
        if i % 10 == 0 or i == total_commits:
            print(f"Progress: {i}/{total_commits} commits processed, {len(all_emails)} unique emails found so far")

    return all_emails

def fetch_emails_from_user(username, max_commits=None):
    print(f"\n{'='*60}")
    print(f"Starting email extraction for GitHub user: {username}")
    print(f"{'='*60}\n")
    
    repos = get_repos(username)
    
    if not repos:
        print(f"No repositories found for user: {username}")
        return set()
    
    all_emails = set()
    total_repos = len(repos)
    
    for i, repo_url in enumerate(repos, 1):
        print(f"\n{'='*60}")
        print(f"Repository {i}/{total_repos}: {repo_url}")
        print(f"{'='*60}")
        
        emails = fetch_emails_from_repo(repo_url, max_commits)
        all_emails.update(emails)
        
        print(f"\nEmails found in this repo: {len(emails)}")
        print(f"Total unique emails so far: {len(all_emails)}")
        
        # Be nice to GitHub API - add a small delay between repos
        if i < total_repos:
            time.sleep(1)
    
    return all_emails

def save_emails_to_file(emails, filename):
    try:
        with open(filename, 'w') as f:
            for email in sorted(emails):
                f.write(email + '\n')
        print(f"Emails saved to: {filename}")
    except IOError as e:
        print(f"Error saving emails to file: {e}")

def main():
    parser = argparse.ArgumentParser(description='Extract email addresses from GitHub repository commits')
    parser.add_argument('target', nargs='?', help='GitHub repository URL or username (use with --user)')
    parser.add_argument('-u', '--user', action='store_true', help='Treat target as a username and process all their repositories')
    parser.add_argument('-o', '--output', help='Output file to save emails (optional)')
    parser.add_argument('-m', '--max-commits', type=int, help='Maximum number of commits to process per repository (optional)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if not args.target:
        print("GitHub Email Extractor")
        print("Usage: python github_email_extractor.py <repository_url|username> [options]")
        print("\nExamples:")
        print("  # Extract from a single repository")
        print("  python github_email_extractor.py https://github.com/google/googletest")
        print("  python github_email_extractor.py https://github.com/blackrock/aladdinsdk -o emails.txt")
        print("\n  # Extract from all repositories of a user")
        print("  python github_email_extractor.py valvesoftware --user")
        print("  python github_email_extractor.py torvalds --user -m 50 -o emails.txt")
        print("\nOptions:")
        print("  -u, --user            Treat target as username (extract from all their repos)")
        print("  -o, --output FILE     Save emails to file")
        print("  -m, --max-commits N   Limit to N commits per repository")
        print("  -v, --verbose         Enable verbose output")
        sys.exit(1)
    
    target = args.target
    
    if args.verbose:
        if args.user:
            print(f"Mode: User extraction")
            print(f"Username: {target}")
        else:
            print(f"Mode: Single repository")
            print(f"Repository: {target}")
        if args.max_commits:
            print(f"Max commits per repo: {args.max_commits}")
        if args.output:
            print(f"Output file: {args.output}")
    
    if args.user:
        emails = fetch_emails_from_user(target, args.max_commits)
        display_target = f"GitHub user: {target}"
    else:
        emails = fetch_emails_from_repo(target, args.max_commits)
        display_target = f"Repository: {target}"
    
    print(f"\n{'='*60}")
    print(f"Extraction Complete!")
    print(f"{display_target}")
    print(f"Total unique emails found: {len(emails)}")
    print(f"{'='*60}")
    
    if emails:
        print("\nExtracted Emails:")
        for i, email in enumerate(sorted(emails), 1):
            print(f"{i:3d}. {email}")
        
        if args.output:
            save_emails_to_file(emails, args.output)
    else:
        print("No email addresses found.")

if __name__ == "__main__":
    main()
