# 📊 DataLens — CSV Analytics Dashboard

A professional full-stack web app to upload any CSV file and instantly get:
- 📈 Auto-generated charts (bar, line, doughnut, histogram)
- 🧠 Smart insights (averages, max values, missing data alerts)
- 📊 Statistical summary (mean, median, std, min, max)
- 🗃️ Searchable data table preview

---

## 🚀 Run Locally

### Step 1 — Clone or unzip the project
```bash
cd data-dashboard
```

### Step 2 — Create virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run the app
```bash
python app.py
```

### Step 5 — Open in browser
```
http://127.0.0.1:5000
```

---

## 🌐 Deploy on Render (Free)

1. Push this folder to a GitHub repo
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Click Deploy ✅

---

## 📂 Project Structure

```
data-dashboard/
├── app.py              ← Flask backend (routes + pandas logic)
├── requirements.txt    ← Python dependencies
├── Procfile            ← Render/Heroku deployment config
├── .gitignore
├── README.md
├── templates/
│   └── index.html      ← Full frontend (HTML + JS + Chart.js)
└── static/
    └── style.css       ← Dark theme styling
```

---

## 🧠 How It Works

1. User uploads a `.csv` file via drag-and-drop or file picker
2. Flask receives it → Pandas reads and analyzes it
3. Backend returns: table data, statistics, chart data, insights
4. Frontend renders everything with Chart.js

---

## 💡 Tech Stack

| Layer | Tool |
|-------|------|
| Backend | Python + Flask |
| Data Analysis | Pandas + NumPy |
| Frontend | HTML + CSS + JS |
| Charts | Chart.js v4 |
| Deployment | Render (gunicorn) |

---

Built with ❤️ as a full-stack data analytics project.
