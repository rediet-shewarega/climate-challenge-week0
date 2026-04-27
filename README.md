# African Climate Trend Analysis — Week 0 Challenge

Exploratory analysis of historical climate data from **Ethiopia, Kenya, Sudan, Tanzania, and Nigeria** (NASA POWER, 2015–2026) in support of Ethiopia's data-driven position ahead of **COP32**.

---

## Project Structure

```
climate-challenge-week0/
├── .github/workflows/ci.yml    # GitHub Actions CI
├── .gitignore
├── requirements.txt
├── README.md
├── data/                       # ← gitignored; place raw & cleaned CSVs here
├── notebooks/
│   ├── ethiopia_eda.ipynb
│   ├── kenya_eda.ipynb
│   ├── sudan_eda.ipynb
│   ├── tanzania_eda.ipynb
│   ├── nigeria_eda.ipynb
│   └── compare_countries.ipynb
├── app/
│   ├── main.py                 # Streamlit dashboard
│   └── utils.py
├── scripts/
│   └── README.md
├── src/
└── tests/
```

---

## Reproducing the Environment

### Prerequisites
- Python 3.11+ 
- `git`

### 1. Clone the repository
```bash
git clone https://github.com/rediet-shewarega/climate-challenge-week0.git
cd climate-challenge-week0
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add data files
Download the NASA POWER CSVs (Ethiopia, Kenya, Sudan, Tanzania, Nigeria) and place them in the `data/` directory:
```
data/
├── ethiopia.csv
├── kenya.csv
├── sudan.csv
├── tanzania.csv
└── nigeria.csv
```
> **Note:** The `data/` directory is listed in `.gitignore` and must never be committed to GitHub.

### 5. Run the notebooks
```bash
jupyter notebook notebooks/
```

### 6. Launch the Streamlit dashboard
```bash
streamlit run app/main.py
```

---

## Dataset

| Column | Unit | Description |
|---|---|---|
| YEAR | – | Year of observation |
| DOY | – | Day of year (1–365/366) |
| T2M | °C | Mean daily air temperature at 2 m |
| T2M_MAX | °C | Maximum daily temperature at 2 m |
| T2M_MIN | °C | Minimum daily temperature at 2 m |
| T2M_RANGE | °C | Daily temperature range |
| PRECTOTCORR | mm/day | Bias-corrected total daily precipitation |
| RH2M | % | Relative humidity at 2 m |
| WS2M | m/s | Mean daily wind speed at 2 m |
| WS2M_MAX | m/s | Maximum daily wind speed at 2 m |
| PS | kPa | Atmospheric surface pressure |
| QV2M | g/kg | Specific humidity |

Source: [NASA POWER](https://power.larc.nasa.gov/), 2015 – March 2026.

---

## CI/CD

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push to `main` and every pull request. It installs dependencies and validates the Python environment.

---

## Team

Challenge facilitated by **10 Academy** — [#all-week0](https://10academy.slack.com)
