# 🌾 AI Agent for Smart Farming Advice

A full-stack web application that gives AI-powered farming advice to farmers based on their crop, soil, season, and location — powered by **Groq LLM (LLaMA 3)** and a **Python Flask** backend.

---

## 📁 Project Structure

```
smart-farming/
├── frontend/
│   ├── index.html      # All pages (SPA-style)
│   ├── style.css       # Green & white agriculture theme
│   └── script.js       # Form handling & API calls
│
├── backend/
│   ├── app.py          # Flask REST API + Groq AI logic
│   └── requirements.txt
│
└── README.md
```

---

## 🚀 Getting Started

### 1. Backend Setup (Python Flask)

```bash
cd smart-farming/backend

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
```

The backend starts at **http://127.0.0.1:5000**

---

### 2. Frontend Setup

Open `smart-farming/frontend/index.html` directly in a browser **or** serve it with a simple HTTP server:

```bash
cd smart-farming/frontend
python -m http.server 8080
```

Then visit **http://localhost:8080**

> Make sure the Flask backend is running before using the form.

---

## 🔌 REST API Reference

### `GET /`
Returns application status.

**Response:**
```json
{ "status": "running", "app": "SmartFarm AI API", "version": "1.0.0" }
```

---

### `POST /advice`
Accepts farmer details and returns AI-generated advice.

**Request body:**
```json
{
  "farmerName": "Ramesh Kumar",
  "location":   "Pune, Maharashtra",
  "crop":       "Tomato",
  "soilType":   "Black",
  "season":     "Summer",
  "question":   "My tomato leaves are turning yellow."
}
```

**Response:**
```json
{
  "success": true,
  "advice":  "Possible Causes:\n- Nitrogen deficiency\n..."
}
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🌱 Crop Advice | Crop-specific recommendations |
| 💧 Irrigation Tips | Water management guidance |
| 🧪 Fertilizer Advice | Soil-type aware nutrient plans |
| 🐛 Pest & Disease | IPM and organic pest control |
| ☁️ Weather Precautions | Season-based crop protection |
| 🌿 Organic Farming | Eco-friendly alternatives |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Bootstrap 5, Vanilla JS |
| Backend | Python 3.x, Flask |
| AI Engine | Groq API (LLaMA 3 8B) |
| CORS | flask-cors |

---

## 📝 Notes

- The Groq API key is embedded in `app.py` for development convenience. For production, use an environment variable: `export GROQ_API_KEY=your_key_here`
- Input validation is handled on both the frontend (Bootstrap) and backend (Flask).
- All responses end with **"Happy Farming! 🌱"**
