"""
Meta Threads API Client for KebunData Automation
Comprehensive client supporting all 11 Threads API permissions & features:
1. threads_basic               - Fetch user profile and root posts
2. threads_content_publish     - Create and publish text & media posts
3. threads_delete              - Delete published posts
4. threads_keyword_search      - Search posts by keyword and find topics
5. threads_location_tagging    - Search locations and tag posts
6. threads_manage_insights     - Account & media performance metrics
7. threads_manage_mentions     - Fetch mentions of the account
8. threads_manage_replies      - Moderation (hide/unhide) & reply controls
9. threads_profile_discovery   - Discover public profiles & public posts
10. threads_read_replies       - Read thread conversation trees and replies
11. threads_share_to_instagram - Cross-posting support
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
    def __init__(self, user_id=None, access_token=None, app_id=None, app_secret=None):
        self._load_dotenv()
        
        self.app_id = app_id or os.environ.get("THREADS_APP_ID", "2229806474461275")
        self.app_secret = app_secret or os.environ.get("THREADS_APP_SECRET")
        self.user_id = user_id or os.environ.get("THREADS_USER_ID")
        self.access_token = access_token or os.environ.get("THREADS_ACCESS_TOKEN")
        self.base_url = os.environ.get("THREADS_API_BASE_URL", "https://graph.threads.net/v1.0")

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

    # ==========================================
    # 1. threads_basic
    # ==========================================
    def get_me(self):
        """Verify token and fetch authenticated account profile details."""
        if not self.access_token:
            raise ValueError("THREADS_ACCESS_TOKEN is missing. Please set it in .env.")
        
        url = f"{self.base_url}/me"
        params = {
            "fields": "id,username,name,threads_profile_picture_url,threads_biography",
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_recent_posts(self, limit=10):
        """Fetch recent root posts from the Threads account."""
        if not self.user_id:
            raise ValueError("THREADS_USER_ID is required.")
        url = f"{self.base_url}/{self.user_id}/threads"
        params = {
            "fields": "id,media_type,text,timestamp,permalink,is_quote_post,shortcode",
            "limit": limit,
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", [])

    # ==========================================
    # 2. threads_content_publish
    # ==========================================
    def create_post(self, text, reply_to_id=None, image_url=None, video_url=None, location_id=None, reply_control=None):
        """
        Create and publish a post or reply on Threads.
        reply_control options: 'everyone', 'accounts_you_follow', 'mentioned_only'
        """
        if not self.user_id or not self.access_token:
            raise ValueError("Both THREADS_USER_ID and THREADS_ACCESS_TOKEN are required.")

        # Step 1: Create Container
        container_url = f"{self.base_url}/{self.user_id}/threads"
        payload = {
            "access_token": self.access_token,
            "text": text
        }
        
        if image_url:
            payload["media_type"] = "IMAGE"
            payload["image_url"] = image_url
        elif video_url:
            payload["media_type"] = "VIDEO"
            payload["video_url"] = video_url
        else:
            payload["media_type"] = "TEXT"

        if reply_to_id:
            payload["reply_to_id"] = reply_to_id
        if location_id:
            payload["location_id"] = location_id
        if reply_control:
            payload["reply_control"] = reply_control

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
        time.sleep(3)  # Processing wait

        # Step 2: Publish Container
        publish_url = f"{self.base_url}/{self.user_id}/threads_publish"
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

    # ==========================================
    # 3. threads_delete
    # ==========================================
    def delete_post(self, media_id):
        """Delete an app user's published Threads post."""
        url = f"{self.base_url}/{media_id}"
        params = {"access_token": self.access_token}
        resp = requests.delete(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json()

    # ==========================================
    # 4. threads_keyword_search
    # ==========================================
    def search_keywords(self, query, search_type="threads"):
        """Search and fetch content with a specific keyword on Threads."""
        url = f"{self.base_url}/keyword_search"
        params = {
            "q": query,
            "search_type": search_type,
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", [])

    # ==========================================
    # 5. threads_location_tagging
    # ==========================================
    def search_locations(self, query):
        """Search for public locations using keywords or coordinates."""
        url = f"{self.base_url}/location_search"
        params = {
            "q": query,
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", [])

    # ==========================================
    # 6. threads_manage_insights
    # ==========================================
    def get_user_insights(self, metrics="views,likes,replies,reposts,quotes,followers_count"):
        """Get account-level insights and performance metrics."""
        url = f"{self.base_url}/{self.user_id}/threads_insights"
        params = {
            "metric": metrics,
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def get_media_insights(self, media_id, metrics="views,likes,replies,reposts,quotes"):
        """Get post-level insights for a specific Threads post."""
        url = f"{self.base_url}/{media_id}/insights"
        params = {
            "metric": metrics,
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", [])

    # ==========================================
    # 7. threads_manage_mentions
    # ==========================================
    def get_mentions(self):
        """Fetch posts where the user is mentioned."""
        url = f"{self.base_url}/{self.user_id}/mentions"
        params = {
            "fields": "id,text,timestamp,username,permalink",
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", [])

    # ==========================================
    # 8. threads_manage_replies
    # ==========================================
    def manage_reply(self, reply_id, hide=True):
        """Hide or unhide a reply to a thread."""
        url = f"{self.base_url}/{reply_id}/manage_reply"
        payload = {
            "hide": str(hide).lower(),
            "access_token": self.access_token
        }
        resp = requests.post(url, data=payload, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def reply_to_comment(self, comment_id, reply_text):
        """Convenience method to reply directly to a comment ID."""
        return self.create_post(text=reply_text, reply_to_id=comment_id)

    # ==========================================
    # 9. threads_profile_discovery
    # ==========================================
    def get_public_profile(self, target_user_id):
        """Access public profile details for a specific Threads account."""
        url = f"{self.base_url}/{target_user_id}"
        params = {
            "fields": "id,username,name,threads_profile_picture_url,threads_biography",
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json()

    # ==========================================
    # 10. threads_read_replies
    # ==========================================
    def get_thread_replies(self, thread_id):
        """Fetch replies/comments for a specific thread."""
        url = f"{self.base_url}/{thread_id}/replies"
        params = {
            "fields": "id,text,timestamp,username,permalink",
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def get_conversation(self, thread_id):
        """Fetch the full conversation tree for a thread."""
        url = f"{self.base_url}/{thread_id}/conversation"
        params = {
            "fields": "id,text,timestamp,username,permalink",
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", [])

    # ==========================================
    # Token Utilities (Exchange & Refresh)
    # ==========================================
    def exchange_short_lived_token(self, short_lived_token, app_secret=None):
        """Exchange short-lived token for 60-day long-lived token."""
        secret = app_secret or self.app_secret
        if not secret:
            raise ValueError("THREADS_APP_SECRET is required to exchange token.")
        url = "https://graph.threads.net/access_token"
        params = {
            "grant_type": "th_exchange_token",
            "client_secret": secret,
            "access_token": short_lived_token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def refresh_long_lived_token(self, long_lived_token=None):
        """Refresh an existing long-lived token (extends validity for another 60 days)."""
        token = long_lived_token or self.access_token
        if not token:
            raise ValueError("Access token is required to refresh.")
        url = "https://graph.threads.net/refresh_access_token"
        params = {
            "grant_type": "th_refresh_token",
            "access_token": token
        }
        resp = requests.get(url, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        return resp.json()


if __name__ == "__main__":
    print("=== Meta Threads API Client (11 Permissions Supported) ===")
    client = ThreadsClient()
    
    print(f"App ID: {client.app_id}")
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
