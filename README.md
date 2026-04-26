# Baseline — Self-Hosted Health & Fitness Tracker

A personal health and fitness tracker built to run on your own hardware.
No cloud. No subscriptions. Your data stays on your device.

![Baseline](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![Flask](https://img.shields.io/badge/flask-3.x-lightgrey)
![Pi Compatible](https://img.shields.io/badge/raspberry%20pi-B%2B%20and%20newer-red)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## What is Baseline?

Baseline is a self-hosted health and fitness tracker designed for people who want full control over their personal health data. It runs on a Raspberry Pi (even a 10-year-old Pi B+), a home server, or any machine with Python installed. All your data lives in a single JSON file on your own hardware — nothing is ever sent to a third party.

---

## Features

### Profiles
- **Netflix-style profile picker** — tap your name to enter, supports unlimited profiles
- **Optional 4-digit PIN** per profile for basic privacy between family members
- **Fully isolated data** — each profile has completely separate logs, food, workouts, and goals

### Health Metrics
- **BMI calculator** with personalized advice based on your result
- **Sleep schedule recommendations** based on age, BMI, and stress level, with bedtime options calculated to wake at the end of a 90-minute sleep cycle
- **Protein target** auto-calculated based on your goal and bodyweight
- **BMR and TDEE** calculated using the Mifflin-St Jeor equation

### Fitness
- **6 goal-based workout plans** — Fat Loss, Muscle Building, Maintenance, Cardio, Flexibility, and Athletic Performance
- Every exercise includes options for **home (bodyweight/dumbbells) or standard gym**
- Plans scale to your available days per week

### Nutrition
- **Timed meal plans** with macros scaled to your calorie target
- **Calorie tracker** with protein, carbs, and fat per entry
- **Next meal** on the dashboard updates based on current time of day

### Daily Log
- Log weight, steps, sleep, water, heart rate, HRV, SpO2, mood, workout, and notes
- **Health app import** — paste CSV or JSON from Apple Health, Fitbit, Garmin, or any export
- Weight logged in Daily Log automatically updates your profile weight

### Apple Health Integration (via Health Auto Export)
- **Automatic sync** from Apple Health via REST API webhook
- Maps 15+ metrics automatically: steps, sleep, active calories, resting heart rate, HRV, SpO2, weight, distance, flights climbed, stand hours, exercise minutes, and more
- Manual entries always take priority over auto-synced data
- **60-day rolling window** — older data is pruned automatically to keep storage lean
- Set up two automations in Health Auto Export (one for Health Metrics, one for Workouts) and your data flows in on your chosen schedule

### Workout Routes & Maps
- **Terrain map** powered by OpenTopoMap — beautiful topographic tiles with contour lines and elevation shading, completely free, no API key required
- Upload **GPX files** exported from Strava, Garmin Connect, Apple Health, or any fitness app
- Route drawn on the map with a **green start marker** and **red finish marker**
- Stats overlay: distance (miles), duration, pace per mile, and average heart rate

### History & Trends
- Charts for weight, steps, sleep, and calories over the last 30 days
- Full log history with mood ratings

### Dashboard
- At-a-glance stats: steps, calories, water, and sleep
- 14-day calendar strip showing which days have logged data
- Weight trend chart, goal progress bars, today's workout preview
- **Next meal suggestion** updates based on current time of day
- **Auto-refreshes every 15 minutes** with a sync timestamp badge

### General
- **Light and dark mode** — preference saved per device
- **Mobile-friendly** with slide-out navigation on phones
- **Export all data** as JSON anytime
- **Auto-populate** — enter your info once in Profile and it fills everywhere automatically

---

## Self-Hosting on Raspberry Pi

### Requirements
- Raspberry Pi (any model — tested on Pi B+ from 2014)
- Raspberry Pi OS (Lite recommended)
- Python 3.9+

### Quick Setup

```bash
git clone https://github.com/dzshafer/baseline.git
cd baseline/baseline
bash setup.sh
```

The setup script installs Flask, creates the data directory, and registers Baseline as a systemd service that starts automatically on every boot.

### Access

```
http://<YOUR_PI_IP>:3000
```

---

## Docker

```bash
git clone https://github.com/dzshafer/baseline.git
cd baseline/baseline
docker compose up -d
```

Update:
```bash
git pull
docker compose up -d --build
```

---

## Running Locally (Mac/PC)

```bash
pip3 install flask
python3 server.py
```

Then open http://localhost:3000

---

## Remote Access with Tailscale

For secure access from anywhere without opening router ports:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Install Tailscale on your phone and laptop, sign in with the same account, and access Baseline at `http://<TAILSCALE_IP>:3000` from anywhere in the world.

---

## Apple Health Auto-Sync Setup

1. Install **Health Auto Export - JSON+CSV** from the App Store
2. Go to **Automations → New Automation → REST API**
3. Set the URL to:
   ```
   http://<YOUR_PI_IP>:3000/api/profiles/<YOUR_PROFILE_ID>/healthautoexport
   ```
4. Settings: JSON, v2, Since Last Sync, Summarize Data ON, Time Grouping: Day
5. Create a second automation with Data Type: **Workouts**, Include Route Data ON

Find your profile ID by opening the browser console on the Baseline dashboard and typing `CURRENT_PROFILE_ID`.

---

## Updating

```bash
cd ~/baseline/baseline
git pull
sudo systemctl restart baseline
```

---

## Data Storage

All data lives in `data/baseline.json` and GPX files in `data/gpx/` — entirely on your device, never sent anywhere.

```bash
cp -r data/ data-backup/
```

---

## Useful Commands

```bash
sudo systemctl status baseline    # Check if running
sudo systemctl restart baseline   # Restart
sudo journalctl -u baseline -f    # Live logs
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profiles` | List all profiles |
| POST | `/api/profiles` | Create a profile |
| GET | `/api/profiles/:id/data` | Get all data for a profile |
| POST | `/api/profiles/:id/profile` | Save profile health data |
| POST | `/api/profiles/:id/logs` | Save a daily log entry |
| GET | `/api/profiles/:id/logs` | Get all log entries |
| POST | `/api/profiles/:id/food` | Add a food log entry |
| GET | `/api/profiles/:id/workouts` | Get all workouts |
| POST | `/api/profiles/:id/workouts` | Save a workout |
| POST | `/api/profiles/:id/gpx` | Upload a GPX file |
| GET | `/api/profiles/:id/gpx/:gpx_id` | Retrieve a GPX file |
| POST | `/api/profiles/:id/healthautoexport` | Apple Health webhook |
| GET | `/api/profiles/:id/export` | Export profile as JSON |
| GET | `/api/export` | Export all profiles |
| GET | `/api/health` | Server health check |

---

## Hardware Tested

- Raspberry Pi B+ (2014, ARMv6, 512MB RAM) ✅
- Raspberry Pi 3B ✅
- Raspberry Pi 4 ✅
- Docker on Mac/Windows/Linux ✅

---

## Roadmap

- [ ] Food search via Open Food Facts API
- [ ] Location tracking via Overland integration  
- [ ] Elevation profile chart for workout routes
- [ ] Correct webhook URL displayed in app settings

---

## AI Involvement

AI assistance was used extensively in development. All feature decisions, testing, deployment, and hardware setup were human-directed and reviewed. The codebase is fully open for inspection.

---

## License

MIT — free to use, modify, and share.
