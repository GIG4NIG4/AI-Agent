import os
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Mengizinkan akses dari Frontend Vercel

# --- KONFIGURASI API KEY ---
GEMINI_API_KEY = "AIzaSyAz7uw42blbw1cJylBpCLJitK7fouHNrkw"
WEATHER_API_KEY = "37000928d57b357d5014115bec3fa325"

# Inisialisasi Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_weather_context(location):
    """Mengambil data cuaca real-time untuk memperkuat reasoning AI"""
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": location,
        "aqi": "no"
    }
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                "temp": data['current']['temp_c'],
                "humidity": data['current']['humidity'],
                "condition": data['current']['condition']['text'],
                "city": data['location']['name']
            }
    except Exception as e:
        print(f"Weather API Error: {e}")
    return None

@app.route('/analyze', methods=['POST'])
def analyze_onion():
    try:
        # 1. Ambil Input (Default Lokasi: Brebes)
        img_file = request.files.get('image')
        user_location = request.form.get('location', 'Brebes, Central Java')

        if not img_file:
            return jsonify({"error": "Silakan unggah foto daun bawang"}), 400

        # 2. Ambil Konteks Cuaca Lokal
        weather = get_weather_context(user_location)
        weather_str = "Data tidak tersedia"
        if weather:
            weather_str = f"Suhu: {weather['temp']}C, Kelembapan: {weather['humidity']}%, Kondisi: {weather['condition']}"

        # 3. Siapkan Prompt Agentic Reasoning
        prompt = f"""
        Role: Anda adalah AgriMind AI Agent, pakar agronomi bawang merah di {user_location}.
        Konteks Lingkungan Saat Ini: {weather_str}.
        
        Tugas:
        1. Analisis foto daun bawang yang dilampirkan secara visual.
        2. Lakukan 'Reasoning' (penalaran): Hubungkan gejala visual dengan kondisi cuaca saat ini. 
           (Contoh: Jika ada bercak dan kelembapan >80%, risiko jamur sangat tinggi).
        3. Berikan diagnosa dan langkah konkret.

        Anda WAJIB memberikan respons dalam format JSON murni seperti ini:
        {{
            "health_index": (integer 0-100),
            "primary_diagnosis": "Nama penyakit atau kondisi",
            "risk_assessment": "Analisis risiko 48 jam ke depan berdasarkan cuaca lokal",
            "environmental_inference": {{
                "soil_moisture": "Estimasi kelembapan tanah (Basah/Kering/Ideal)",
                "ph_level": "Estimasi pH berdasarkan kondisi visual"
            }},
            "action_plan": [
                "Tindakan segera 1",
                "Tindakan segera 2",
                "Tindakan segera 3"
            ],
            "weather_context": {{
                "location": "{user_location}",
                "temp": "{weather['temp'] if weather else 'N/A'}",
                "humidity": "{weather['humidity'] if weather else 'N/A'}"
            }}
        }}
        """

        # 4. Proses Gambar dan Kirim ke Gemini
        img_data = img_file.read()
        image_part = {
            "mime_type": img_file.content_type,
            "data": img_data
        }

        response = model.generate_content([prompt, image_part])
        
        # Bersihkan response teks jika AI memberikan markdown ```json
        clean_json = response.text.replace('```json', '').replace('```', '').strip()

        return clean_json, 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "AgriMind AI Backend is Running", "default_location": "Brebes"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)