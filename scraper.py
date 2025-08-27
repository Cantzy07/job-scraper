import requests
import smtplib
from email.mime.text import MIMEText
import os

# GitHub API URL for the repository content
GITHUB_REPO_API_ML = "https://api.github.com/repos/speedyapply/2026-AI-College-Jobs/commits?path=NEW_GRAD_USA.md"
GITHUB_REPO_API_SWE = "https://api.github.com/repos/speedyapply/2026-SWE-College-Jobs/commits?path=NEW_GRAD_USA.md"

# Use a fixed path next to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAST_FILE_ML = os.path.join(BASE_DIR, "ai_ml_last_commit.txt")
LAST_FILE_SWE = os.path.join(BASE_DIR, "swe_last_commit.txt")
CREDS_FILE = os.path.join(BASE_DIR, "credentials.txt")

def load_last_commit(file):
    try:
        with open(file, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_commit(file, commit_hash):
    with open(file, "w") as f:
        f.write(commit_hash)

def check_for_updates(repo_api, last_file):
    try:
        resp = requests.get(repo_api, timeout=15)
    except Exception as e:
        print(f"Request error: {e}")
        return None

    if resp.status_code != 200:
        print(f"GitHub API error: {resp.status_code} | {resp.text[:300]}")
        return None

    commits = resp.json()
    if not isinstance(commits, list) or not commits:
        print("No commits returned for the file.")
        return None

    latest = commits[0]
    latest_sha = latest.get("sha")
    if not latest_sha:
        print("Latest commit SHA missing.")
        return None

    last_sha = load_last_commit(last_file)

    # First run: persist the current SHA so the file always exists
    if last_sha is None:
        save_last_commit(last_file, latest_sha)
        print("Initialized last_commit.txt with current SHA.")
        return None

    if last_sha != latest_sha:
        save_last_commit(last_file, latest_sha)
        commit_msg = latest["commit"]["message"]
        author = latest["commit"]["author"]["name"]
        date = latest["commit"]["author"]["date"]
        commit_url = latest["html_url"]
        return f"New commit by {author} on {date}:\n\n\"{commit_msg}\"\n\nView the change: {commit_url}"

    return None

# Send email notification
def send_email(body):
    sender_email, sender_pw = get_credentials(CREDS_FILE)
    receiver_email = sender_email
    subject = "New Roles Available for AI/ML"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Send email via SMTP (use Gmail, Outlook, etc.)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_pw)  # Use an App Password
        server.sendmail(sender_email, receiver_email, msg.as_string())

def get_credentials(file_path):
    file = open(file_path, "r")
    lines = file.readlines()
    email = ""
    pw = ""

    for line in lines:
        if "email" in line:
            email = line.split("=")[1].strip()

        if "password" in line:
            pw = line.split("=")[1].strip()

    return email, pw

# Main function
if __name__ == "__main__":
    ml_changes = check_for_updates(GITHUB_REPO_API_ML, LAST_FILE_ML)
    swe_changes = check_for_updates(GITHUB_REPO_API_SWE, LAST_FILE_SWE)

    if ml_changes != None:
        send_email(ml_changes)
        print("Email sent for ML/AI repo!")
    elif swe_changes != None:
        send_email(ml_changes)
        print("Email sent for SWE repo!")
    else:
        print("No new updates.")

