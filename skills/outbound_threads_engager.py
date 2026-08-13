"""
KebunData Threads Outbound Niche Hunter & Auto-Engager
Finds relevant community gardening / farming posts on Meta Threads and leaves helpful, value-first comments to drive organic profile visits and followers.
"""

import os
import sys
import json
import time
import random
import argparse
import requests
import urllib3

# Ensure local skills folder is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from threads_client import ThreadsClient
from generate_threads_content import call_gemini, load_agent_soul

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# High-intent farming & gardening keywords
NICHE_KEYWORDS = [
    "pokok cili",
    "daun kuning",
    "fertigasi",
    "kebun bandar",
    "baja AB",
    "hidroponik",
    "akar reput",
    "serangan kutu trip",
    "cocopeat tanaman",
    "tanaman pasu",
    "pokok layu",
    "sembur racun organik"
]

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "engaged_threads.json")

def load_engaged_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_engaged_cache(cache_list):
    # Keep last 500 records
    if len(cache_list) > 500:
        cache_list = cache_list[-500:]
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_list, f, indent=2)

def evaluate_and_generate_outbound_reply(post_text, username="Geng Kebun", keyword=""):
    """
    Evaluates if the post is genuinely about plants/gardening, and crafts a high-value, friendly comment.
    """
    farmer_soul = load_agent_soul("farmer")
    marketer_soul = load_agent_soul("kebundata-threads")
    
    system_prompt = f"""
Anda ialah Ahmad Kamil / KebunData (Gabungan Agronomist Pakar + Sahabat Kebun Mesra) di Meta Threads.

TUGASAN:
1. Analisa teks post orang lain. Jika post ini TIDAK relevan dengan perbualan tanaman / pokok / pertanian / baja / perkebunan (cth: spam, politik, berita artis, atau rungutan tiada kaitan), jawab SAHAJA: SKIP
2. Jika RELEVAN, hasilkan SATU balasan komen bernilai tinggi:
   - NADA: Santai, jujur, mesra macam kawan borak di kebun ('member kebun'). Bahasa Melayu santai.
   - NILAI: Berikan 1 tip agronomi logik yang bantu selesaikan atau terangkan masalah yang dia alami.
   - DILARANG SAMA SEKALI: Jangan menjual produk, jangan letak link, jangan ajak follow/beli ('Sila DM saya' dilarang), tiada perkataan bot/formal.
   - CONVERSATION EXTENDER: Di hujung ayat, tanya SATU soalan santai (cth: jenis media, waktu siraman, atau usia pokok) supaya dia seronok nak balas balik.
   - PANJANG: 2 hingga 3 ayat sahaja.

Rujukan Karakter:
{farmer_soul}
{marketer_soul}
"""
    
    prompt = f"""
Post Pengguna di Threads:
"{post_text}"
(Daripada: @{username} | Keyword: {keyword})

Sila analisa dan berikan respon (atau balas 'SKIP'):
"""
    reply = call_gemini(prompt, system_instruction=system_prompt, temperature=0.75)
    return reply.strip()

def run_outbound_hunter(dry_run=True, max_replies=1, custom_keyword=None):
    print("==========================================================")
    print(f"🌱 KebunData Outbound Niche Hunter ({'DRY-RUN (Simulasi)' if dry_run else '🚀 LIVE POSTING'})")
    print("==========================================================")
    
    client = ThreadsClient()
    if not client.access_token:
        print("❌ Error: THREADS_ACCESS_TOKEN is missing in .env.")
        return

    engaged_cache = load_engaged_cache()
    keyword = custom_keyword or random.choice(NICHE_KEYWORDS)
    print(f"🔍 Searching Threads for keyword: '{keyword}'...")

    try:
        posts = client.search_keywords(keyword)
    except Exception as e:
        print(f"⚠️ Search error or endpoint limitation: {e}")
        # Fallback simulation if keyword search returns 0 or needs specific permissions
        posts = []

    if not posts:
        print(f"ℹ️ No new search results returned for '{keyword}'.")
        print("💡 Simulating evaluation against a sample community question:")
        posts = [
            {
                "id": f"sim_post_{int(time.time())}",
                "text": "Kenapa pokok cili saya kat balkoni daun bawah semua jadi kuning dan gugur ya? Padahal hari2 siram pagi petang... help me geng kebun 😭",
                "username": "gardening_malaysia_fan"
            }
        ]

    replies_count = 0
    for post in posts:
        post_id = post.get("id")
        post_text = post.get("text", "")
        username = post.get("username", "Geng Kebun")

        if post_id in engaged_cache:
            continue
        if len(post_text.strip()) < 15:
            continue
        if "kebundata" in username.lower() or "ak.kamil" in username.lower():
            continue

        print(f"\n--- Found Candidate Post by @{username} (ID: {post_id}) ---")
        print(f"Post Text: \"{post_text}\"")

        reply_content = evaluate_and_generate_outbound_reply(post_text, username=username, keyword=keyword)
        
        if reply_content.upper() == "SKIP":
            print("⏩ AI Evaluator decided to SKIP this post (not relevant).")
            continue

        print(f"\n💬 Generated Expert Reply:\n\"{reply_content}\"")

        if dry_run:
            print("🛡️ [DRY RUN]: No actual comment posted. (Use --publish to send live comment)")
            engaged_cache.append(post_id)
            replies_count += 1
        else:
            jitter = random.randint(30, 90)
            print(f"⏳ Applying Human Anti-Bot Jitter: waiting {jitter}s...")
            time.sleep(jitter)
            
            try:
                pub_result = client.reply_to_comment(comment_id=post_id, reply_text=reply_content)
                print(f"✅ Successfully posted outbound comment! Reply ID: {pub_result.get('id')}")
                engaged_cache.append(post_id)
                replies_count += 1
            except Exception as pe:
                print(f"❌ Failed to publish comment: {pe}")

        if replies_count >= max_replies:
            break

    save_engaged_cache(engaged_cache)
    print(f"\n✨ Completed! Processed {replies_count} outbound post(s).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KebunData Threads Outbound Niche Hunter")
    parser.add_argument("--publish", action="store_true", help="Publish comments live to Threads (default is dry-run)")
    parser.add_argument("--keyword", type=str, default=None, help="Specific search keyword")
    parser.add_argument("--max", type=int, default=1, help="Max replies per run")
    
    args = parser.parse_args()
    run_outbound_hunter(dry_run=(not args.publish), max_replies=args.max, custom_keyword=args.keyword)
