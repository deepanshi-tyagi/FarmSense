from flask import Flask, render_template, request, send_file, session
from predict import predict_crop
import requests
import json
import csv
import os
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


app = Flask(__name__)
app.secret_key = "farmsense_secret_key"

API_KEY = "af1e04d1b97ba06f14aaa5d742cf3f82"
HISTORY_FILE = "prediction_history.csv"


CROP_DETAILS = {
    "rice": {"season": "Kharif", "soil": "Clayey soil", "water": "High", "tip": "Needs high rainfall and humid climate."},
    "maize": {"season": "Kharif", "soil": "Loamy soil", "water": "Moderate", "tip": "Avoid waterlogging."},
    "chickpea": {"season": "Rabi", "soil": "Sandy loam", "water": "Low", "tip": "Good for dry regions."},
    "kidneybeans": {"season": "Kharif", "soil": "Loamy soil", "water": "Moderate", "tip": "Requires cool climate."},
    "pigeonpeas": {"season": "Kharif", "soil": "Loamy soil", "water": "Low", "tip": "Tolerates drought."},
    "mothbeans": {"season": "Kharif", "soil": "Sandy soil", "water": "Low", "tip": "Best for arid areas."},
    "mungbean": {"season": "Kharif", "soil": "Loamy soil", "water": "Moderate", "tip": "Short duration crop."},
    "blackgram": {"season": "Kharif", "soil": "Clay loam", "water": "Moderate", "tip": "Avoid excess irrigation."},
    "lentil": {"season": "Rabi", "soil": "Loamy soil", "water": "Low", "tip": "Best in cool climate."},
    "pomegranate": {"season": "All season", "soil": "Sandy loam", "water": "Low", "tip": "Drought tolerant fruit crop."},
    "banana": {"season": "All season", "soil": "Loamy soil", "water": "High", "tip": "Needs warm humid climate."},
    "mango": {"season": "Summer", "soil": "Alluvial soil", "water": "Moderate", "tip": "Avoid frost areas."},
    "grapes": {"season": "Winter", "soil": "Sandy loam", "water": "Moderate", "tip": "Needs sunlight and pruning."},
    "watermelon": {"season": "Summer", "soil": "Sandy loam", "water": "High", "tip": "Needs warm climate."},
    "muskmelon": {"season": "Summer", "soil": "Sandy loam", "water": "Moderate", "tip": "Avoid excess moisture."},
    "apple": {"season": "Winter", "soil": "Loamy soil", "water": "Moderate", "tip": "Needs cool climate."},
    "orange": {"season": "Winter", "soil": "Sandy loam", "water": "Moderate", "tip": "Needs subtropical climate."},
    "papaya": {"season": "All season", "soil": "Loamy soil", "water": "Moderate", "tip": "Sensitive to waterlogging."},
    "coconut": {"season": "All season", "soil": "Sandy soil", "water": "High", "tip": "Best for coastal areas."},
    "cotton": {"season": "Kharif", "soil": "Black soil", "water": "Moderate", "tip": "Needs warm climate."},
    "jute": {"season": "Kharif", "soil": "Alluvial soil", "water": "High", "tip": "Needs warm humid climate."},
    "coffee": {"season": "Winter", "soil": "Loamy soil", "water": "Moderate", "tip": "Needs shade and humidity."}
}

CROP_MARKET_INFO = {
    "rice": {"price": "₹2200 - ₹2800/quintal", "demand": "High"},
    "maize": {"price": "₹1800 - ₹2400/quintal", "demand": "High"},
    "chickpea": {"price": "₹5000 - ₹7000/quintal", "demand": "High"},
    "kidneybeans": {"price": "₹8000 - ₹12000/quintal", "demand": "Medium"},
    "pigeonpeas": {"price": "₹7000 - ₹9500/quintal", "demand": "High"},
    "mothbeans": {"price": "₹6000 - ₹8500/quintal", "demand": "Medium"},
    "mungbean": {"price": "₹7000 - ₹9500/quintal", "demand": "High"},
    "blackgram": {"price": "₹7000 - ₹10000/quintal", "demand": "High"},
    "lentil": {"price": "₹5500 - ₹7500/quintal", "demand": "Medium"},
    "pomegranate": {"price": "₹4000 - ₹9000/quintal", "demand": "High"},
    "banana": {"price": "₹1200 - ₹2500/quintal", "demand": "Medium"},
    "mango": {"price": "₹3000 - ₹10000/quintal", "demand": "High"},
    "grapes": {"price": "₹4000 - ₹12000/quintal", "demand": "High"},
    "watermelon": {"price": "₹800 - ₹1800/quintal", "demand": "Seasonal"},
    "muskmelon": {"price": "₹1200 - ₹2500/quintal", "demand": "Seasonal"},
    "apple": {"price": "₹6000 - ₹15000/quintal", "demand": "High"},
    "orange": {"price": "₹2500 - ₹6000/quintal", "demand": "High"},
    "papaya": {"price": "₹1500 - ₹3500/quintal", "demand": "Medium"},
    "coconut": {"price": "₹2500 - ₹4000/quintal", "demand": "High"},
    "cotton": {"price": "₹6000 - ₹7500/quintal", "demand": "High"},
    "jute": {"price": "₹4000 - ₹5500/quintal", "demand": "Medium"},
    "coffee": {"price": "₹15000 - ₹25000/quintal", "demand": "High"}
}


def load_metrics():
    try:
        if os.path.exists("metrics.json") and os.path.getsize("metrics.json") > 0:
            with open("metrics.json", "r") as file:
                return json.load(file)
    except Exception:
        return None

    return None


def get_model_chart_data():
    metrics = load_metrics()
    model_names = []
    model_f1_scores = []

    if metrics and "all_models" in metrics:
        for model_name, values in metrics["all_models"].items():
            model_names.append(model_name)
            model_f1_scores.append(values["f1_score"])

    return model_names, model_f1_scores


def load_history():
    try:
        if not os.path.exists(HISTORY_FILE):
            return []

        if os.path.getsize(HISTORY_FILE) == 0:
            return []

        df = pd.read_csv(HISTORY_FILE)

        if df.empty:
            return []

        return df.tail(5).to_dict(orient="records")

    except Exception:
        return []


def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city.strip(),
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    if response.status_code != 200:
        raise Exception(data.get("message", "Weather API error"))

    return {
        "city": city,
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"]
    }


def get_fertilizer_recommendation(N, P, K):
    advice = []

    if N < 50:
        advice.append("Nitrogen is low. Use urea, compost, or nitrogen-rich fertilizer.")
    elif N > 100:
        advice.append("Nitrogen is high. Avoid extra nitrogen fertilizer.")
    else:
        advice.append("Nitrogen level is suitable.")

    if P < 40:
        advice.append("Phosphorus is low. Use DAP or bone meal.")
    elif P > 80:
        advice.append("Phosphorus is high. Avoid extra phosphate fertilizer.")
    else:
        advice.append("Phosphorus level is suitable.")

    if K < 40:
        advice.append("Potassium is low. Use MOP or potash fertilizer.")
    elif K > 80:
        advice.append("Potassium is high. Avoid extra potassium fertilizer.")
    else:
        advice.append("Potassium level is suitable.")

    return advice


def attach_crop_details(predictions):
    final_predictions = []

    for item in predictions:
        crop_name = item["crop"].lower()

        details = CROP_DETAILS.get(crop_name, {
            "season": "Not available",
            "soil": "Not available",
            "water": "Not available",
            "tip": "Details will be added soon."
        })

        market = CROP_MARKET_INFO.get(crop_name, {
            "price": "Market data not available",
            "demand": "Not available"
        })

        item["details"] = details
        item["market"] = market

        final_predictions.append(item)

    return final_predictions


def filter_predictions(predictions, selected_soil, selected_season, irrigation):
    filtered = []

    for item in predictions:
        crop_name = item["crop"].lower()
        details = CROP_DETAILS.get(crop_name, {})

        crop_soil = details.get("soil", "").lower()
        crop_season = details.get("season", "").lower()
        crop_water = details.get("water", "").lower()

        bonus = 0

        if selected_soil.lower() in crop_soil:
            bonus += 8

        if selected_season.lower() in crop_season or crop_season == "all season":
            bonus += 8

        if irrigation == "yes" and crop_water in ["moderate", "high"]:
            bonus += 5

        if irrigation == "no" and crop_water == "low":
            bonus += 5

        item["confidence"] = min(100, round(item["confidence"] + bonus, 2))
        filtered.append(item)

    filtered = sorted(filtered, key=lambda x: x["confidence"], reverse=True)
    return filtered[:3]


def generate_explanation(predictions, soil_type, season, irrigation, weather):
    top_crop = predictions[0]["crop"]

    return (
        f"{top_crop} is recommended because its growing requirements match the selected "
        f"soil type, season, irrigation availability, temperature "
        f"({weather['temperature']}°C), humidity ({weather['humidity']}%), and rainfall conditions."
    )


def save_prediction_history(city, N, P, K, ph, rainfall, weather, predictions, soil_type, season, irrigation):
    file_exists = os.path.exists(HISTORY_FILE)

    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists or os.path.getsize(HISTORY_FILE) == 0:
            writer.writerow([
                "timestamp",
                "city",
                "N",
                "P",
                "K",
                "temperature",
                "humidity",
                "ph",
                "rainfall",
                "soil_type",
                "season",
                "irrigation",
                "top_crop",
                "confidence"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            city,
            N,
            P,
            K,
            weather["temperature"],
            weather["humidity"],
            ph,
            rainfall,
            soil_type,
            season,
            irrigation,
            predictions[0]["crop"],
            predictions[0]["confidence"]
        ])


@app.route("/")
def home():
    model_names, model_f1_scores = get_model_chart_data()

    return render_template(
        "index.html",
        metrics=load_metrics(),
        history=load_history(),
        model_names=model_names,
        model_f1_scores=model_f1_scores
    )


@app.route("/predict", methods=["POST"])
def predict():
    try:
        city = request.form["city"]

        N = float(request.form["N"])
        P = float(request.form["P"])
        K = float(request.form["K"])
        ph = float(request.form["ph"])
        rainfall = float(request.form["rainfall"])

        soil_type = request.form["soil_type"]
        season = request.form["season"]
        irrigation = request.form["irrigation"]

        if ph < 0 or ph > 14:
            raise Exception("pH value must be between 0 and 14.")

        if N < 0 or P < 0 or K < 0 or rainfall < 0:
            raise Exception("N, P, K and rainfall cannot be negative.")

        weather = get_weather(city)

        input_data = [
            N,
            P,
            K,
            weather["temperature"],
            weather["humidity"],
            ph,
            rainfall
        ]

        predictions = predict_crop(input_data)
        predictions = attach_crop_details(predictions)
        predictions = filter_predictions(predictions, soil_type, season, irrigation)

        fertilizer_advice = get_fertilizer_recommendation(N, P, K)

        explanation = generate_explanation(
            predictions,
            soil_type,
            season,
            irrigation,
            weather
        )

        save_prediction_history(
            city,
            N,
            P,
            K,
            ph,
            rainfall,
            weather,
            predictions,
            soil_type,
            season,
            irrigation
        )

        session["report_data"] = {
            "city": city,
            "weather": weather,
            "inputs": {
                "Nitrogen": N,
                "Phosphorus": P,
                "Potassium": K,
                "pH": ph,
                "Rainfall": rainfall,
                "Soil Type": soil_type,
                "Season": season,
                "Irrigation": irrigation
            },
            "predictions": predictions,
            "fertilizer_advice": fertilizer_advice,
            "metrics": load_metrics()
        }

        model_names, model_f1_scores = get_model_chart_data()

        return render_template(
            "index.html",
            prediction=predictions,
            weather=weather,
            metrics=load_metrics(),
            history=load_history(),
            explanation=explanation,
            soil_type=soil_type,
            season=season,
            irrigation=irrigation,
            fertilizer_advice=fertilizer_advice,
            model_names=model_names,
            model_f1_scores=model_f1_scores
        )

    except Exception as e:
        model_names, model_f1_scores = get_model_chart_data()

        return render_template(
            "index.html",
            error=str(e),
            metrics=load_metrics(),
            history=load_history(),
            model_names=model_names,
            model_f1_scores=model_f1_scores
        )


@app.route("/download-report")
def download_report():
    report_data = session.get("report_data")

    if not report_data:
        return "No report available. Please make a prediction first."

    file_path = "FarmSense_Professional_Report.pdf"

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        textColor=colors.HexColor("#1f7a3f"),
        fontSize=22,
        spaceAfter=16
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#1f7a3f"),
        fontSize=14,
        spaceBefore=12,
        spaceAfter=8
    )

    normal_style = styles["Normal"]

    story = []

    story.append(Paragraph("FarmSense AI - Crop Recommendation Report", title_style))
    story.append(Paragraph("AI-powered crop recommendation using soil data, weather data, and machine learning.", normal_style))
    story.append(Spacer(1, 0.2 * inch))

    weather = report_data["weather"]
    inputs = report_data["inputs"]
    predictions = report_data["predictions"]
    fertilizer_advice = report_data["fertilizer_advice"]
    metrics = report_data["metrics"]

    story.append(Paragraph("Weather Information", heading_style))

    weather_table = Table([
        ["City", report_data["city"]],
        ["Temperature", f"{weather['temperature']} °C"],
        ["Humidity", f"{weather['humidity']} %"],
        ["Condition", weather["condition"]],
        ["Wind Speed", f"{weather['wind_speed']} m/s"]
    ], colWidths=[160, 320])

    weather_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#dff3e3")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(weather_table)

    story.append(Paragraph("Input Values", heading_style))

    input_rows = [["Parameter", "Value"]]
    for key, value in inputs.items():
        input_rows.append([key, value])

    input_table = Table(input_rows, colWidths=[160, 320])
    input_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f7a3f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(input_table)

    story.append(Paragraph("Top 3 Crop Recommendations", heading_style))

    crop_rows = [["Rank", "Crop", "Confidence"]]
    for i, crop in enumerate(predictions, start=1):
        crop_rows.append([str(i), crop["crop"], f"{crop['confidence']}%"])

    crop_table = Table(crop_rows, colWidths=[60, 220, 200])
    crop_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f7a3f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(crop_table)

    story.append(Paragraph("Fertilizer Recommendation", heading_style))

    for advice in fertilizer_advice:
        story.append(Paragraph(f"- {advice}", normal_style))
        story.append(Spacer(1, 4))

    if metrics:
        story.append(Paragraph("Model Performance", heading_style))

        model_table = Table([
            ["Best Model", metrics["best_model"]],
            ["Best F1 Score", f"{metrics['best_f1_score']}%"]
        ], colWidths=[160, 320])

        model_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#dff3e3")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))

        story.append(model_table)

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Generated by FarmSense AI", normal_style))

    doc.build(story)

    return send_file(file_path, as_attachment=True)


@app.route("/admin")
def admin_dashboard():
    try:
        if not os.path.exists(HISTORY_FILE) or os.path.getsize(HISTORY_FILE) == 0:
            return render_template(
                "admin.html",
                total_predictions=0,
                most_predicted_crop="No data",
                recent_predictions=[],
                city_usage=[],
                crop_chart_labels=[],
                crop_chart_values=[],
                city_chart_labels=[],
                city_chart_values=[],
                trend_chart_labels=[],
                trend_chart_values=[]
            )

        df = pd.read_csv(HISTORY_FILE)

        if df.empty:
            return render_template(
                "admin.html",
                total_predictions=0,
                most_predicted_crop="No data",
                recent_predictions=[],
                city_usage=[],
                crop_chart_labels=[],
                crop_chart_values=[],
                city_chart_labels=[],
                city_chart_values=[],
                trend_chart_labels=[],
                trend_chart_values=[]
            )

        df["city"] = df["city"].astype(str).str.strip()
        df["top_crop"] = df["top_crop"].astype(str).str.strip()

        total_predictions = len(df)
        most_predicted_crop = df["top_crop"].value_counts().idxmax()
        recent_predictions = df.tail(10).to_dict(orient="records")

        city_usage = (
            df.groupby("city")
            .size()
            .reset_index(name="count")
            .sort_values(by="count", ascending=False)
            .to_dict(orient="records")
        )

        crop_distribution = df["top_crop"].value_counts()
        crop_chart_labels = crop_distribution.index.tolist()
        crop_chart_values = crop_distribution.values.tolist()

        city_distribution = df["city"].value_counts()
        city_chart_labels = city_distribution.index.tolist()
        city_chart_values = city_distribution.values.tolist()

        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        trend_data = df.groupby("date").size()

        trend_chart_labels = [str(date) for date in trend_data.index.tolist()]
        trend_chart_values = trend_data.values.tolist()

        return render_template(
            "admin.html",
            total_predictions=total_predictions,
            most_predicted_crop=most_predicted_crop,
            recent_predictions=recent_predictions,
            city_usage=city_usage,
            crop_chart_labels=crop_chart_labels,
            crop_chart_values=crop_chart_values,
            city_chart_labels=city_chart_labels,
            city_chart_values=city_chart_values,
            trend_chart_labels=trend_chart_labels,
            trend_chart_values=trend_chart_values
        )

    except Exception as e:
        return f"Admin Dashboard Error: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)