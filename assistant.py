"""Small, deterministic agricultural assistant that works without internet access."""

import re


CROPS = {
    "rice": ("Kharif", "clayey or alluvial soil", "high", "Keep the field moist and avoid moisture stress during flowering."),
    "maize": ("Kharif", "well-drained loamy soil", "moderate", "Avoid waterlogging and provide nitrogen in split doses."),
    "chickpea": ("Rabi", "sandy-loam soil", "low", "It prefers cool, dry weather and light irrigation."),
    "kidney beans": ("Kharif", "well-drained loamy soil", "moderate", "Use good drainage and avoid very hot conditions."),
    "pigeon peas": ("Kharif", "loamy soil", "low", "This drought-tolerant pulse still needs drainage."),
    "moth beans": ("Kharif", "sandy soil", "low", "A useful option for hot, arid regions."),
    "mung bean": ("Kharif or summer", "well-drained loamy soil", "moderate", "Avoid standing water; it is a short-duration pulse."),
    "black gram": ("Kharif", "clay-loam soil", "moderate", "Avoid excessive irrigation and waterlogging."),
    "lentil": ("Rabi", "loamy soil", "low", "It grows best in cool weather with limited irrigation."),
    "pomegranate": ("year-round", "sandy-loam soil", "low", "Use drip irrigation and avoid prolonged wet soil."),
    "banana": ("year-round", "fertile loamy soil", "high", "Maintain regular moisture and protect plants from strong wind."),
    "mango": ("summer", "deep, well-drained loamy soil", "moderate", "Avoid frost and waterlogging around the roots."),
    "grapes": ("winter", "well-drained sandy-loam soil", "moderate", "Good sunlight, pruning, and drainage are important."),
    "watermelon": ("summer", "sandy-loam soil", "moderate", "Water consistently during fruit set, then reduce near harvest."),
    "muskmelon": ("summer", "sandy-loam soil", "moderate", "Warm weather and excellent drainage give the best results."),
    "apple": ("winter", "well-drained loamy soil", "moderate", "It needs a cool climate and suitable chilling hours."),
    "orange": ("winter", "well-drained sandy-loam soil", "moderate", "Keep moisture even but never leave roots waterlogged."),
    "papaya": ("year-round", "well-drained loamy soil", "moderate", "It is highly sensitive to waterlogging and frost."),
    "coconut": ("year-round", "sandy or coastal soil", "high", "Regular water is important, especially for young palms."),
    "cotton": ("Kharif", "deep black soil", "moderate", "Warm weather and good drainage are essential."),
    "jute": ("Kharif", "fertile alluvial soil", "high", "Warm, humid weather and abundant water suit this crop."),
    "coffee": ("winter", "rich, well-drained loamy soil", "moderate", "Provide shade, moisture, and good organic matter."),
}

ALIASES = {
    "kidneybeans": "kidney beans", "rajma": "kidney beans",
    "pigeonpeas": "pigeon peas", "arhar": "pigeon peas", "tur": "pigeon peas",
    "mothbeans": "moth beans", "mungbean": "mung bean", "moong": "mung bean",
    "blackgram": "black gram", "urad": "black gram", "lentils": "lentil",
}

SOILS = {
    "loamy": "Loamy soil balances drainage and nutrient retention. It suits maize, pulses, many fruits, and vegetables.",
    "sandy": "Sandy soil drains quickly. Add compost to improve water holding; melons, coconut, and drought-tolerant pulses can suit it.",
    "clay": "Clay soil stores water and nutrients but can compact. Improve drainage and add organic matter; rice often suits wetter clay soil.",
    "black": "Black soil holds moisture and is naturally suited to cotton. Avoid over-irrigation and compaction.",
    "alluvial": "Alluvial soil is generally fertile and productive. Rice, jute, maize, vegetables, and many fruits can grow well with suitable water.",
}


def _crop_in(message):
    normalized = re.sub(r"[^a-z0-9 ]", " ", message.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    for alias, crop in ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", normalized):
            return crop
    for crop in sorted(CROPS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(crop)}\b", normalized):
            return crop
    return None


def _crop_answer(crop):
    season, soil, water, tip = CROPS[crop]
    return (
        f"{crop.title()} is mainly a {season} crop. It prefers {soil} and has "
        f"{water} water needs. Tip: {tip}"
    )


def answer_question(message):
    text = " ".join(message.strip().lower().split())
    if not text:
        return "Please ask me a question about a crop, soil, season, irrigation, fertilizer, or pH."

    crop = _crop_in(text)
    if crop:
        return _crop_answer(crop)

    if any(word in text for word in ("hello", "hi", "hey", "namaste")):
        return "Namaste! I am the offline FarmSense Assistant. Ask me about crops, soil, seasons, irrigation, fertilizer, or pH."

    for soil, guidance in SOILS.items():
        if re.search(rf"\b{soil}(?: soil)?\b", text):
            return guidance + " A soil test is the best way to confirm nutrients and pH."

    if "kharif" in text:
        return "Common Kharif options include rice, maize, cotton, jute, pigeon pea, mung bean, and black gram. Final choice depends on soil, rainfall, and irrigation."
    if "rabi" in text:
        return "Common Rabi options include chickpea, lentil, wheat, and mustard. FarmSense currently predicts chickpea and lentil from this group."
    if "summer" in text:
        return "Warm-season options include watermelon, muskmelon, mango, papaya, and mung bean where irrigation is available."

    if any(word in text for word in ("fertilizer", "fertiliser", "urea", "dap", "npk", "nitrogen", "phosphorus", "potassium")):
        return "Choose fertilizer from a soil test: nitrogen supports leafy growth, phosphorus supports roots and flowering, and potassium supports strength and stress tolerance. Avoid fixed doses without local soil-test and crop-stage guidance."

    if any(word in text for word in ("irrigation", "water", "watering")):
        return "Irrigate according to crop stage, soil, and weather. Sandy soil needs smaller, more frequent watering; clay soil needs slower, less frequent watering. Morning irrigation and drip systems reduce waste."

    if "ph" in text or "acidic" in text or "alkaline" in text:
        return "Soil pH controls nutrient availability. Many crops prefer about 6.0-7.5, but the ideal range varies by crop. Test the soil before adding lime or other amendments."

    if any(phrase in text for phrase in ("best crop", "which crop", "recommend crop", "suitable crop")):
        return "Use the FarmSense prediction form for a personalized crop result. Enter your city, N, P, K, pH, rainfall, soil type, season, and irrigation availability."

    if any(word in text for word in ("help", "what can you", "topics")):
        return "I can explain supported crops, soil types, Kharif/Rabi seasons, irrigation, fertilizer nutrients, and soil pH. Try: 'Tell me about rice' or 'Which crops suit black soil?'"

    return "I do not have a reliable offline answer for that yet. Try asking about a named crop, soil type, Kharif/Rabi season, irrigation, fertilizer, or pH."
