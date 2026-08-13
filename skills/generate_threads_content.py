"""
KebunData Threads Content & Reply Generator (Two-Tier AI Engine)
Uses Gemini API to generate:
1. High-engagement viral root posts (Marketer Agent Persona)
2. Interactive, value-packed comment replies with conversational loop extenders (Farmer + Marketer Agent Personas)
"""

import os
import sys
import json
import random
import requests
import urllib3

# Set stdout/stderr to UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Default Sample Topic Themes for KebunData Threads
TOPIC_THEMES = [
    {
        "category": "Soil & Water Telemetry",
        "focus": "Pokok mati lemas vs kurang air - kenapa sensor moisture penting",
        "key_fact": "Akar pokok cili/rockmelon perlukan oksigen dalam media. Bila kelembapan cecah 100% berterusan >6 jam, akar mula mereput (root rot) sebelum daun tunjuk tanda layu."
    },
    {
        "category": "Fertilizer & EC Waste",
        "focus": "Membazir baja AB sebab bacaan EC lari waktu panas terik",
        "key_fact": "Waktu tengah hari panas terik (12pm-2pm), kadar transpirasi tinggi. Jika siram baja EC pekat, pokok akan 'baja shock' dan daun terbakar. Waktu panas pokok nak air lebih berbanding garam baja."
    },
    {
        "category": "Pest & Disease Early Warning",
        "focus": "Kutu trip dan hama merah - punca daun cili berkedut/keriting",
        "key_fact": "Kutu trip serang pucuk muda sebelum nampak dengan mata kasar. Petani biasa sembur racun bila daun dah kerinting mangkuk, masa tu populasi kutu dah matang."
    },
    {
        "category": "Smart IoT vs Manual Farming",
        "focus": "Banding kos pasang sensor IoT RM200 vs rugi satu musim tuaian RM5,000",
        "key_fact": "Kerosakan pam fertigasi atau paip tersumbat yang lambat dikesan 24 jam boleh bunuh 500 polibeg cili serentak."
    },
    {
        "category": "Cocopeat vs Tanah Campuran",
        "focus": "Bahaya guna cocopeat mentah tak rendam / tak basuh tannin",
        "key_fact": "Cocopeat baru ada kandungan garam dan tannin tinggi. Kalau tak basuh sampai EC < 0.5, anak benih akan terbantut dan daun kuning dari bawah."
    }
]

def load_dotenv():
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

def get_api_key():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        api_key = os.environ.get("OPENROUTER_API_KEY")
    return api_key

def call_gemini(prompt, system_instruction=None, temperature=0.75):
    api_key = get_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please set it in .env.")
    
    # Primary model: gemini-flash-latest / gemini-2.5-flash
    model_name = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 600
        }
    }
    
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
    
    response = requests.post(url, json=payload, verify=False, timeout=30)
    
    # Fallback to gemini-flash-latest / gemini-2.5-pro if needed
    if response.status_code != 200:
        fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
        response = requests.post(fallback_url, json=payload, verify=False, timeout=30)
        
    response.raise_for_status()
    data = response.json()
    return data['candidates'][0]['content']['parts'][0]['text']

def load_agent_soul(agent_name="kebundata-threads"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    soul_path = os.path.join(workspace_dir, "agents", agent_name, "SOUL.md")
    
    if os.path.exists(soul_path):
        with open(soul_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def generate_threads_post(custom_topic=None):
    """
    Generate a high-converting, scroll-stopping Meta Threads post.
    """
    marketer_soul = load_agent_soul("kebundata-threads")
    
    if custom_topic:
        theme_context = f"Topic Focus: {custom_topic}"
    else:
        chosen = random.choice(TOPIC_THEMES)
        theme_context = f"Topic: {chosen['category']}\nProblem/Focus: {chosen['focus']}\nAgronomy Fact: {chosen['key_fact']}"
    
    prompt = f"""
Sila hasilkan 1 post Meta Threads yang tular untuk akaun KebunData.

Gunakan konteks ini:
{theme_context}

Garis panduan posting:
1. HOOK: Baris 1 & 2 mesti curi perhatian (curiosity / counter-intuitive fact).
2. BODY: 2-3 baris santai yang bagi fakta berguna & mudah faham (jangan formal).
3. ENGAGEMENT LOOP: Baris terakhir MESTI satu soalan terbuka yang mesra untuk ajak pembaca komen dan kongsi pengalaman kebun mereka.
4. JANGAN letak hashtag bertimbun-timbun (maksimum 1-2 hashtag santai seperti #KebunData #KebunBandar jika perlu).
5. Outputkan teks post Threads SAHAJA tanpa pengenalan atau tanda petik.
"""
    return call_gemini(prompt, system_instruction=marketer_soul, temperature=0.8)

def generate_threads_reply(original_post_text, user_comment, user_name="Sahabat Kebun"):
    """
    Generate a two-tier reply:
    1. Tier 1 (Farmer Agent): Practical Agronomy solution.
    2. Tier 2 (Marketer Agent): Santai BM delivery + Conversation Loop Extender Question.
    """
    farmer_soul = load_agent_soul("farmer")
    marketer_soul = load_agent_soul("kebundata-threads")
    
    system_prompt = f"""
Anda adalah sistem balasan komen AI dua-peringkat (Agronomist + Community Marketer) untuk akaun Threads KebunData.

PANDUAN JAWAPAN KOMEN THREADS:
1. Nada suara: Santai, mesra, membina ('member kebun'), dalam Bahasa Melayu santai.
2. Kandungan: Berikan jawapan/sebab yang logik & praktikal secara ringkas (1-2 ayat).
3. SYARAT WAJIB (CONVERSATION EXTENDER): Jangan tamatkan balasan dengan noktah semata-mata! Sentiasa tanya soalan susulan balik kepada penanya (cth: tanya jenis pokok, media tanaman, atau waktu siraman) supaya dia membalas semula komen ini.
4. Panjang: Ringkas (2-4 ayat maksimum). Sesuai dibaca di skrin telefon.

Rujukan Jiwa Agen:
{marketer_soul}
"""
    
    prompt = f"""
Post Asal KebunData di Threads:
"{original_post_text}"

Komen daripada @{user_name}:
"{user_comment}"

Sila jana balasan Threads yang mesra, informatif, dan mengandungi soalan susulan untuk mencetuskan multi-turn reply loop.
Outputkan teks balasan sahaja.
"""
    return call_gemini(prompt, system_instruction=system_prompt, temperature=0.7)


if __name__ == "__main__":
    print("==================================================")
    print("🌱 KebunData Threads Two-Tier AI Generator Test")
    print("==================================================")
    
    try:
        print("\n[1] Testing Root Post Generation (Marketer Soul)...")
        post = generate_threads_post()
        print("\n--- GENERATED THREADS POST ---")
        print(post)
        print("------------------------------")
        
        print("\n[2] Testing Simulated Auto-Reply (Farmer + Marketer Souls)...")
        sample_post = "Ramai ingat pokok cili layu sebab kurang air. Sebenarnya bila kami cek sensor kelembapan tanah, 80% mati sebab lemas akar... 🥀"
        sample_comment = "Salam tuan, pokok cili saya daun baru tumbuh tapi tepi dia menggulung ke atas dan keras. Ni sebab terlebih air ke penyakit?"
        
        reply = generate_threads_reply(
            original_post_text=sample_post,
            user_comment=sample_comment,
            user_name="azman_fertigasi"
        )
        print(f"\nUser Comment: \"{sample_comment}\"")
        print("\n--- GENERATED THREADS REPLY ---")
        print(reply)
        print("-------------------------------")
        
    except Exception as e:
        print(f"\n❌ Error during generation test: {e}")
        print("Tip: Make sure GEMINI_API_KEY is configured in your environment or .env file.")
