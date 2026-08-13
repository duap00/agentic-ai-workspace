"""
Meta Threads API Client for KebunData Automation
Supports:
- Verifying Threads API credentials
- Creating and publishing text posts (Root Threads)
- Fetching latest user threads and comments/replies
- Replying to specific comments/threads (Auto-Reply)
"""

import os
import sys
import json
import time
import requests
import urllib3

# Set stdout/stderr to UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Disable insecure request warnings (useful when behind proxies)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ThreadsClient:
    BASE_URL = "https://graph.threads.net/v1.0"

    def __init__(self, user_id=None, access_token=None):
        self.user_id = user_id or os.environ.get("THREADS_USER_ID")
        self.access_token = access_token or os.environ.get("THREADS_ACCESS_TOKEN")
        
        if not self.access_token:
            self._load_dotenv()
            self.user_id = self.user_id or os.environ.get("THREADS_USER_ID")
            self.access_token = self.access_token or os.environ.get("THREADS_ACCESS_TOKEN")

    def _load_dotenv(self):
        """Helper to load .env file from script directory or workspace root."""
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
            os.path.join(os.getcwd(), ".env"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        ]
        for env_path in possible_paths:
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip("'").strip('"'))
                break

    def get_me(self):
        """Verify token and fetch account profile details."""
        if not self.access_token:
            raise ValueError("THREADS_ACCESS_TOKEN is missing. Please set it in .env.")
        
        url = f"{self.BASE_URL}/me"
        params = {
            "fields": "id,username,name,threads_profile_picture_url,threads_biography",
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def create_post(self, text, reply_to_id=None, image_url=None):
        """
        Create and publish a post or reply on Threads.
        Step 1: Create media container
        Step 2: Wait 2-3 seconds for container processing
        Step 3: Publish container
        """
        if not self.user_id or not self.access_token:
            raise ValueError("Both THREADS_USER_ID and THREADS_ACCESS_TOKEN are required.")

        # Step 1: Create Container
        container_url = f"{self.BASE_URL}/{self.user_id}/threads"
        payload = {
            "access_token": self.access_token,
            "text": text
        }
        
        if image_url:
            payload["media_type"] = "IMAGE"
            payload["image_url"] = image_url
        else:
            payload["media_type"] = "TEXT"

        if reply_to_id:
            payload["reply_to_id"] = reply_to_id

        print(f"Creating Threads container (Reply: {bool(reply_to_id)})...")
        res_container = requests.post(container_url, data=payload, verify=False, timeout=20)
        
        if res_container.status_code != 200:
            print(f"Failed to create container: {res_container.status_code} - {res_container.text}")
            res_container.raise_for_status()

        container_data = res_container.json()
        creation_id = container_data.get("id")
        if not creation_id:
            raise ValueError(f"No creation_id returned: {container_data}")

        print(f"Container created successfully. ID: {creation_id}")
        # Wait briefly for Meta to process container
        time.sleep(3)

        # Step 2: Publish Container
        publish_url = f"{self.BASE_URL}/{self.user_id}/threads_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }
        
        print("Publishing container to live Threads feed...")
        res_publish = requests.post(publish_url, data=publish_payload, verify=False, timeout=20)
        
        if res_publish.status_code != 200:
            print(f"Failed to publish container: {res_publish.status_code} - {res_publish.text}")
            res_publish.raise_for_status()

        published_data = res_publish.json()
        print(f"✅ Published successfully! Thread ID: {published_data.get('id')}")
        return published_data

    def get_recent_posts(self, limit=10):
        """Fetch recent root posts from KebunData Threads account."""
        url = f"{self.BASE_URL}/{self.user_id}/threads"
        params = {
            "fields": "id,media_type,text,timestamp,permalink,is_quote_post",
            "limit": limit,
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def get_thread_replies(self, thread_id):
        """Fetch replies/comments for a specific thread."""
        url = f"{self.BASE_URL}/{thread_id}/replies"
        params = {
            "fields": "id,text,timestamp,username,permalink",
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def reply_to_comment(self, comment_id, reply_text):
        """Convenience method to reply directly to a comment ID."""
        return self.create_post(text=reply_text, reply_to_id=comment_id)


if __name__ == "__main__":
    print("=== Meta Threads API Client Test CLI ===")
    client = ThreadsClient()
    
    if not client.access_token:
        print("\n⚠️ Note: THREADS_ACCESS_TOKEN is not set yet.")
        print("Please configure THREADS_USER_ID and THREADS_ACCESS_TOKEN in your .env file.")
        print("See docs/kebundata-threads-setup.md for setup instructions.")
        sys.exit(0)

    try:
        profile = client.get_me()
        print(f"✅ Connected to Threads Account: @{profile.get('username')} (ID: {profile.get('id')})")
        print(f"Name: {profile.get('name')}")
    except Exception as e:
        print(f"❌ Error connecting to Threads API: {e}")
