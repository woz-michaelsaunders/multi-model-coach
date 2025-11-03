import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

JIRA_API_KEY = os.getenv("JIRA_API_KEY")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")  # e.g. https://yourcompany.atlassian.net
JIRA_EMAIL = os.getenv("JIRA_EMAIL")  # Your JIRA email
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")  # e.g. ABC


def extract_adf_text(adf):
    """Recursively extract plain text from Atlassian Document Format (ADF)"""
    if isinstance(adf, str):
        return adf
    if not isinstance(adf, dict):
        return ""
    text = ""
    if adf.get("type") == "text":
        text += adf.get("text", "")
    if "content" in adf:
        for item in adf["content"]:
            text += extract_adf_text(item)
    return text

def fetch_jira_stories():
    """
    Fetches stories from the JIRA project using the REST API.
    Returns a list of dicts with keys: key, summary, description, status, assignee
    """
    if not all([JIRA_API_KEY, JIRA_BASE_URL, JIRA_EMAIL, JIRA_PROJECT_KEY]):
        raise ValueError("JIRA API credentials or project key missing in .env file.")

    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    jql = f'project={JIRA_PROJECT_KEY} AND issuetype=Story ORDER BY status DESC, updated DESC'
    # Create base64-encoded auth string
    auth_str = f"{JIRA_EMAIL}:{JIRA_API_KEY}"
    b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Accept": "application/json"
    }
    params = {
        "jql": jql,
        "fields": "summary,description,status,assignee,priority,customfield_10016,sprint,created,updated"
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    stories = []
    for issue in data.get("issues", []):
        fields = issue["fields"]
        desc = fields.get("description", "")
        if isinstance(desc, dict):
            desc = extract_adf_text(desc)
            
        # Get sprint information if available
        sprint_field = fields.get("sprint", {})
        sprint_name = sprint_field.get("name", "No Sprint") if sprint_field else "No Sprint"
        
        # Get story points if available (adjust customfield number if needed)
        story_points = fields.get("customfield_10016", "No Points")
        
        stories.append({
            "key": issue["key"],
            "summary": fields.get("summary", ""),
            "description": desc,
            "status": fields.get("status", {}).get("name", "Unknown"),
            "assignee": fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned",
            "priority": fields.get("priority", {}).get("name", "No Priority"),
            "story_points": story_points,
            "sprint": sprint_name,
            "created": fields.get("created", "Unknown"),
            "updated": fields.get("updated", "Unknown")
        })
    return stories
