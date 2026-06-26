# FarmSense

An intelligent agricultural recommendation system powered by machine learning. Helps farmers optimize crop selection based on weather, soil properties, and environmental factors.

## Features

- Smart crop prediction using ML models
- Real-time weather data integration
- AI-powered agricultural assistant
- Prediction history tracking
- PDF report generation

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd farmsense
   ```

2. Create virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables (.env file)
   ```
   FLASK_ENV=development
   FLASK_SECRET_KEY=your-secret-key
   ```

5. Run the application
   ```bash
   python app.py
   ```
  http://127.0.0.1:5000
  
## Project Structure

```
farmsense/
├── app.py                 
├── model.py             
├── predict.py            
├── assistant.py        
├── weather.py            
├── requirements.txt      
├── data/crops.csv        
└── static/templates/     
```

## Main Modules

- **app.py**: Flask routes and API endpoints
- **model.py**: Machine learning model training and inference
- **predict.py**: Crop prediction logic
- **assistant.py**: AI chatbot for agricultural advice
- **weather.py**: Weather data fetching and processing

## Dependencies

Flask, pandas, numpy, scikit-learn, plotly, reportlab, requests, python-dotenv

See `requirements.txt` for full list with versions.

## Usage

1. Enter soil parameters and location
2. Get AI-powered crop recommendations
3. View prediction confidence and details
4. Download PDF report if needed
