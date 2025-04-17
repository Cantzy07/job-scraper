import requests
import smtplib
from email.mime.text import MIMEText

# GitHub API URL for the repository content
GITHUB_REPO_API = "https://api.github.com/repos/Cantzy07/job-scraper/commits"

# Load previous commit hash
def load_last_commit():
    try:
        with open("last_commit.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

# Save latest commit hash
def save_last_commit(commit_hash):
    with open("last_commit.txt", "w") as f:
        f.write(commit_hash)

# check for updates
def check_for_updates():
    response = requests.get(GITHUB_REPO_API)

    if response.status_code == 200:
        commits = response.json()
        latest_commit = commits[0]
        latest_sha = latest_commit['sha']
        last_commit = load_last_commit()

        if last_commit != latest_sha:
            save_last_commit(latest_sha)

            commit_msg = latest_commit['commit']['message']
            author = latest_commit['commit']['author']['name']
            date = latest_commit['commit']['author']['date']
            commit_url = latest_commit['html_url']  # Link to the commit

            # Return a summary of the change
            return f"New commit by {author} on {date}:\n\n\"{commit_msg}\"\n\nView the change: {commit_url}"

    return None  # No changes

# Send email notification
def send_email(body):
    sender_email, sender_pw = get_credentials("credentials.txt")
    receiver_email = sender_email
    subject = "New Roles Available"

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
    changes = check_for_updates()
    if changes != None:
        send_email(changes)
        print("Email sent!")
    else:
        print("No new updates.")

