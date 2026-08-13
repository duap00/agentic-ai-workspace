# 📱 KebunData Meta Threads Automation: Setup & Operations Guide

Panduan lengkap untuk memasang dan menjalankan sistem **Auto-Post & Two-Tier Auto-Reply** untuk akaun **KebunData Threads** menggunakan **Meta Threads API**, **Google Gemini**, dan **n8n / Python**.

---

## 🏛️ 1. Seni Bina Sistem (Two-Tier Growth Engine)

1. **Auto-Post (The Hook Specialist):**
   - Beroperasi pada waktu puncak trafik Threads (8:00 AM, 12:30 PM, 8:30 PM MYT).
   - Menghasilkan post berimpak tinggi dalam gaya *Santai BM / Manglish* dengan struktur:
     - **Hook** (pecah mitos / data telemetry mengejutkan).
     - **Isi Ringkas** (2-3 poin praktikal).
     - **Engagement Loop** (soalan terbuka untuk mencetuskan komen).
2. **Auto-Reply (The Conversation Multiplier):**
   - Mendengar komen baharu setiap 10 minit.
   - Menggabungkan kepakaran **Farmer Agent** (fakta agronomi tepat) dan **Marketer Agent** (gaya mesra member kebun).
   - **WAJIB menyoal semula pengguna** bagi membina *multi-turn discussion* yang menaikkan ranking algoritma Threads.

---

## 🔑 2. Cara Dapatkan Kredensial Meta Threads API

Meta telah melancarkan **Official Threads API (Graph API v1.0)**. Ikuti langkah ini:

### Langkah 2.1: Cipta App di Meta for Developers
1. Pergi ke portal [Meta for Developers](https://developers.facebook.com/) dan log masuk dengan akaun Facebook/Instagram anda.
2. Klik **My Apps** > **Create App**.
3. Pilih use case **Other** > pilih jenis **Business** (atau **Threads API** jika tersedia terus).
4. Berikan nama App (cth: `KebunData-Growth-Engine`).

### Langkah 2.2: Tambah Produk Threads API
1. Dalam Dashboard App anda, cari produk **Threads** dan klik **Set Up**.
2. Di bawah menu **Roles** > **Roles**, tambah akaun Instagram/Threads KebunData anda sebagai **Tester** atau **Developer**.
3. Log masuk ke akaun Threads KebunData anda dan terima jemputan Tester di bahagian *Settings > Security / Developer permissions*.

### Langkah 2.3: Jana User Access Token & Dapatkan User ID
1. Pergi ke **Threads API > Tools** (atau Graph API Explorer).
2. Pilih App anda dan pastikan kebenaran (*Permissions*) ini ditandakan:
   - `threads_basic`
   - `threads_content_publish`
   - `threads_read_replies`
   - `threads_manage_replies`
3. Klik **Generate Token** dan luluskan akses ke akaun KebunData Threads anda.
4. Tukarkan token pendek tersebut kepada **Long-Lived Access Token** (sah selama 60 hari) melalui endpoint Token Exchange Meta.
5. Buat panggilan pengesahan untuk dapatkan User ID:
   ```bash
   GET https://graph.threads.net/v1.0/me?access_token=YOUR_ACCESS_TOKEN
   ```

---

## ⚙️ 3. Konfigurasi Fail `.env`

Tambahkan pembolehubah berikut ke dalam fail `.env` anda:

```ini
# Google Gemini API (Untuk Marketer & Farmer Agent)
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.5-flash

# Meta Threads API
THREADS_USER_ID=17841400000000000
THREADS_ACCESS_TOKEN=THQWJ...
```

---

## 🧪 4. Menguji Skrip Menggunakan Python CLI

Anda boleh menguji penjanaan teks dan sambungan API terus melalui terminal:

### Uji Penjanaan Teks & Simulasi Komen:
```bash
python skills/generate_threads_content.py
```
*Skrip ini akan menguji prompt Marketer SOUL dan menghasilkan contoh post viral serta contoh balasan komen bercabang.*

### Uji Sambungan Meta Threads API:
```bash
python skills/threads_client.py
```

---

## 🚀 5. Import Blueprint ke n8n (OCI Ubuntu Server)

1. Buka antaramuka **n8n Web Interface** anda di OCI server.
2. Pergi ke **Workflows** > klik **Add Workflow** > menu tiga titik (top right) > **Import from File**.
3. Import 2 blueprint yang telah disediakan:
   - `workflows/kebundata-threads-autopost.json` (Penjadualan Post Automatik).
   - `workflows/kebundata-threads-autoreply.json` (Pendengar & Penjawab Komen Automatik).
4. Pastikan pembolehubah `THREADS_USER_ID`, `THREADS_ACCESS_TOKEN`, dan `GEMINI_API_KEY` telah dimasukkan ke dalam n8n Environment Variables atau disesuaikan pada node HTTP Request.
5. Tukarkan status workflow kepada **Active: True**.

---

## 📈 6. Tips Pertumbuhan Algoritma Threads (Best Practices)

- **Kepantasan Balas (Response Speed):** Balasan yang diberikan dalam masa 15-30 minit pertama selepas komen ditulis mendapat lonjakan keutamaan algoritma Meta.
- **Kedalaman Perbualan (Depth over Volume):** 1 post dengan 10 komen bersarang (*nested conversation*) adalah 5x lebih bernilai daripada 10 post tanpa sebarang komen.
- **Kualiti Nada:** Kekal santai ("Tuan", "Geng kebun", "Korang"), jangan nampak seperti bot automatik generik.
