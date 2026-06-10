import csv
import os
from datetime import datetime
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import pandas as pd
from werkzeug.utils import secure_filename
import requests
import base64
import json
import difflib
from localization import (
    DEFAULT_LANGUAGE,
    ENGLISH_TRANSLATIONS,
    LANGUAGES,
    TranslationService,
    build_language_instruction,
)

# ==============================================================================
# WARNING: OPENROUTER API KEY REQUIRED
# ==============================================================================
# Put your free OpenRouter API key here! Get one at: https://openrouter.ai/workspaces/default/keys
OPENROUTER_API_KEY = "your api key"
MODEL_LIST = [
    "google/gemma-4-31b-it:free",
    "google/gemma-3-4b-it:free",          # Fastest - small but vision-capable
    "baidu/qianfan-ocr-fast:free",        # Fastest - optimized for screenshot/OCR
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "google/gemma-4-26b-a4b-it:free",     # Vision + 256K context, efficient MoE (3.8B active)
    "google/gemma-3-27b-it:free",
    "google/gemma-3-12b-it:free",
]

# Pick a fast, free vision model
SELECTED_MODEL = "google/gemma-4-31b-it:free"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
FEEDBACK_FILE = os.path.join(BASE_DIR, 'feedback_messages.csv')
ALLOWED_UPLOAD_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
os.makedirs(UPLOAD_DIR, exist_ok=True)

disease_info = pd.read_csv(os.path.join(BASE_DIR, 'disease_info.csv'), encoding='cp1252')
supplement_info = pd.read_csv(os.path.join(BASE_DIR, 'supplement_info.csv'), encoding='cp1252')

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "plant-disease-language-switcher")
app.config["JSON_AS_ASCII"] = False
translation_service = TranslationService(BASE_DIR, OPENROUTER_API_KEY)


def get_selected_language_code():
    return translation_service.get_language_code(session.get("language", DEFAULT_LANGUAGE))


def get_selected_language():
    return translation_service.get_language(get_selected_language_code())


def ui_text(key, language_code=None, **params):
    return translation_service.get_text(language_code or DEFAULT_LANGUAGE, key, **params)


@app.context_processor
def inject_localization():
    current_language = get_selected_language()

    def translate(key, **params):
        return translation_service.get_text(current_language["code"], key, **params)

    return {
        "current_language": current_language,
        "current_language_code": current_language["code"],
        "language_options": LANGUAGES,
        "english_catalog": ENGLISH_TRANSLATIONS,
        "t": translate,
    }


def encode_image(image_path):
    """Encode image to base64 for OpenRouter API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def prediction(image_path, language_code):
    """Run prediction using OpenRouter Vision API."""
    language = translation_service.get_language(language_code)
    language_instruction = build_language_instruction(language)

    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "YOUR_OPENROUTER_KEY_HERE":
        return {
            "title": ui_text("error.api_key_missing_title", language["code"]),
            "description": ui_text("error.api_key_missing_desc", language["code"]),
            "prevent": ui_text("error.api_key_missing_prevent", language["code"]),
            "is_healthy": False,
            "confidence_percent": 0.0,
            "analysis_warning": ui_text("error.api_key_missing_warning", language["code"]),
        }
        
    try:
        base64_image = encode_image(image_path)
        mime_type = "image/jpeg"
        if image_path.lower().endswith('.png'):
            mime_type = "image/png"
        elif image_path.lower().endswith('.webp'):
            mime_type = "image/webp"

        prompt = f"""
        Analyze this plant leaf image. Identify the exact plant (e.g. Guava, Mango, Tomato) and whether it is healthy or has a disease.
        Write every string value in {language['ai_name']}.
        {language_instruction}
        You MUST return ONLY a valid JSON object (do not use markdown formatting or backticks, just raw JSON text) with the following exact keys:
        {{
            "title": "Plant Name : Disease Name" (or "Plant Name : Healthy" if it is healthy),
            "description": "A short paragraph describing the plant and the disease.",
            "prevent": "A short paragraph on how to prevent or treat it (or how to maintain if healthy).",
            "is_healthy": true or false,
            "supplement_name": "Name of a real-world product, fertilizer, or fungicide to treat this (or maintain it if healthy)."
        }}
        """

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Plant Disease Detection App",
            "Content-Type": "application/json"
        }

        payload_template = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        }

        fallback_models = [
            SELECTED_MODEL,
            "google/gemma-4-26b-a4b-it:free",
            "nvidia/nemotron-nano-12b-v2-vl:free",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
        ]

        response = None
        for model_name in fallback_models:
            payload = payload_template.copy()
            payload["model"] = model_name
            
            try:
                print(f"Trying model: {model_name}...")
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                break # Success!
            except requests.exceptions.HTTPError as e:
                if response is not None and response.status_code in [404, 429, 502, 503]:
                    print(f"Model {model_name} failed with {response.status_code}, trying next...")
                    continue
                else:
                    raise e # Other HTTP errors

        if response is None or response.status_code in [404, 429, 502, 503]:
            raise Exception("All free models are currently offline or rate-limited. Please try again in a few minutes.")
            
        
        response_data = response.json()
        text = response_data['choices'][0]['message']['content'].strip()
        
        # Clean up possible markdown
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
            
        result = json.loads(text)
        result["confidence_percent"] = 99.0
        result["analysis_warning"] = None
        return result
    except Exception as e:
        print(f"OpenRouter Error: {e}")
        try:
            print("Response:", response.text)
        except:
            pass
        return {
            "title": ui_text("error.analysis_title", language["code"]),
            "description": ui_text("error.analysis_desc", language["code"], error=str(e)),
            "prevent": ui_text("error.analysis_prevent", language["code"]),
            "is_healthy": False,
            "confidence_percent": 0.0,
            "analysis_warning": ui_text("error.analysis_warning", language["code"]),
        }

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    submission_message = None
    submission_error = None

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        feedback = request.form.get('feedback', '').strip()
        language_code = get_selected_language_code()

        if not email or not feedback:
            submission_error = ui_text('contact.message.error_missing', language_code)
        else:
            feedback_exists = os.path.exists(FEEDBACK_FILE)

            with open(FEEDBACK_FILE, 'a', newline='', encoding='utf-8') as feedback_file:
                writer = csv.writer(feedback_file)

                if not feedback_exists:
                    writer.writerow(['timestamp', 'email', 'feedback'])

                writer.writerow([datetime.now().isoformat(timespec='seconds'), email, feedback])

            submission_message = ui_text('contact.message.success', language_code)

    return render_template(
        'contact-us.html',
        submission_message=submission_message,
        submission_error=submission_error,
    )

@app.route('/index')
def ai_engine_page():
    return render_template('index.html')

@app.route('/mobile-device')
def mobile_device_detected_page():
    return render_template('mobile-device.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method != 'POST':
        return redirect(url_for('ai_engine_page'))

    language_code = get_selected_language_code()
    image = request.files.get('image')

    if image is None or not image.filename:
        return render_template(
            'index.html',
            upload_error=ui_text('error.upload_choose', language_code),
        )

    original_filename = secure_filename(image.filename)
    extension = os.path.splitext(original_filename)[1].lower()

    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        return render_template(
            'index.html',
            upload_error=ui_text('error.upload_extension', language_code),
        )

    stored_filename = f"leaf-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}{extension}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)
    image.save(file_path)

    prediction_result = prediction(file_path, language_code)
    if not prediction_result:
        return render_template('index.html', upload_error=ui_text('error.analyze_image', language_code))
        
    title = prediction_result.get('title', 'Unknown')
    description = prediction_result.get('description', '')
    prevent = prediction_result.get('prevent', '')
    is_healthy = prediction_result.get('is_healthy', False)
    confidence = prediction_result.get('confidence_percent', 99.0)
    analysis_warning = prediction_result.get('analysis_warning', None)
    uploaded_image_url = url_for('static', filename=f"uploads/{stored_filename}")

    # HYBRID SUPPLEMENT SYSTEM
    # 1. Try to fuzzy-match the AI's title against the original CSV database
    disease_names = list(disease_info['disease_name'])
    matches = difflib.get_close_matches(title, disease_names, n=1, cutoff=0.5)
    
    if matches:
        # Match found! Use the exact CSV data for this disease
        match_idx = disease_names.index(matches[0])
        sname = supplement_info['supplement name'][match_idx]
        simage = supplement_info['supplement image'][match_idx]
        buy_link = supplement_info['buy link'][match_idx]
    else:
        # No match found (e.g. Guava). Use AI's dynamic suggestion!
        sname = prediction_result.get('supplement_name', 'General Plant Fertilizer')
        simage = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Spray_Bottle.svg/200px-Spray_Bottle.svg.png"
        buy_link = f"https://www.amazon.com/s?k={sname.replace(' ', '+')}"

    return render_template(
        'submit.html',
        title=title,
        desc=description,
        prevent=prevent,
        uploaded_image_url=uploaded_image_url,
        pred=-1,
        sname=sname,
        simage=simage,
        buy_link=buy_link,
        confidence_percent=confidence,
        top_matches=[],
        analysis_warning=analysis_warning,
        is_healthy=is_healthy,
    )

@app.route('/market', methods=['GET', 'POST'])
def market():
    return render_template('market.html', supplement_image = list(supplement_info['supplement image']),
                           supplement_name = list(supplement_info['supplement name']), disease = list(disease_info['disease_name']), buy = list(supplement_info['buy link']))

@app.route('/api/language', methods=['POST'])
def set_language():
    data = request.get_json(silent=True) or {}
    language_code = translation_service.get_language_code(data.get("language"))
    session["language"] = language_code
    language = translation_service.get_language(language_code)
    return jsonify({"language": language})


@app.route('/api/translations/<language_code>', methods=['GET'])
def get_translations(language_code):
    language = translation_service.get_language(language_code)

    try:
        catalog = translation_service.get_or_create_catalog(language["code"])
        return jsonify({"language": language, "translations": catalog})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 503


@app.route('/api/chat', methods=['POST'])
def api_chat():
    language = get_selected_language()
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "YOUR_OPENROUTER_KEY_HERE":
        return jsonify({"error": ui_text("error.chat_api_missing", language["code"])}), 400

    data = request.get_json(silent=True) or {}
    messages = data.get('messages', [])
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Plant Disease Chatbot",
        "Content-Type": "application/json"
    }
    
    system_message = {
        "role": "system",
        "content": (
            "You are a friendly, expert AI agriculturist and plant pathologist. "
            "You are chatting with a user who just received a diagnosis for their plant leaf. "
            "Answer their questions clearly, concisely, and with practical advice. "
            f"{build_language_instruction(language)} "
            "Do not output markdown code blocks if possible."
        )
    }
    
    payload_template = {
        "messages": [system_message] + messages
    }
    
    fallback_models = [
        SELECTED_MODEL,
        "google/gemma-4-26b-a4b-it:free",
        "google/gemma-3-12b-it:free",
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
    ]
    
    response = None
    for model_name in fallback_models:
        payload = payload_template.copy()
        payload["model"] = model_name
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            break
        except requests.exceptions.HTTPError as e:
            if response is not None and response.status_code in [404, 429, 502, 503]:
                continue
            else:
                return jsonify({"error": str(e)}), 500

    if response is None or response.status_code in [404, 429, 502, 503]:
        return jsonify({"error": ui_text("error.chat_models_busy", language["code"])}), 503
        
    try:
        result = response.json()
        reply = result['choices'][0]['message']['content'].strip()
        return jsonify({"reply": reply}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
