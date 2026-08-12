import os
import sys
import json
import requests
import urllib3

# Disable insecure request warnings (for corporate proxy bypass when testing locally)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Helper function to load .env file manually without external dependencies
def load_dotenv():
    # Look for .env in the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ".env")
    
    # If not found there, try the current working directory
    if not os.path.exists(env_path):
        env_path = os.path.join(os.getcwd(), ".env")
        
    if os.path.exists(env_path):
        print(f"Loading environment variables from: {env_path}")
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                # Strip quotes from value
                value = value.strip().strip("'").strip('"')
                os.environ[key.strip()] = value

def setup_paths():
    # Detect operating system
    if os.name == "nt":  # Windows
        print("Detected OS: Windows")
        google_drive_hub = r"G:\My Drive\AI\0_Etiqa_Solution_Automation_Hub"
        output_folder = r"C:\Users\NX505883\Documents\Project\agentic-ai-workspace\workflows\generated-content"
    else:  # Linux (OCI Server)
        print("Detected OS: Linux (OCI Server)")
        google_drive_hub = r"/home/ubuntu/0_Etiqa_Solution_Automation_Hub"
        output_folder = r"/home/ubuntu/generated-content"
        
    brand_voice_path = os.path.join(google_drive_hub, "[01] Product Rules & Documents", "Brand_Voice_Guide.txt")
    product_folder = os.path.join(google_drive_hub, "[01] Product Rules & Documents")
    
    return brand_voice_path, product_folder, output_folder

# Try to import pypdf to read PDF files
try:
    import pypdf
except ImportError:
    print("Error: 'pypdf' library is required to read PDFs.")
    print("Please run: pip install pypdf")
    sys.exit(1)

def get_gemini_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables or .env file.")
        print("Please create a file named '.env' in the same folder as this script and add:")
        print("GEMINI_API_KEY=your_actual_api_key_here")
        sys.exit(1)
    return api_key

def extract_text_from_pdf(pdf_path):
    print(f"Reading PDF: {os.path.basename(pdf_path)}...")
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        # Read first 15 pages to keep context size reasonable and fast
        max_pages = min(15, len(reader.pages))
        for i in range(max_pages):
            text += reader.pages[i].extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Failed to read {pdf_path}: {e}")
        return ""

def call_gemini(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7
        }
    }
    
    try:
        print("Contacting Gemini Pro API...")
        # Use verify=False to prevent SSL errors on local laptop corporate proxies
        response = requests.post(url, json=payload, verify=False)
        response.raise_for_status()
        res_data = response.json()
        return res_data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)

def main():
    # Load .env file if it exists
    load_dotenv()
    
    api_key = get_gemini_api_key()
    brand_voice_path, product_folder, output_folder = setup_paths()
    
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # 1. Read Brand Voice
    if not os.path.exists(brand_voice_path):
        print(f"Error: Brand Voice Guide not found at {brand_voice_path}")
        sys.exit(1)
    with open(brand_voice_path, "r", encoding="utf-8") as f:
        brand_voice = f.read()
        
    # 2. Find and read PDFs
    if not os.path.exists(product_folder):
        print(f"Error: Product Documents folder not found at {product_folder}")
        sys.exit(1)
        
    pdf_files = [f for f in os.listdir(product_folder) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"No PDF brochures found in {product_folder}")
        sys.exit(1)
        
    pdf_text = ""
    for pdf in pdf_files:
        pdf_path = os.path.join(product_folder, pdf)
        pdf_text += f"=== PRODUCT DOCUMENT: {pdf} ===\n"
        pdf_text += extract_text_from_pdf(pdf_path) + "\n"
        
    # 3. Construct prompt
    prompt = f"""
You are the elite AI Copywriter for etiqasolution.
You write social media content for Ahmad Kamil, a Takaful Agent.

YOUR VOICE AND STYLE GUIDELINES (Strictly follow this):
{brand_voice}

PRODUCT DETAILS:
{pdf_text}

TASK:
Write 3 highly engaging social media posts (suitable for Facebook, LinkedIn, or TikTok script format) in a mix of Malay and English (natural professional Manglish/Malaysian style) based on the product rules above.

Each post must contain:
1. **Hook**: Short, punchy, curiosity-inducing statement (Alex Hormozi style).
2. **Body**: Use financial math or numbers (e.g. comparing RM5/day coffee vs RM5/day medical card coverage, or cost of delayed sign-up). Avoid boring corporate jargon.
3. **Visual Guide**: Prompt description for the green screen or video background.
4. **Call to Action**: Direct users to book a free 10-minute review at cal.com/duap00 or WhatsApp.

Format the output clearly as Markdown.
"""

    # 4. Generate content
    content = call_gemini(prompt, api_key)
    
    # 5. Save output
    output_path = os.path.join(output_folder, "etiqa_posts_batch.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("\n" + "="*40)
    print("SUCCESS!")
    print(f"Generated posts saved to: {output_path}")
    print("="*40)

if __name__ == "__main__":
    main()
