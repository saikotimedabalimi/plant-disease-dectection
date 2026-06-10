import json
import os
import threading
import time

import requests


DEFAULT_LANGUAGE = "en"
TRANSLATION_MODELS = [
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
]

LANGUAGES = [
    {"code": "en", "label": "English", "native_label": "English", "direction": "ltr", "ai_name": "English"},
    {"code": "as", "label": "Assamese", "native_label": "অসমীয়া", "direction": "ltr", "ai_name": "Assamese"},
    {"code": "bn", "label": "Bengali", "native_label": "বাংলা", "direction": "ltr", "ai_name": "Bengali"},
    {"code": "brx", "label": "Bodo", "native_label": "बड़ो", "direction": "ltr", "ai_name": "Bodo"},
    {"code": "doi", "label": "Dogri", "native_label": "डोगरी", "direction": "ltr", "ai_name": "Dogri"},
    {"code": "gu", "label": "Gujarati", "native_label": "ગુજરાતી", "direction": "ltr", "ai_name": "Gujarati"},
    {"code": "hi", "label": "Hindi", "native_label": "हिन्दी", "direction": "ltr", "ai_name": "Hindi"},
    {"code": "kn", "label": "Kannada", "native_label": "ಕನ್ನಡ", "direction": "ltr", "ai_name": "Kannada"},
    {"code": "ks", "label": "Kashmiri", "native_label": "कॉशुर", "direction": "ltr", "ai_name": "Kashmiri in Devanagari script"},
    {"code": "gom", "label": "Konkani", "native_label": "कोंकणी", "direction": "ltr", "ai_name": "Konkani in Devanagari script"},
    {"code": "mai", "label": "Maithili", "native_label": "मैथिली", "direction": "ltr", "ai_name": "Maithili"},
    {"code": "ml", "label": "Malayalam", "native_label": "മലയാളം", "direction": "ltr", "ai_name": "Malayalam"},
    {"code": "mni", "label": "Manipuri", "native_label": "ꯃꯩꯇꯩꯂꯣꯟ", "direction": "ltr", "ai_name": "Manipuri (Meitei)"},
    {"code": "mr", "label": "Marathi", "native_label": "मराठी", "direction": "ltr", "ai_name": "Marathi"},
    {"code": "ne", "label": "Nepali", "native_label": "नेपाली", "direction": "ltr", "ai_name": "Nepali"},
    {"code": "or", "label": "Odia", "native_label": "ଓଡ଼ିଆ", "direction": "ltr", "ai_name": "Odia"},
    {"code": "pa", "label": "Punjabi", "native_label": "ਪੰਜਾਬੀ", "direction": "ltr", "ai_name": "Punjabi (Gurmukhi script)"},
    {"code": "sa", "label": "Sanskrit", "native_label": "संस्कृतम्", "direction": "ltr", "ai_name": "Sanskrit"},
    {"code": "sat", "label": "Santali", "native_label": "ᱥᱟᱱᱛᱟᱲᱤ", "direction": "ltr", "ai_name": "Santali"},
    {"code": "sd", "label": "Sindhi", "native_label": "सिन्धी", "direction": "ltr", "ai_name": "Sindhi in Devanagari script"},
    {"code": "ta", "label": "Tamil", "native_label": "தமிழ்", "direction": "ltr", "ai_name": "Tamil"},
    {"code": "te", "label": "Telugu", "native_label": "తెలుగు", "direction": "ltr", "ai_name": "Telugu"},
    {"code": "ur", "label": "Urdu", "native_label": "اردو", "direction": "rtl", "ai_name": "Urdu"},
]

LANGUAGE_MAP = {language["code"]: language for language in LANGUAGES}

ENGLISH_TRANSLATIONS = {
    "brand.title": "Plant Disease Detection",
    "brand.subtitle": "AI crop health assistant",
    "nav.home": "Home",
    "nav.ai_engine": "AI Engine",
    "nav.supplements": "Supplements",
    "nav.contact": "Contact",
    "nav.analyze_leaf": "Analyze Leaf",
    "nav.language": "Language",
    "footer.eyebrow": "Plant Care Platform",
    "footer.title": "A friendlier interface for faster plant health decisions.",
    "footer.copy": "Upload a leaf image, review likely disease information, and find prevention guidance and supplements in one clean workflow.",
    "footer.navigate": "Navigate",
    "footer.connect": "Connect",
    "footer.created_by": "Created by saikoti&ko",
    "footer.tagline": "Designed to help growers identify issues earlier and act with confidence.",
    "home.page_title": "Plant Disease Detection",
    "home.hero.eyebrow": "Field-ready diagnosis",
    "home.hero.title": "Cleaner plant disease detection with a more modern, responsive experience.",
    "home.hero.copy": "This AI assistant helps you upload a leaf image, review likely disease insights, and move straight into prevention or supplement guidance without digging through cluttered pages.",
    "home.hero.open_engine": "Open AI Engine",
    "home.hero.browse_supplements": "Browse Supplements",
    "home.stats.crop_groups": "crop groups supported",
    "home.stats.upload_flow": "upload flow for diagnosis and guidance",
    "home.stats.mobile_access": "mobile-friendly access across pages",
    "home.visual.analysis": "Leaf image analysis",
    "home.visual.redesign": "Responsive redesign",
    "home.visual.workflow": "Workflow",
    "home.visual.workflow_title": "Upload, diagnose, and act from the same dashboard.",
    "home.visual.workflow_copy": "The refreshed interface makes the app feel lighter, more trustworthy, and easier to use on laptops, tablets, and phones.",
    "home.visual.metric_experience": "Experience",
    "home.visual.metric_experience_value": "Clear sections with warmer agricultural colors",
    "home.visual.metric_result_flow": "Result flow",
    "home.visual.metric_result_flow_value": "Diagnosis, prevention, and product guidance",
    "home.visual.metric_audience": "Audience",
    "home.visual.metric_audience_value": "Growers, students, greenhouses, and home gardens",
    "home.visual.metric_use_case": "Use case",
    "home.visual.metric_use_case_value": "Quickly triage plant stress from a leaf photo",
    "home.why.eyebrow": "Why it feels better",
    "home.why.title": "A sharper interface around the same core AI engine.",
    "home.why.copy": "The new layout focuses attention on the upload action, improves readability, and gives every screen a shared design language.",
    "home.feature1.kicker": "Focused",
    "home.feature1.title": "Guided upload journey",
    "home.feature1.copy": "Key actions are now grouped into a stronger hero and a cleaner analysis panel so users know exactly where to start.",
    "home.feature2.kicker": "Readable",
    "home.feature2.title": "Better hierarchy and spacing",
    "home.feature2.copy": "Sections, cards, and call-to-action buttons now have stronger visual contrast, richer color, and more breathing room.",
    "home.feature3.kicker": "Responsive",
    "home.feature3.title": "Works across screen sizes",
    "home.feature3.copy": "The desktop-only warning has been replaced with a layout that adapts cleanly to mobile and tablet screens.",
    "home.crops.eyebrow": "Supported plants",
    "home.crops.title": "Crop categories included in the detector.",
    "home.crops.copy": "The model currently covers a broad mix of fruits and vegetables, giving users one place to test common disease cases.",
    "home.crop.apple.name": "Apple",
    "home.crop.apple.desc": "Scab, rust, black rot, and healthy leaf patterns.",
    "home.crop.blueberry.name": "Blueberry",
    "home.crop.blueberry.desc": "Healthy foliage reference for fast comparison.",
    "home.crop.cherry.name": "Cherry",
    "home.crop.cherry.desc": "Powdery mildew and healthy canopy guidance.",
    "home.crop.corn.name": "Corn",
    "home.crop.corn.desc": "Rust, leaf blight, and cercospora detection support.",
    "home.crop.grape.name": "Grape",
    "home.crop.grape.desc": "Black rot, esca, blight, and healthy vine checks.",
    "home.crop.orange.name": "Orange",
    "home.crop.orange.desc": "Helps identify citrus greening symptoms earlier.",
    "home.crop.peach.name": "Peach",
    "home.crop.peach.desc": "Bacterial spot and healthy leaf references.",
    "home.crop.pepper_bell.name": "Pepper Bell",
    "home.crop.pepper_bell.desc": "Spot disease recognition for pepper plants.",
    "home.crop.potato.name": "Potato",
    "home.crop.potato.desc": "Early and late blight analysis from leaf photos.",
    "home.crop.raspberry.name": "Raspberry",
    "home.crop.raspberry.desc": "Healthy leaf validation for quick confidence checks.",
    "home.crop.soybean.name": "Soybean",
    "home.crop.soybean.desc": "Healthy soybean foliage classification support.",
    "home.crop.squash.name": "Squash",
    "home.crop.squash.desc": "Powdery mildew symptom recognition for squash leaves.",
    "home.crop.strawberry.name": "Strawberry",
    "home.crop.strawberry.desc": "Leaf scorch and healthy canopy detection.",
    "home.crop.tomato.name": "Tomato",
    "home.crop.tomato.desc": "Broad tomato disease coverage across common categories.",
    "home.process.eyebrow": "How it works",
    "home.process.title": "A simple three-step flow for growers and students.",
    "home.process.copy": "The experience is designed to move from image upload to action with as little friction as possible.",
    "home.process.step1": "Upload a leaf image",
    "home.process.step1_copy": "Use a local photo or your device camera to send the clearest leaf sample you have.",
    "home.process.step2": "Review the diagnosis",
    "home.process.step2_copy": "The model predicts the most likely class and presents it in a clearer results layout.",
    "home.process.step3": "Take the next step",
    "home.process.step3_copy": "Read prevention guidance or move into the supplement page to continue treatment research.",
    "index.page_title": "AI Engine",
    "index.hero.eyebrow": "AI Engine",
    "index.hero.title": "Analyze a plant leaf photo in a cleaner, more guided workspace.",
    "index.hero.copy": "Upload an image from your device or capture one live, then let the model return likely disease information, prevention guidance, and related supplements.",
    "index.hero.pill_upload": "Upload image",
    "index.hero.pill_camera": "Capture from camera",
    "index.hero.pill_review": "Review treatment steps",
    "index.context.kicker": "Context",
    "index.context.title": "Why early plant disease detection matters",
    "index.context.copy": "Catching symptoms earlier helps reduce crop loss, improves treatment timing, and avoids wasted effort on the wrong intervention. A quick image-based screening tool is useful when you need a fast first pass.",
    "index.context.item1": "Supports rapid triage before symptoms spread further through the crop.",
    "index.context.item2": "Helps students and growers compare visible leaf patterns with known disease classes.",
    "index.context.item3": "Brings diagnosis, prevention, and product suggestions into one interface.",
    "index.upload.kicker": "Upload",
    "index.upload.title": "Start your analysis",
    "index.upload.copy": "Choose a clear leaf image or capture one directly from your camera feed.",
    "index.upload.choose_image": "Choose image",
    "index.upload.open_camera": "Open camera",
    "index.upload.no_file": "No file chosen yet.",
    "index.upload.capture": "Capture photo",
    "index.upload.close_camera": "Close camera",
    "index.upload.note": "Use a well-lit image with the leaf centered in frame for the most reliable classification.",
    "index.upload.submit": "Submit analysis",
    "index.prevent.kicker": "Prevention",
    "index.prevent.title": "Keep plants stronger before disease spreads",
    "index.prevent.copy": "Prevention is still the most cost-effective strategy. Use the model as a signal, then combine it with strong growing practices and closer inspection.",
    "index.prevent.item1": "Inspect leaves regularly and isolate suspicious plants quickly.",
    "index.prevent.item2": "Maintain airflow and avoid leaving foliage wet for long periods.",
    "index.prevent.item3": "Remove infected material and sanitize tools after handling it.",
    "index.prevent.item4": "Rotate crops and keep soil fertility balanced over time.",
    "index.prevent.item5": "Use the supplement page to continue research after diagnosis.",
    "index.prevent.read_more": "Read more prevention tips",
    "index.alt.preview": "Selected preview image",
    "index.js.camera_unavailable": "Camera access is not available in this browser. Please upload an image instead.",
    "index.js.camera_live": "Camera is live. Capture a photo when the leaf is in focus.",
    "index.js.camera_error": "Unable to access the camera. Please upload an image from your device.",
    "index.js.camera_closed_no_file": "Camera closed. No file chosen yet.",
    "submit.hero.eyebrow": "Diagnosis result",
    "submit.hero.copy_healthy": "The model identified a healthy plant class. Review the notes below to keep the plant vigorous and maintain strong growing conditions.",
    "submit.hero.copy_unhealthy": "The model found a likely disease match. Use the summary, prevention steps, and supplement section below as your next reference point.",
    "submit.status.healthy": "It is a healthy leaf",
    "submit.status.warning": "Needs attention",
    "submit.alt.uploaded_image": "Uploaded leaf image",
    "submit.meta.upload": "Your upload",
    "submit.meta.confidence": "{confidence}% confidence",
    "submit.cta.analyze_another": "Analyze another leaf",
    "submit.overview.kicker": "Overview",
    "submit.overview.title_healthy": "Healthy plant notes",
    "submit.overview.title_unhealthy": "Disease summary",
    "submit.top_matches": "Top model matches",
    "submit.next_steps.kicker": "Next steps",
    "submit.next_steps.title_healthy": "Keep growth conditions strong",
    "submit.next_steps.title_unhealthy": "Prevent further disease spread",
    "submit.supplement.kicker_healthy": "Fertilizer",
    "submit.supplement.kicker_unhealthy": "Supplement",
    "submit.supplement.copy_healthy": "A fertilizer option linked to this healthy class for ongoing care and plant vigor.",
    "submit.supplement.copy_unhealthy": "A product reference linked with this diagnosis so you can continue treatment research.",
    "submit.supplement.buy": "Buy product",
    "submit.chat.ask_ai": "Ask AI",
    "submit.chat.assistant": "AI Assistant",
    "submit.chat.initial_message": "Hello! I see your plant was diagnosed as {diagnosis}. Do you have any questions about treating this or keeping your plant healthy?",
    "submit.chat.placeholder": "Ask a question...",
    "submit.chat.typing": "AI is typing...",
    "submit.chat.error_prefix": "Error:",
    "submit.chat.connection_error": "Error connecting to the chat server.",
    "market.page_title": "Supplement Market",
    "market.hero.eyebrow": "Supplement library",
    "market.hero.title": "Browse fertilizers and supplements in a more polished catalog view.",
    "market.hero.copy": "Each card connects a predicted plant condition with a related product so users can keep researching after diagnosis.",
    "market.status.fertilizer": "Fertilizer",
    "market.status.supplement": "Supplement",
    "market.card.copy_healthy": "Product reference for maintaining plant vigor and supporting a healthy crop after classification.",
    "market.card.copy_unhealthy": "Product reference for users who want to continue treatment planning after a disease prediction.",
    "market.cta.buy": "Buy product",
    "contact.page_title": "Contact Us",
    "contact.hero.eyebrow": "Contact",
    "contact.hero.title": "Send feedback with just your email and message.",
    "contact.hero.copy": "Share suggestions, report issues, or tell us what would make the project more useful for you.",
    "contact.form.kicker": "Feedback form",
    "contact.form.title": "We would love to hear from you",
    "contact.form.copy": "Enter your email address and your feedback message below. The message will be saved directly by the app.",
    "contact.form.email_label": "Email address",
    "contact.form.email_placeholder": "you@example.com",
    "contact.form.feedback_label": "Feedback message",
    "contact.form.feedback_placeholder": "Share your idea, issue, or suggestion here...",
    "contact.form.submit": "Send feedback",
    "contact.message.success": "Thanks for the feedback. Your message has been saved.",
    "contact.message.error_missing": "Please enter both your email address and feedback message.",
    "mobile.page_title": "Plant Disease Detection",
    "mobile.hero.eyebrow": "Responsive view",
    "mobile.hero.title": "This experience now supports mobile screens too.",
    "mobile.hero.copy": "The site has been refreshed to work across phones, tablets, and desktops. You can continue directly to the analysis engine from here.",
    "mobile.hero.open_engine": "Open AI Engine",
    "mobile.hero.back_home": "Back to home",
    "error.api_key_missing_title": "API Key Missing",
    "error.api_key_missing_desc": "Please add your OpenRouter API Key to app.py.",
    "error.api_key_missing_prevent": "Get a free key from OpenRouter and set the OPENROUTER_API_KEY variable in app.py.",
    "error.api_key_missing_warning": "OpenRouter API key is required to use the universal plant model.",
    "error.analysis_title": "Analysis Error",
    "error.analysis_desc": "The AI encountered an error processing the image: {error}",
    "error.analysis_prevent": "Try uploading a clearer image, check your API key, or try selecting a different free model from the MODEL_LIST in app.py.",
    "error.analysis_warning": "There was an issue communicating with OpenRouter or parsing its response.",
    "error.upload_choose": "Please choose a plant leaf image before submitting.",
    "error.upload_extension": "Please upload a JPG, JPEG, PNG, or WEBP image.",
    "error.analyze_image": "Error analyzing image with AI. Please check your API key or try again.",
    "error.chat_api_missing": "API key is missing.",
    "error.chat_models_busy": "All AI models are currently busy or unavailable. Please try again later.",
}


def _build_cache_path(base_dir):
    return os.path.join(base_dir, "translation_cache.json")


def _load_cache(cache_path):
    if not os.path.exists(cache_path):
        return {}

    try:
        with open(cache_path, "r", encoding="utf-8") as cache_file:
            return json.load(cache_file)
    except (json.JSONDecodeError, OSError):
        return {}


class TranslationService:
    def __init__(self, base_dir, openrouter_api_key):
        self.base_dir = base_dir
        self.openrouter_api_key = openrouter_api_key
        self.cache_path = _build_cache_path(base_dir)
        self.lock = threading.Lock()
        self.cache = _load_cache(self.cache_path)

    def get_language(self, code):
        return LANGUAGE_MAP.get(code, LANGUAGE_MAP[DEFAULT_LANGUAGE])

    def get_language_code(self, code):
        return self.get_language(code)["code"]

    def get_cached_catalog(self, language_code):
        language_code = self.get_language_code(language_code)
        if language_code == DEFAULT_LANGUAGE:
            return ENGLISH_TRANSLATIONS
        return self.cache.get(language_code)

    def get_text(self, language_code, key, **params):
        catalog = self.get_cached_catalog(language_code) or ENGLISH_TRANSLATIONS
        text = catalog.get(key) or ENGLISH_TRANSLATIONS.get(key) or key
        try:
            return text.format(**params)
        except (KeyError, ValueError):
            return text

    def get_or_create_catalog(self, language_code):
        language = self.get_language(language_code)
        if language["code"] == DEFAULT_LANGUAGE:
            return ENGLISH_TRANSLATIONS

        cached_catalog = self.get_cached_catalog(language["code"])
        if cached_catalog:
            return cached_catalog

        translated_catalog = self._translate_catalog(language)
        with self.lock:
            self.cache[language["code"]] = translated_catalog
            self._save_cache()
        return translated_catalog

    def _save_cache(self):
        with open(self.cache_path, "w", encoding="utf-8") as cache_file:
            json.dump(self.cache, cache_file, ensure_ascii=False, indent=2)

    def _translate_catalog(self, language):
        if not self.openrouter_api_key or self.openrouter_api_key == "YOUR_OPENROUTER_KEY_HERE":
            raise RuntimeError("OpenRouter API key is missing.")

        source_json = json.dumps(ENGLISH_TRANSLATIONS, ensure_ascii=False, separators=(",", ":"))
        prompt = (
            f"Translate the values in this JSON object into {language['ai_name']} for a plant disease detection website. "
            "Keep every key exactly the same. Preserve placeholders like {diagnosis}, {confidence}, and {error} exactly as written. "
            "Return only valid raw JSON with translated values. Keep product, disease, plant, and scientific names in English when there is no widely used local equivalent. "
            f"JSON: {source_json}"
        )

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Plant Disease Detection Translation",
            "Content-Type": "application/json",
        }

        last_error = None
        for attempt in range(6):
            model_name = TRANSLATION_MODELS[attempt % len(TRANSLATION_MODELS)]
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a precise software localization engine that returns raw JSON only."},
                    {"role": "user", "content": prompt},
                ],
            }
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=180,
                )

                if response.status_code == 429:
                    raise RuntimeError("Translation model is temporarily rate-limited.")

                response.raise_for_status()
                response_data = response.json()
                translated_text = response_data["choices"][0]["message"]["content"]
                if translated_text is None:
                    raise RuntimeError("Translation response was empty.")

                translated_text = translated_text.strip()
                if translated_text.startswith("```json"):
                    translated_text = translated_text[7:]
                elif translated_text.startswith("```"):
                    translated_text = translated_text[3:]
                if translated_text.endswith("```"):
                    translated_text = translated_text[:-3]

                translated_catalog = json.loads(translated_text.strip())
                if set(translated_catalog.keys()) != set(ENGLISH_TRANSLATIONS.keys()):
                    raise RuntimeError("Translated catalog keys do not match the English catalog.")
                return translated_catalog
            except Exception as exc:
                last_error = exc
                time.sleep(8 + (attempt * 6))

        raise RuntimeError(f"Unable to generate translations for {language['label']}: {last_error}")


def build_language_instruction(language):
    return (
        f"Respond in {language['ai_name']}. "
        "Keep plant names, disease names, scientific terms, and product names in English when that is clearer for the user."
    )
